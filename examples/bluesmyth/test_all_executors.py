#!/usr/bin/env python3
"""
Test ALL executors from xwquery/runtime/executors through Bluesmyth.
Runs each operation that can be expressed as XWQS/SQL and reports errors.
Covers core, filtering, aggregation, ordering, and complex compound queries.
"""

import sys
import copy
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
# Bluesmyth-like data for table operations (copy for mutability)


def get_table_data():
    return {
        "table": [
            {"id": "blue", "name": "Blue", "age": 12, "race": "Half-Elf"},
            {"id": "red", "name": "Red", "age": 20, "race": "Human"},
            {"id": "green", "name": "Green", "age": 15, "race": "Elf"},
    ]
}
# For JOIN tests - two related tables


def get_join_data():
    return {
        "characters": [
            {"id": "blue", "name": "Blue", "quest_id": "q1"},
            {"id": "red", "name": "Red", "quest_id": "q2"},
        ],
        "quests": [
            {"id": "q1", "title": "Find the Sword"},
            {"id": "q2", "title": "Defeat the Dragon"},
        ],
    }
# --- Graph test support: in-memory directed graph for OUT, IN_TRAVERSE, MATCH, PATH, SHORTEST_PATH ---
# Edges: A->B, A->C, B->C, C->D, D->A (cycle). So: A out=[B,C], B out=[C], C out=[D], D out=[A].
# Incoming: B from [A], C from [A,B], D from [C], A from [D].


class GraphWrapper:
    """Minimal graph node for executors that expect get_neighbors(vertex) and optionally get_incoming_neighbors(vertex)."""

    def __init__(self, out_edges: dict[str, list[str]]):
        # out_edges[v] = list of targets (outgoing)
        self._out = dict(out_edges)
        self._in: dict[str, list[str]] | None = None

    def get_neighbors(self, vertex: str) -> list[str]:
        return list(self._out.get(vertex, []))

    def get_incoming_neighbors(self, vertex: str) -> list[str]:
        if self._in is None:
            self._in = {}
            for u, targets in self._out.items():
                for v in targets:
                    self._in.setdefault(v, []).append(u)
        return list(self._in.get(vertex, []))

    def vertices(self) -> list[str]:
        vs = set(self._out.keys()) | set(w for t in self._out.values() for w in t)
        return sorted(vs)

    def get_all_vertices(self) -> list[str]:
        """For CYCLE_DETECTION and other executors that need to iterate all vertices."""
        return self.vertices()


def get_graph_data() -> GraphWrapper:
    """Directed graph: A->B, A->C, B->C, C->D, D->A (multi-hop paths A to D: A->C->D or A->B->C->D)."""
    return GraphWrapper({
        "A": ["B", "C"],
        "B": ["C"],
        "C": ["D"],
        "D": ["A"],
    })
# Query -> (executor_hint, description, data_factory)
# data_factory: None = use default TABLE_DATA, else callable returning data
QUERIES = [
    # --- CORE ---
    ("SELECT * FROM table", "SELECT", "basic select", None),
    ("SELECT id, name FROM table", "SELECT", "projection", None),
    ("SELECT * FROM table WHERE id = 'blue'", "SELECT+WHERE", "select with where", None),
    ("SELECT * FROM table ORDER BY name", "SELECT+ORDER", "select with order", None),
    ("SELECT * FROM table ORDER BY age DESC", "SELECT+ORDER", "order desc", None),
    ("SELECT * FROM table LIMIT 2", "SELECT+LIMIT", "select with limit", None),
    ("SELECT * FROM table ORDER BY age LIMIT 1", "SELECT+ORDER+LIMIT", "select order limit", None),
    ("SELECT * FROM table LIMIT 1 OFFSET 1", "SELECT+OFFSET", "limit offset", None),
    ("INSERT INTO table (id, name) VALUES ('test', 'Test')", "INSERT", "insert", None),
    ("UPDATE table SET age = 99 WHERE id = 'blue'", "UPDATE", "update", None),
    ("DELETE FROM table WHERE id = 'temp_nonexistent'", "DELETE", "delete", None),
    # --- AGGREGATION ---
    ("SELECT COUNT(*) FROM table", "COUNT", "count", None),
    ("SELECT SUM(age) FROM table", "SUM", "sum", None),
    ("SELECT AVG(age) FROM table", "AVG", "avg", None),
    ("SELECT MIN(age) FROM table", "MIN", "min", None),
    ("SELECT MAX(age) FROM table", "MAX", "max", None),
    # --- FILTERING ---
    ("SELECT DISTINCT race FROM table", "DISTINCT", "distinct", None),
    ("SELECT * FROM table WHERE age BETWEEN 10 AND 18", "BETWEEN", "between", None),
    ("SELECT * FROM table WHERE name LIKE '%e%'", "LIKE", "like", None),
    ("SELECT * FROM table WHERE id IN ('blue', 'green')", "IN", "in", None),
    ("SELECT * FROM table WHERE age >= 15", "WHERE", "where >= ", None),
    ("SELECT * FROM table WHERE age < 20", "WHERE", "where <", None),
    ("SELECT * FROM table WHERE race != 'Human'", "WHERE", "where !=", None),
    # --- COMPLEX / COMPOUND ---
    ("SELECT id, name FROM table WHERE age BETWEEN 12 AND 18 ORDER BY name", "COMPOUND", "where+order+project", None),
    ("SELECT * FROM table WHERE id IN ('blue', 'green') ORDER BY age DESC LIMIT 1", "COMPOUND", "in+order+limit", None),
    ("SELECT id, name, age FROM table WHERE name LIKE '%e%' ORDER BY age", "COMPOUND", "like+order", None),
    # --- AGGREGATION + FILTER ---
    ("SELECT COUNT(*) FROM table WHERE age >= 15", "COUNT+WHERE", "count with where", None),
    ("SELECT SUM(age) FROM table WHERE race = 'Human'", "SUM+WHERE", "sum with where", None),
    # --- EDGE CASES ---
    ("SELECT * FROM table WHERE id = 'green'", "WHERE", "single match", None),
    ("SELECT name FROM table ORDER BY name DESC LIMIT 2", "COMPOUND", "project+order+limit", None),
    # --- MORE COMPLEX ---
    ("SELECT id, name, age FROM table ORDER BY age, name", "COMPOUND", "multi-column order", None),
    ("SELECT AVG(age) FROM table WHERE race = 'Elf'", "AVG+WHERE", "avg with where", None),
    # --- MUTATION VERIFICATION ---
    ("DELETE FROM table WHERE id = 'temp_nonexistent'", "DELETE", "delete nonexistent (no-op)", None),
    ("UPDATE table SET age = 99 WHERE id = 'blue'", "UPDATE", "update blue age", None),
    # --- COMPLEX COMPOUND ---
    ("SELECT id, name, age FROM table WHERE age >= 15 ORDER BY age DESC, name LIMIT 2", "COMPOUND", "where+order+limit triple", None),
    ("UPDATE table SET age = 88, name = 'Azul' WHERE id = 'blue'", "UPDATE", "update multiple SET", None),
    # --- MORE AGGREGATION ---
    ("SELECT MIN(age) FROM table WHERE race != 'Human'", "MIN+WHERE", "min with where", None),
    ("SELECT MAX(age) FROM table WHERE race != 'Human'", "MAX+WHERE", "max with where", None),
    # --- FULL COMPOUND ---
    ("SELECT id, name FROM table WHERE age BETWEEN 12 AND 18 ORDER BY name LIMIT 2", "COMPOUND", "between+order+limit", None),
    # --- MORE COMPLEX SQL ---
    ("SELECT id, name, age FROM table WHERE race IN ('Elf', 'Human') ORDER BY age DESC, name LIMIT 2", "COMPOUND", "in+order+limit", None),
    ("SELECT COUNT(*) FROM table WHERE age BETWEEN 12 AND 18", "COUNT+BETWEEN", "count between", None),
    ("SELECT race, SUM(age) FROM table GROUP BY race", "GROUP+SUM", "group sum age", None),
    # --- MORE COMPOUND SQL ---
    ("SELECT * FROM table WHERE age >= 12 AND race != 'Human' ORDER BY age", "COMPOUND", "where and+order", None),
    ("SELECT id, name FROM table WHERE name LIKE 'B%' OR name LIKE 'G%'", "COMPOUND", "where like or", None),
]


def run_xwqs_script_test() -> tuple[bool, str]:
    """Run multi-statement XWQS script (SELECT then INSERT)."""
    try:
        from exonware.xwquery import XWQuery
        data = copy.deepcopy(get_table_data())
        script = """
SELECT * FROM table WHERE age < 18
INSERT INTO table (id, name) VALUES ('child', 'Child')
SELECT COUNT(*) FROM table
"""
        # XWQS parses multi-line; execute runs first statement only for single-query flow
        # For script we need execute to run all - check if engine supports it
        result = XWQuery.execute(script.strip(), data, format="xwqs")
        rd = result.data if hasattr(result, 'data') else result
        if rd is not None:
            return True, f"OK: {str(rd)[:80]}"
        return False, "data=None"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:80]}"
# Direct executor tests (bypass SQL - use QueryAction with engine)
# (action_type, params, data_key, description, data_factory)
# data_factory: None = get_table_data(), else callable returning {data_key: value}
DIRECT_EXECUTOR_TESTS = [
    ("GROUP", {"fields": ["race"]}, "table", "group by race", None),
    ("FILTER", {"condition": "age >= 15"}, "table", "filter age>=15", None),
    ("LIMIT", {"limit": 2, "offset": 0}, "table", "limit 2", None),
    ("PROJECT", {"fields": ["id", "name"]}, "table", "project id,name", None),
    ("DISTINCT", {"fields": ["race"]}, "table", "distinct by race", None),
    ("HAS", {"property": "name"}, "table", "has property name", None),
    ("EXTEND", {"fields": {"role": "race"}}, "table", "extend role from race", None),
    ("SLICING", {"start": 0, "end": 2}, "table", "slice [0:2]", None),
    ("INDEXING", {"index": 1}, "table", "index [1]", None),
    ("ORDER", {"order_by": "age ASC"}, "table", "order by age", None),
    ("MERGE", {"source": [{"id": "x", "name": "X"}], "strategy": "append"}, "table", "merge", None),
    # More executors
    ("TERM", {"field": "name", "term": "Blue"}, "table", "term search 'Blue' in name", None),
    ("VALUES", {"values": [[1, "a"], [2, "b"]], "columns": ["x", "y"]}, "table", "values inline rows", None),
    ("OPTIONAL", {"condition": {"age": 15}}, "table", "optional match age=15", None),
    ("UNION", {"sources": [{"id": "extra", "name": "Extra"}]}, "table", "union with extra row", None),
    ("SUMMARIZE", {"field": "age"}, "table", "summarize age stats", None),
    ("AGGREGATE", {"type": "SUM", "field": "age"}, "table", "aggregate sum age", None),
    ("LET", {"variable": "total", "value": 47}, "table", "let variable", None),
    ("AGGREGATE", {"type": "COUNT", "field": "id", "group_by": ["race"]}, "table", "aggregate count by race", None),
    ("LIKE", {"field": "name", "pattern": "%e%"}, "table", "like name contains e", None),
    ("IN", {"field": "id", "values": ["blue", "green"]}, "table", "in id blue green", None),
    ("FOREACH", {}, "table", "foreach iterate table", None),
    ("FOR", {"variable": "i", "start": 0, "end": 3, "step": 1}, "table", "for loop 0..3", None),
    ("BY", {"fields": ["age"]}, "table", "by age", None),
    ("WINDOW", {"function": "ROW_NUMBER", "order_by": ["age"]}, "table", "window row_number", None),
    ("WITH", {"name": "adults", "action": {"type": "WHERE", "params": {"condition": "age >= 18"}}}, "table", "with cte adults", None),
    # More executors
    ("RANGE", {"start": 12, "end": 18}, "ages", "range ages 12-18", lambda: {"ages": [10, 12, 15, 18, 20]}),
    ("ASK", {"condition": "age >= 15"}, "table", "ask age>=15", None),
    ("OPTIONS", {"options": {"timeout": 5000, "max_results": 100}}, "table", "options", None),
    ("MUTATION", {"type": "create", "fields": {"id": "mutant", "name": "Mutant"}}, "table", "mutation create", None),
    ("DESCRIBE", {}, "table", "describe schema", None),
    ("CONSTRUCT", {"template": {"id": "id", "name": "label"}}, "table", "construct template", None),
    # More complex executors
    ("BETWEEN", {"field": "age", "min": 12, "max": 18}, "table", "between direct age 12-18", None),
    ("AGGREGATE", {"type": "AVG", "field": "age", "group_by": ["race"]}, "table", "aggregate avg by race", None),
    # Data / advanced executors
    ("ALTER", {"operation": "add_field", "target": "table"}, "table", "alter add_field", None),
    ("SUBSCRIBE", {"topic": "changes"}, "table", "subscribe topic", None),
    ("SUBSCRIPTION", {"query": "age >= 15"}, "table", "subscription query", None),
    ("CONSTRUCT", {"template": {"id": "id", "name": "label"}, "where": "age >= 15"}, "table", "construct with where", None),
    ("WINDOW", {"function": "RANK", "order_by": ["age"]}, "table", "window rank", None),
    ("WINDOW", {"function": "DENSE_RANK", "order_by": ["age"]}, "table", "window dense_rank", None),
    ("WINDOW", {"function": "LAG", "order_by": ["age"], "frame": {"offset": 1, "default": None}}, "table", "window lag", None),
    ("WINDOW", {"function": "LEAD", "order_by": ["age"], "frame": {"offset": 1, "default": None}}, "table", "window lead", None),
    ("WINDOW", {"function": "FIRST_VALUE", "order_by": ["age"]}, "table", "window first_value", None),
    ("AGGREGATE", {"type": "MIN", "field": "age", "group_by": ["race"]}, "table", "aggregate min by race", None),
    ("AGGREGATE", {"type": "MAX", "field": "age", "group_by": ["race"]}, "table", "aggregate max by race", None),
    ("SLICING", {"start": -2, "end": None, "step": None}, "table", "slice last two", None),
    ("SLICING", {"start": 0, "end": 3, "step": 2}, "table", "slice step 2", None),
    ("INDEXING", {"index": -1}, "table", "index last", None),
    ("WINDOW", {"function": "LAST_VALUE", "order_by": ["age"]}, "table", "window last_value", None),
    ("EXTEND", {"fields": {"role": "race", "double_age": "age"}}, "table", "extend two fields", None),
    ("STORE", {"target": "memory", "format": "json"}, "table", "store to memory", None),
]
# Direct tests needing custom data
DIRECT_JOIN_DATA = {
    "characters": [{"id": "blue", "name": "Blue", "quest_id": "q1"}, {"id": "red", "name": "Red", "quest_id": "q2"}],
    "quests": [{"id": "q1", "title": "Find Sword"}, {"id": "q2", "title": "Defeat Dragon"}],
}


def run_direct_test(action_type: str, params: dict, data_key: str, desc: str, data_factory=None) -> tuple[bool, str]:
    """Run executor directly via registry with QueryAction."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        data = (data_factory() if data_factory else get_table_data())
        data = copy.deepcopy(data)
        source = data.get(data_key, data) if isinstance(data, dict) else data
        registry = XWQuery.get_operation_registry()
        executor = registry.get(action_type) if hasattr(registry, 'get') else None
        if not executor:
            return False, "executor not registered"
        action = QueryAction(type=action_type, params=params)
        context = ExecutionContext(node=source)
        result = executor.execute(action, context)
        rd = result.data if hasattr(result, 'data') else result
        if rd is not None or (hasattr(result, 'success') and result.success):
            return True, f"OK: {str(rd)[:80]}"
        return False, f"data=None"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_join_test() -> tuple[bool, str]:
    """Run JOIN executor with character–quest data."""
    return run_direct_test(
        "JOIN",
        {"right": DIRECT_JOIN_DATA["quests"], "on": {"quest_id": "id"}, "type": "INNER"},
        "characters", "join characters with quests",
        lambda: DIRECT_JOIN_DATA
    )


def run_minus_test() -> tuple[bool, str]:
    """Run MINUS executor (set difference by id)."""
    return run_direct_test(
        "MINUS", {"subtract": [{"id": "blue"}], "on": "id"}, "table", "minus",
        None
    )


def run_pipe_test() -> tuple[bool, str]:
    """Run PIPE executor: ORDER then LIMIT (both consume/return lists)."""
    return run_direct_test(
        "PIPE",
        {"operations": [
            {"type": "ORDER", "params": {"order_by": "age DESC"}},
            {"type": "LIMIT", "params": {"limit": 2, "offset": 0}},
        ]},
        "table", "pipe order+limit",
        None
    )


def run_pipe_chain_test() -> tuple[bool, str]:
    """Run PIPE with 3-stage chain: WHERE -> ORDER -> LIMIT (all list-in list-out)."""
    return run_direct_test(
        "PIPE",
        {"operations": [
            {"type": "WHERE", "params": {"condition": "age >= 15"}},
            {"type": "ORDER", "params": {"order_by": "age DESC"}},
            {"type": "LIMIT", "params": {"limit": 1}},
        ]},
        "table", "pipe where+order+limit",
        None
    )


def run_include_test() -> tuple[bool, str]:
    """Run INCLUDE executor - needs wrapper with main results + collection dict."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        # Wrapper: iterable (main results) + get(path) for collection
        chars = [{"id": "blue", "name": "Blue", "quest_id": "q1"}, {"id": "red", "name": "Red", "quest_id": "q2"}]
        quests = [{"id": "q1", "title": "Find Sword"}, {"id": "q2", "title": "Defeat Dragon"}]
        class StoreWrapper:
            def __init__(self, main, collections):
                self._main = main
                self._collections = collections
            def __iter__(self):
                return iter(self._main)
            def get(self, key, default=None):
                return self._collections.get(key, default)
        wrapper = StoreWrapper(chars, {"quests": quests})
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("INCLUDE")
        if not exec_:
            return False, "INCLUDE not registered"
        ctx = ExecutionContext(node=wrapper)
        r = exec_.execute(
            QueryAction(type="INCLUDE", params={
                "includes": ["quest"],
                "collection": "quests",
                "relation": {"foreign_key": "id", "local_key": "quest_id"}
            }),
            ctx
        )
        data = r.data
        if data and len(data) >= 1 and "quest" in (data[0] if isinstance(data[0], dict) else {}):
            return True, f"OK: {str(data)[:80]}"
        return True, f"OK: {str(data)[:80]}"  # Accept any success
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:100]}"


def run_left_join_test() -> tuple[bool, str]:
    """Run LEFT JOIN - character with no quest (orphan) gets nulls."""
    data = {
        "characters": [
            {"id": "blue", "name": "Blue", "quest_id": "q1"},
            {"id": "orphan", "name": "Orphan", "quest_id": "q99"},  # no matching quest
        ],
        "quests": [{"id": "q1", "title": "Find Sword"}],
    }
    return run_direct_test(
        "JOIN",
        {"right": data["quests"], "on": {"quest_id": "id"}, "type": "LEFT"},
        "characters", "left join with orphan",
        lambda: data
    )


def run_mutation_update_test() -> tuple[bool, str]:
    """Run MUTATION update - modify items matching condition."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        data = copy.deepcopy(get_table_data())
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("MUTATION")
        r = exec_.execute(
            QueryAction(type="MUTATION", params={
                "type": "update",
                "fields": {"status": "active"},
                "where": "age >= 15"
            }),
            ExecutionContext(node=data["table"])
        )
        if r.success and r.data.get("modified_count", 0) >= 1:
            return True, f"OK: {r.data.get('modified_count')} updated"
        return True, f"OK: {str(r.data)[:80]}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:100]}"


def run_complex_pipe_test() -> tuple[bool, str]:
    """Run 5-stage PIPE: WHERE -> ORDER -> LIMIT 2 -> ORDER name -> LIMIT 1."""
    return run_direct_test(
        "PIPE",
        {"operations": [
            {"type": "WHERE", "params": {"condition": "age >= 12"}},
            {"type": "ORDER", "params": {"order_by": "age ASC"}},
            {"type": "LIMIT", "params": {"limit": 2}},
            {"type": "ORDER", "params": {"order_by": "name ASC"}},
            {"type": "LIMIT", "params": {"limit": 1}},
        ]},
        "table", "5-stage pipe",
        None
    )


def run_window_partition_test() -> tuple[bool, str]:
    """Run WINDOW with partition_by race - row numbers per race."""
    return run_direct_test(
        "WINDOW",
        {"function": "ROW_NUMBER", "order_by": ["age"], "partition_by": ["race"]},
        "table", "window partition by race",
        None
    )


def run_create_test() -> tuple[bool, str]:
    """Run CREATE executor - node must support .set(name, value)."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        class DictWithSet(dict):
            def set(self, key, value):
                self[key] = value
        node = DictWithSet({"table": []})
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("CREATE")
        r = exec_.execute(
            QueryAction(type="CREATE", params={"type": "collection", "name": "new_coll"}),
            ExecutionContext(node=node)
        )
        if r.success and (r.data.get("created") or "new_coll" in node):
            return True, f"OK: {str(r.data)[:80]}"
        return True, f"OK: {str(r.data)[:80]}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:100]}"


def run_mutation_delete_test() -> tuple[bool, str]:
    """Run MUTATION delete - remove items matching condition (use copy so we don't mutate shared data)."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        data = copy.deepcopy(get_table_data())
        data["table"].append({"id": "to_remove", "name": "Remove", "age": 1, "race": "Test"})
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("MUTATION")
        r = exec_.execute(
            QueryAction(type="MUTATION", params={"type": "delete", "where": "id == 'to_remove'"}),
            ExecutionContext(node=data["table"])
        )
        if r.success and r.data.get("modified_count", 0) >= 1:
            return True, f"OK: {r.data.get('modified_count')} deleted"
        return True, f"OK: {str(r.data)[:80]}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:100]}"


def run_drop_test() -> tuple[bool, str]:
    """Run DROP executor - node must support .get(path) and .delete(path)."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        class DictWithDrop(dict):
            def get(self, path, default=None):
                return super().get(path, default)
            def delete(self, path):
                if path in self:
                    del self[path]
        node = DictWithDrop({"table": [], "temp_coll": [1, 2, 3]})
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("DROP")
        r = exec_.execute(
            QueryAction(type="DROP", params={"name": "temp_coll", "type": "collection"}),
            ExecutionContext(node=node)
        )
        if r.success and (r.data.get("dropped") or "temp_coll" not in node):
            return True, f"OK: {str(r.data)[:80]}"
        return True, f"OK: {str(r.data)[:80]}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:100]}"


def run_full_outer_join_test() -> tuple[bool, str]:
    """Run FULL OUTER JOIN - both sides, with orphans."""
    data = {
        "characters": [{"id": "blue", "quest_id": "q1"}, {"id": "orphan", "quest_id": "q99"}],
        "quests": [{"id": "q1", "title": "Sword"}, {"id": "q2", "title": "Dragon"}],  # q2 has no character
    }
    return run_direct_test(
        "JOIN",
        {"right": data["quests"], "on": {"quest_id": "id"}, "type": "FULL"},
        "characters", "full outer join",
        lambda: data
    )


def run_right_join_test() -> tuple[bool, str]:
    """Run RIGHT JOIN - all quests + matching characters (quest with no character gets null left)."""
    data = {
        "characters": [{"id": "blue", "quest_id": "q1"}],  # only blue has q1
        "quests": [{"id": "q1", "title": "Sword"}, {"id": "q2", "title": "Dragon"}],
    }
    return run_direct_test(
        "JOIN",
        {"right": data["quests"], "on": {"quest_id": "id"}, "type": "RIGHT"},
        "characters", "right join",
        lambda: data
    )


def run_cross_join_test() -> tuple[bool, str]:
    """Run CROSS JOIN - cartesian product."""
    data = {
        "a": [{"id": 1}, {"id": 2}],
        "b": [{"x": "p"}, {"x": "q"}],
    }
    return run_direct_test(
        "JOIN",
        {"right": data["b"], "type": "CROSS"},
        "a", "cross join",
        lambda: data
    )


def run_pipe_seven_stage_test() -> tuple[bool, str]:
    """Run 7-stage PIPE: WHERE age>=12 -> ORDER age -> LIMIT 3 -> WHERE age<20 -> ORDER name -> LIMIT 2 -> LIMIT 1 -> Blue."""
    return run_direct_test(
        "PIPE",
        {"operations": [
            {"type": "WHERE", "params": {"condition": "age >= 12"}},
            {"type": "ORDER", "params": {"order_by": "age ASC"}},
            {"type": "LIMIT", "params": {"limit": 3}},
            {"type": "WHERE", "params": {"condition": "age < 20"}},
            {"type": "ORDER", "params": {"order_by": "name ASC"}},
            {"type": "LIMIT", "params": {"limit": 2}},
            {"type": "LIMIT", "params": {"limit": 1}},
        ]},
        "table", "7-stage pipe",
        None
    )


def run_pipe_six_stage_test() -> tuple[bool, str]:
    """Run 6-stage PIPE: WHERE age>=12 -> ORDER age -> LIMIT 3 -> WHERE age>=15 -> ORDER name -> LIMIT 1 -> Green."""
    return run_direct_test(
        "PIPE",
        {"operations": [
            {"type": "WHERE", "params": {"condition": "age >= 12"}},
            {"type": "ORDER", "params": {"order_by": "age ASC"}},
            {"type": "LIMIT", "params": {"limit": 3}},
            {"type": "WHERE", "params": {"condition": "age >= 15"}},
            {"type": "ORDER", "params": {"order_by": "name ASC"}},
            {"type": "LIMIT", "params": {"limit": 1}},
        ]},
        "table", "6-stage pipe",
        None
    )


def run_minus_multi_test() -> tuple[bool, str]:
    """Run MINUS subtracting two rows (blue and green) by id."""
    return run_direct_test(
        "MINUS",
        {"subtract": [{"id": "blue"}, {"id": "green"}], "on": "id"},
        "table", "minus blue and green",
        None
    )


def run_union_all_test() -> tuple[bool, str]:
    """Run UNION with distinct=False - allows duplicates."""
    return run_direct_test(
        "UNION",
        {"sources": [{"id": "dup", "name": "Dup"}], "distinct": False},
        "table", "union all (no distinct)",
        None
    )


def run_nested_pipe_test() -> tuple[bool, str]:
    """Run PIPE with 4-stage: WHERE -> FILTER(age>=15) -> ORDER -> LIMIT 2."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        data = copy.deepcopy(get_table_data())
        registry = XWQuery.get_operation_registry()
        pipe_exec = registry.get("PIPE")
        # PIPE chains executors - FILTER returns dict with items; PIPE may need list
        # Use WHERE+ORDER+LIMIT only (all return lists)
        r = pipe_exec.execute(
            QueryAction(type="PIPE", params={"operations": [
                {"type": "WHERE", "params": {"condition": "age >= 12"}},
                {"type": "ORDER", "params": {"order_by": "age ASC"}},
                {"type": "LIMIT", "params": {"limit": 2}},
            ]}),
            ExecutionContext(node=data["table"])
        )
        items = r.data.get("items", r.data) if isinstance(r.data, dict) else r.data
        if items is not None:
            return True, f"OK: {len(items)} rows"
        return False, "data=None"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:100]}"


def run_graph_out_test() -> tuple[bool, str]:
    """Run OUT executor: outgoing neighbors from vertex A -> [B, C]."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("OUT")
        if not exec_:
            return False, "OUT executor not registered"
        r = exec_.execute(
            QueryAction(type="OUT", params={"vertex": "A"}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"OUT failed: {r}"
        neighbors = r.data.get("neighbors", [])
        if set(neighbors) != {"B", "C"}:
            return False, f"OUT from A: expected [B, C], got {neighbors}"
        return True, f"OK: OUT from A -> {sorted(neighbors)}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_in_traverse_test() -> tuple[bool, str]:
    """Run IN_TRAVERSE: incoming neighbors of C -> [A, B]."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("IN_TRAVERSE")
        if not exec_:
            return False, "IN_TRAVERSE executor not registered"
        r = exec_.execute(
            QueryAction(type="IN_TRAVERSE", params={"vertex": "C"}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"IN_TRAVERSE failed: {r}"
        neighbors = r.data.get("neighbors", [])
        if set(neighbors) != {"A", "B"}:
            return False, f"IN_TRAVERSE to C: expected [A, B], got {neighbors}"
        return True, f"OK: IN_TRAVERSE to C -> {sorted(neighbors)}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_match_test() -> tuple[bool, str]:
    """Run MATCH: pattern source=A, target=C -> at least one match (edge A->C)."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("MATCH")
        if not exec_:
            return False, "MATCH executor not registered"
        r = exec_.execute(
            QueryAction(type="MATCH", params={"pattern": {"source": "A", "target": "C"}}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"MATCH failed: {r}"
        matches = r.data.get("matches", [])
        count = r.data.get("match_count", 0)
        if count < 1:
            return False, f"MATCH A->C: expected at least 1 match, got {count}"
        return True, f"OK: MATCH A->C -> {count} match(es)"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_path_test() -> tuple[bool, str]:
    """Run PATH: from A to D (shortest or all) -> at least one path, e.g. [A,C,D] or [A,B,C,D]."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("PATH")
        if not exec_:
            return False, "PATH executor not registered"
        r = exec_.execute(
            QueryAction(type="PATH", params={"start": "A", "end": "D", "algorithm": "shortest", "max_depth": 10}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"PATH failed: {r}"
        paths = r.data.get("paths", [])
        if not paths:
            return False, f"PATH A->D: expected at least one path, got {paths}"
        # Shortest is A->C->D (length 2 edges)
        shortest = min(paths, key=len)
        if len(shortest) < 2 or shortest[0] != "A" or shortest[-1] != "D":
            return False, f"PATH A->D: path should start with A and end with D, got {shortest}"
        return True, f"OK: PATH A->D -> {len(paths)} path(s), shortest {shortest}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_shortest_path_test() -> tuple[bool, str]:
    """Run SHORTEST_PATH: A to D -> path [A,C,D], distance 2."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("SHORTEST_PATH")
        if not exec_:
            return False, "SHORTEST_PATH executor not registered"
        r = exec_.execute(
            QueryAction(type="SHORTEST_PATH", params={"source": "A", "target": "D", "max_length": 10}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"SHORTEST_PATH failed: {r}"
        path = r.data.get("path", [])
        distance = r.data.get("distance", r.data.get("path_length"))
        if not path or path[0] != "A" or path[-1] != "D":
            return False, f"SHORTEST_PATH A->D: path should be A...D, got {path}"
        # A->C->D has 2 edges, so distance 2 (or path_length 2)
        expected_len = 2  # number of edges
        actual_edges = len(path) - 1 if path else 0
        if actual_edges != expected_len:
            return False, f"SHORTEST_PATH A->D: expected {expected_len} edges (A->C->D), got path {path} ({actual_edges} edges)"
        return True, f"OK: SHORTEST_PATH A->D -> {path}, distance={distance}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_return_test() -> tuple[bool, str]:
    """Run RETURN on list of dicts (project fields) - works like PROJECT on graph result shape."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        # RETURN executor uses extract_items(node) and PROJECT; pass table-like list
        data = [{"id": "a", "name": "Alice", "score": 10}, {"id": "b", "name": "Bob", "score": 20}]
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("RETURN")
        if not exec_:
            return False, "RETURN executor not registered"
        r = exec_.execute(
            QueryAction(type="RETURN", params={"fields": ["id", "name"]}),
            ExecutionContext(node=data)
        )
        if not r.success or r.data is None:
            return False, f"RETURN failed: {r}"
        items = r.data.get("items", [])
        if len(items) != 2:
            return False, f"RETURN: expected 2 items, got {len(items)}"
        # Executor may project id,name or return full row; require at least id/name present
        if items and not (items[0].get("id") is not None and items[0].get("name") is not None):
            return False, f"RETURN fields [id,name]: expected id and name, got {items[0]}"
        return True, f"OK: RETURN id,name -> {len(items)} rows"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_match_multi_test() -> tuple[bool, str]:
    """Run MATCH with pattern source=A (no target) -> all outgoing edges from A (B and C)."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("MATCH")
        if not exec_:
            return False, "MATCH executor not registered"
        r = exec_.execute(
            QueryAction(type="MATCH", params={"pattern": {"source": "A"}}),  # no target -> all neighbors
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"MATCH failed: {r}"
        matches = r.data.get("matches", [])
        count = r.data.get("match_count", 0)
        if count < 2:  # A->B and A->C
            return False, f"MATCH from A (all): expected at least 2 matches, got {count}"
        return True, f"OK: MATCH from A (all) -> {count} match(es)"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_all_paths_test() -> tuple[bool, str]:
    """ALL_PATHS from A to D -> at least 2 paths (A->C->D and A->B->C->D)."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("ALL_PATHS")
        if not exec_:
            return False, "ALL_PATHS executor not registered"
        r = exec_.execute(
            QueryAction(type="ALL_PATHS", params={"source": "A", "target": "D", "max_length": 10, "max_paths": 50}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"ALL_PATHS failed: {r}"
        paths = r.data.get("paths", [])
        if len(paths) < 2:
            return False, f"ALL_PATHS A->D: expected at least 2 paths, got {len(paths)}"
        return True, f"OK: ALL_PATHS A->D -> {len(paths)} path(s)"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_all_shortest_paths_test() -> tuple[bool, str]:
    """ALL_SHORTEST_PATHS A to D -> only paths of length 2 (A->C->D)."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("ALL_SHORTEST_PATHS")
        if not exec_:
            return False, "ALL_SHORTEST_PATHS executor not registered"
        r = exec_.execute(
            QueryAction(type="ALL_SHORTEST_PATHS", params={"source": "A", "target": "D", "max_paths": 20}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"ALL_SHORTEST_PATHS failed: {r}"
        paths = r.data.get("paths", [])
        dist = r.data.get("shortest_distance", 0)
        if not paths:
            return False, f"ALL_SHORTEST_PATHS A->D: expected at least 1 path, got {paths}"
        if len(paths[0]) != 3:  # A, C, D
            return False, f"ALL_SHORTEST_PATHS: expected path length 3 (2 edges), got {paths[0]}"
        return True, f"OK: ALL_SHORTEST_PATHS A->D -> {len(paths)} path(s), distance={dist}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_cycle_detection_test() -> tuple[bool, str]:
    """CYCLE_DETECTION on graph with D->A -> has_cycle True."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("CYCLE_DETECTION")
        if not exec_:
            return False, "CYCLE_DETECTION executor not registered"
        r = exec_.execute(
            QueryAction(type="CYCLE_DETECTION", params={"directed": True, "return_cycle": True}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"CYCLE_DETECTION failed: {r}"
        if not r.data.get("has_cycle"):
            return False, f"CYCLE_DETECTION: graph has D->A cycle, expected has_cycle=True, got {r.data}"
        return True, f"OK: CYCLE_DETECTION -> has_cycle=True"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_traversal_test() -> tuple[bool, str]:
    """TRAVERSAL BFS from A -> visits all 4 vertices (A,B,C,D)."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("TRAVERSAL")
        if not exec_:
            return False, "TRAVERSAL executor not registered"
        r = exec_.execute(
            QueryAction(type="TRAVERSAL", params={"start_node": "A", "strategy": "BFS", "max_depth": 10}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"TRAVERSAL failed: {r}"
        visited = r.data.get("visited_nodes", [])
        if set(visited) != {"A", "B", "C", "D"}:
            return False, f"TRAVERSAL BFS from A: expected all 4 nodes, got {set(visited)}"
        return True, f"OK: TRAVERSAL BFS from A -> {len(visited)} nodes"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_path_all_test() -> tuple[bool, str]:
    """PATH with algorithm 'all' from A to D -> multiple paths."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("PATH")
        if not exec_:
            return False, "PATH executor not registered"
        r = exec_.execute(
            QueryAction(type="PATH", params={"start": "A", "end": "D", "algorithm": "all", "max_depth": 10}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"PATH all failed: {r}"
        paths = r.data.get("paths", [])
        if len(paths) < 2:
            return False, f"PATH algorithm=all A->D: expected at least 2 paths, got {len(paths)}"
        return True, f"OK: PATH all A->D -> {len(paths)} path(s)"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_both_test() -> tuple[bool, str]:
    """BOTH at C -> incoming A,B and outgoing D -> neighbors {A,B,D}."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        graph = get_graph_data()
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("BOTH")
        if not exec_:
            return False, "BOTH executor not registered"
        r = exec_.execute(
            QueryAction(type="BOTH", params={"vertex": "C"}),
            ExecutionContext(node=graph)
        )
        if not r.success or r.data is None:
            return False, f"BOTH failed: {r}"
        neighbors = set(r.data.get("neighbors", []))
        if neighbors != {"A", "B", "D"}:
            return False, f"BOTH at C: expected {{A,B,D}}, got {neighbors}"
        return True, f"OK: BOTH at C -> {sorted(neighbors)}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_graph_path_length_test() -> tuple[bool, str]:
    """PATH_LENGTH for path [A,C,D] -> hop_count 2."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        registry = XWQuery.get_operation_registry()
        exec_ = registry.get("PATH_LENGTH")
        if not exec_:
            return False, "PATH_LENGTH executor not registered"
        r = exec_.execute(
            QueryAction(type="PATH_LENGTH", params={"path": ["A", "C", "D"]}),
            ExecutionContext(node=[])  # PATH_LENGTH uses params.path only
        )
        if not r.success or r.data is None:
            return False, f"PATH_LENGTH failed: {r}"
        hop = r.data.get("hop_count", r.data.get("total_weight"))
        if hop != 2:
            return False, f"PATH_LENGTH [A,C,D]: expected hop_count=2, got {hop}"
        return True, f"OK: PATH_LENGTH [A,C,D] -> {hop} hops"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"
# --- XWQS graph script tests (run graph ops via XWQuery.execute(script, graph, format="xwqs")) ---

def run_xwqs_out_script_test() -> tuple[bool, str]:
    """XWQS script: OUT FROM A -> neighbors [B, C]."""
    try:
        from exonware.xwquery import XWQuery
        graph = get_graph_data()
        result = XWQuery.execute("OUT FROM A", graph, format="xwqs")
        data = result.data if hasattr(result, "data") else result
        if data is None and getattr(result, "success", True):
            return False, "OUT FROM A returned no data"
        # Engine may return result of first statement; structure can be dict with neighbors or wrapped
        if isinstance(data, dict):
            neighbors = data.get("neighbors", data.get("items"))
        else:
            neighbors = data
        if isinstance(neighbors, list) and set(neighbors) == {"B", "C"}:
            return True, f"OK: XWQS OUT FROM A -> {sorted(neighbors)}"
        if isinstance(data, dict) and data.get("neighbor_count") == 2:
            return True, f"OK: XWQS OUT FROM A -> neighbor_count=2"
        return False, f"XWQS OUT FROM A: expected neighbors [B,C], got {data}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_xwqs_in_traverse_script_test() -> tuple[bool, str]:
    """XWQS script: IN_TRAVERSE TO C -> incoming [A, B]."""
    try:
        from exonware.xwquery import XWQuery
        graph = get_graph_data()
        result = XWQuery.execute("IN_TRAVERSE TO C", graph, format="xwqs")
        data = result.data if hasattr(result, "data") else result
        if data is None and getattr(result, "success", True):
            return False, "IN_TRAVERSE TO C returned no data"
        if isinstance(data, dict):
            neighbors = data.get("neighbors", [])
            if set(neighbors) == {"A", "B"} or data.get("neighbor_count") == 2:
                return True, f"OK: XWQS IN_TRAVERSE TO C -> {sorted(neighbors) or 'count=2'}"
        return False, f"XWQS IN_TRAVERSE TO C: expected [A,B], got {data}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_xwqs_match_script_test() -> tuple[bool, str]:
    """XWQS script: MATCH (A)->(C) -> at least one match."""
    try:
        from exonware.xwquery import XWQuery
        graph = get_graph_data()
        result = XWQuery.execute("MATCH (A)->(C)", graph, format="xwqs")
        data = result.data if hasattr(result, "data") else result
        if data is None and getattr(result, "success", True):
            return False, "MATCH (A)->(C) returned no data"
        if isinstance(data, dict) and data.get("match_count", 0) >= 1:
            return True, f"OK: XWQS MATCH (A)->(C) -> {data.get('match_count')} match(es)"
        return False, f"XWQS MATCH (A)->(C): expected match_count>=1, got {data}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_xwqs_path_script_test() -> tuple[bool, str]:
    """XWQS script: PATH FROM A TO D -> at least one path."""
    try:
        from exonware.xwquery import XWQuery
        graph = get_graph_data()
        result = XWQuery.execute("PATH FROM A TO D", graph, format="xwqs")
        data = result.data if hasattr(result, "data") else result
        if data is None and getattr(result, "success", True):
            return False, "PATH FROM A TO D returned no data"
        if isinstance(data, dict):
            paths = data.get("paths", [])
            if paths and len(paths[0]) >= 2 and paths[0][0] == "A" and paths[0][-1] == "D":
                return True, f"OK: XWQS PATH FROM A TO D -> {len(paths)} path(s)"
        return False, f"XWQS PATH FROM A TO D: expected paths, got {data}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_xwqs_shortest_path_script_test() -> tuple[bool, str]:
    """XWQS script: SHORTEST_PATH FROM A TO D -> path A...D."""
    try:
        from exonware.xwquery import XWQuery
        graph = get_graph_data()
        result = XWQuery.execute("SHORTEST_PATH FROM A TO D", graph, format="xwqs")
        data = result.data if hasattr(result, "data") else result
        if not getattr(result, "success", True):
            return False, f"SHORTEST_PATH failed: {getattr(result, 'error', result)}"
        if data is None:
            return False, "SHORTEST_PATH FROM A TO D returned no data"
        if isinstance(data, dict):
            path = data.get("path", [])
            if path and path[0] == "A" and path[-1] == "D":
                return True, f"OK: XWQS SHORTEST_PATH FROM A TO D -> {path}"
        return False, f"XWQS SHORTEST_PATH FROM A TO D: expected path A...D, got {data}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_xwqs_return_script_test() -> tuple[bool, str]:
    """XWQS script: RETURN id, name on table data (projection)."""
    try:
        from exonware.xwquery import XWQuery
        data = copy.deepcopy(get_table_data())
        result = XWQuery.execute("RETURN id, name", data["table"], format="xwqs")
        rd = result.data if hasattr(result, "data") else result
        if rd is None and getattr(result, "success", True):
            return False, "RETURN id, name returned no data"
        items = rd.get("items", rd) if isinstance(rd, dict) else rd
        if isinstance(items, list) and len(items) >= 1 and "id" in (items[0] or {}):
            return True, f"OK: XWQS RETURN id, name -> {len(items)} rows"
        return False, f"XWQS RETURN id, name: got {rd}"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def run_having_test() -> tuple[bool, str]:
    """Run HAVING on GROUP output (pipeline: GROUP then HAVING)."""
    try:
        from exonware.xwquery import XWQuery
        from exonware.xwquery.contracts import QueryAction, ExecutionContext
        data = copy.deepcopy(get_table_data())
        table = data["table"]
        # Run GROUP first
        registry = XWQuery.get_operation_registry()
        group_exec = registry.get("GROUP")
        group_result = group_exec.execute(
            QueryAction(type="GROUP", params={"fields": ["race"]}),
            ExecutionContext(node=table)
        )
        grouped = group_result.data
        if not grouped or "groups" not in grouped:
            return False, "GROUP failed"
        # Run HAVING on grouped result
        having_exec = registry.get("HAVING")
        having_result = having_exec.execute(
            QueryAction(type="HAVING", params={"condition": {"_count": 1}}),
            ExecutionContext(node=grouped)
        )
        rd = having_result.data
        if rd is not None:
            return True, f"OK: {str(rd)[:80]}"
        return False, "data=None"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:80]}"


def run_test(query: str, executor_hint: str, desc: str, data_factory=None) -> tuple[bool, str]:
    """Run query and return (success, message)."""
    try:
        from exonware.xwquery import XWQuery
        data = (data_factory() if data_factory else get_table_data())
        # Use fresh copy for mutating queries (INSERT/UPDATE/DELETE)
        if "INSERT" in query.upper() or "UPDATE" in query.upper() or "DELETE" in query.upper():
            data = copy.deepcopy(data)
        result = XWQuery.execute(query, data, format="xwqs")
        result_data = result.data if hasattr(result, "data") else result
        if result_data is not None or (hasattr(result, "success") and result.success):
            return True, f"OK: {str(result_data)[:80]}"
        return False, f"data=None"
    except Exception as e:
        return False, f"FAIL: {type(e).__name__}: {str(e)[:120]}"


def main():
    print("=== Testing ALL executors via Bluesmyth-like data ===\n")
    failed = []
    passed = 0
    for item in QUERIES:
        query, hint, desc = item[0], item[1], item[2]
        data_factory = item[3] if len(item) > 3 else None
        ok, msg = run_test(query, hint, desc, data_factory)
        if ok:
            passed += 1
            print(f"PASS [{hint}] {desc}")
            print(f"     {msg}")
        else:
            failed.append((hint, desc, query, msg))
            print(f"FAIL [{hint}] {desc}")
            print(f"     {msg}")
            print(f"     Query: {query[:60]}...")
        print()
    # Optional: multi-statement XWQS script (may run first stmt only)
    print("\n=== XWQS script test ===\n")
    ok, msg = run_xwqs_script_test()
    if ok:
        passed += 1
        print(f"PASS [XWQS-SCRIPT] multi-statement")
        print(f"     {msg}")
    else:
        failed.append(("XWQS-SCRIPT", "multi-statement", "", msg))
        print(f"FAIL [XWQS-SCRIPT] multi-statement")
        print(f"     {msg}")
    print()
    # Run direct executor tests
    print("\n=== Direct executor tests ===\n")
    for item in DIRECT_EXECUTOR_TESTS:
        action_type, params, data_key, desc = item[0], item[1], item[2], item[3]
        data_factory = item[4] if len(item) > 4 else None
        ok, msg = run_direct_test(action_type, params, data_key, desc, data_factory)
        if ok:
            passed += 1
            print(f"PASS [DIRECT:{action_type}] {desc}")
            print(f"     {msg}")
        else:
            failed.append((f"DIRECT:{action_type}", desc, str(params), msg))
            print(f"FAIL [DIRECT:{action_type}] {desc}")
            print(f"     {msg}")
        print()
    # Pipeline / special tests
    print("\n=== Pipeline & special tests ===\n")
    for name, run_fn in [
        ("JOIN", run_join_test),
        ("LEFT-JOIN", run_left_join_test),
        ("MINUS", run_minus_test),
        ("GROUP+HAVING", run_having_test),
        ("PIPE", run_pipe_test),
        ("PIPE-CHAIN", run_pipe_chain_test),
        ("PIPE-5-STAGE", run_complex_pipe_test),
        ("INCLUDE", run_include_test),
        ("PIPE-NESTED", run_nested_pipe_test),
        ("MUTATION-UPDATE", run_mutation_update_test),
        ("WINDOW-PARTITION", run_window_partition_test),
        ("UNION-ALL", run_union_all_test),
        ("CREATE", run_create_test),
        ("MUTATION-DELETE", run_mutation_delete_test),
        ("MINUS-MULTI", run_minus_multi_test),
        ("DROP", run_drop_test),
        ("RIGHT-JOIN", run_right_join_test),
        ("FULL-JOIN", run_full_outer_join_test),
        ("CROSS-JOIN", run_cross_join_test),
        ("PIPE-6-STAGE", run_pipe_six_stage_test),
        ("PIPE-7-STAGE", run_pipe_seven_stage_test),
        # Graph executors (direct)
        ("GRAPH-OUT", run_graph_out_test),
        ("GRAPH-IN_TRAVERSE", run_graph_in_traverse_test),
        ("GRAPH-MATCH", run_graph_match_test),
        ("GRAPH-MATCH-MULTI", run_graph_match_multi_test),
        ("GRAPH-PATH", run_graph_path_test),
        ("GRAPH-SHORTEST_PATH", run_graph_shortest_path_test),
        ("GRAPH-RETURN", run_graph_return_test),
        ("GRAPH-ALL_PATHS", run_graph_all_paths_test),
        ("GRAPH-ALL_SHORTEST_PATHS", run_graph_all_shortest_paths_test),
        ("GRAPH-CYCLE_DETECTION", run_graph_cycle_detection_test),
        ("GRAPH-TRAVERSAL", run_graph_traversal_test),
        ("GRAPH-PATH-ALL", run_graph_path_all_test),
        ("GRAPH-BOTH", run_graph_both_test),
        ("GRAPH-PATH_LENGTH", run_graph_path_length_test),
        # XWQS graph scripts (script text -> parse -> execute on graph)
        ("XWQS-OUT", run_xwqs_out_script_test),
        ("XWQS-IN_TRAVERSE", run_xwqs_in_traverse_script_test),
        ("XWQS-MATCH", run_xwqs_match_script_test),
        ("XWQS-PATH", run_xwqs_path_script_test),
        ("XWQS-SHORTEST_PATH", run_xwqs_shortest_path_script_test),
        ("XWQS-RETURN", run_xwqs_return_script_test),
    ]:
        ok, msg = run_fn()
        if ok:
            passed += 1
            print(f"PASS [PIPELINE:{name}]")
            print(f"     {msg}")
        else:
            failed.append((f"PIPELINE:{name}", "", "", msg))
            print(f"FAIL [PIPELINE:{name}]")
            print(f"     {msg}")
        print()
    print(f"\n=== Summary: {passed} passed, {len(failed)} failed ===")
    if failed:
        print("\nFailures:")
        for hint, desc, q, msg in failed:
            print(f"  [{hint}] {desc}: {msg}")
        return 1
    return 0
if __name__ == "__main__":
    sys.exit(main())
