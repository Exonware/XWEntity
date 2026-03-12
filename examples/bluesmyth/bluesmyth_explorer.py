#!/usr/bin/env python3
"""
Bluesmyth Lore Explorer
======================
CLI tool to browse the Blue's Myth world. Use entity IDs or names to look up
characters, locations, quests, contracts, and more.
Interactive mode (no args): runs a loop; type 'exit' to quit.
One-shot mode (with args): e.g. python bluesmyth_explorer.py who blue
Usage:
  python bluesmyth_explorer.py
  python bluesmyth_explorer.py who blue
  python bluesmyth_explorer.py where "Cave of Spilled Crystals"
  python bluesmyth_explorer.py quests --status active
  python bluesmyth_explorer.py contracts
  python bluesmyth_explorer.py world
  python bluesmyth_explorer.py list character
  python bluesmyth_explorer.py action character blue summary
  python bluesmyth_explorer.py action world . describe_world
  python bluesmyth_explorer.py exit
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Callable
# Run from bluesmyth directory so local import works
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from bluesmyth_entities import (
    Character,
    Contract,
    Dungeon,
    invalidate_bluesmyth_cache,
    Item,
    Location,
    Monster,
    Quest,
    Settlement,
    Tower,
    World,
)


def _find_character(name_or_id: str) -> Character | None:
    """Find character by id or name (case-insensitive)."""
    key = name_or_id.strip().lower()
    for c in Character.all():
        if (c.id or "").lower() == key or (c.name or "").lower() == key:
            return c
    return None


def _find_location(name_or_id: str) -> tuple[str, object] | None:
    """Find location by id or name. Returns (kind, entity)."""
    key = name_or_id.strip().lower()
    # Check Location
    for loc in Location.all():
        if (loc.get("id") or "").lower() == key or (loc.get("name") or "").lower() == key:
            return ("location", loc)
    # Check Dungeon
    for d in Dungeon.all():
        if (d.get("id") or "").lower() == key or (d.get("name") or "").lower() == key:
            return ("dungeon", d)
    # Check Tower
    for t in Tower.all():
        if (t.get("id") or "").lower() == key or (t.get("name") or "").lower() == key:
            return ("tower", t)
    # Check Settlement (by id, settlement_type, or location name)
    loc_by_id = {loc.get("id"): loc for loc in Location.all()}
    for s in Settlement.all():
        sid = (s.get("id") or "").lower()
        loc_id = s.get("location_id")
        loc = loc_by_id.get(loc_id) if loc_id else None
        loc_name = (loc.get("name") or "").lower() if loc else ""
        if sid == key or loc_name == key:
            return ("settlement", s)
    return None


def _get_character_name(cid: str) -> str:
    """Resolve character id to name."""
    c = _find_character(cid)
    return c.name if c else cid


def _find_quest(name_or_id: str) -> object | None:
    """Find quest by id or title (case-insensitive)."""
    key = name_or_id.strip().lower()
    for q in Quest.all():
        if (q.get("id") or "").lower() == key or (q.get("title") or "").lower() == key:
            return q
    return None


def _find_contract(name_or_id: str) -> object | None:
    """Find contract by id (case-insensitive)."""
    key = name_or_id.strip().lower()
    for c in Contract.all():
        if (c.get("id") or "").lower() == key:
            return c
    return None


def _find_item(name_or_id: str) -> object | None:
    """Find item by id or name (case-insensitive)."""
    key = name_or_id.strip().lower()
    for i in Item.all():
        if (i.get("id") or "").lower() == key or (i.get("name") or "").lower() == key:
            return i
    return None


def _find_monster(name_or_id: str) -> object | None:
    """Find monster by id or name (case-insensitive)."""
    key = name_or_id.strip().lower()
    for m in Monster.all():
        if (m.get("id") or "").lower() == key or (m.get("name") or "").lower() == key:
            return m
    return None


def _show_quest_detail(q: object) -> None:
    """Print full quest details."""
    title = q.get("title") or q.get("id") or "?"
    print(f"\n{title}")
    print("-" * 40)
    print(f"  Status:    {q.get('status') or '?'}")
    print(f"  Type:      {q.get('quest_type') or '?'}")
    if q.get("giver_id"):
        print(f"  Giver:     {_get_character_name(q.get('giver_id'))}")
    if q.get("target_id"):
        print(f"  Target:    {_get_character_name(q.get('target_id'))}")
    if q.get("description"):
        print(f"\n  {q.get('description')}")
    participants = q.get("participants") or []
    if participants:
        print(f"\n  Participants:")
        for p in participants:
            print(f"    - {_get_character_name(p.get('character_id', ''))}: {p.get('role', '')}")
    rewards = q.get("rewards") or []
    if rewards:
        print(f"\n  Rewards:")
        for r in rewards:
            print(f"    - {r.get('reward_type', '?')}: {r.get('description', '')}")
    print()


def _show_contract_detail(c: object) -> None:
    """Print full contract details."""
    ctype = c.get("contract_type") or "Contract"
    parties = c.get("parties") or []
    party_names = [_get_character_name(p) for p in parties]
    print(f"\n{ctype}")
    print("-" * 40)
    print(f"  Parties:   {' <-> '.join(party_names)}")
    if c.get("conditions"):
        print(f"\n  Conditions:\n  {c.get('conditions')}")
    if c.get("consequences"):
        print(f"\n  Consequences:\n  {c.get('consequences')}")
    if c.get("description"):
        print(f"\n  {c.get('description')}")
    print()


def _show_item_detail(i: object) -> None:
    """Print full item details."""
    name = i.get("name") or i.get("id") or "?"
    print(f"\n{name}")
    print("-" * 40)
    if i.get("item_type"):
        print(f"  Type:  {i.get('item_type')}")
    if i.get("description"):
        print(f"\n  {i.get('description')}")
    print()


def _show_monster_detail(m: object) -> None:
    """Print full monster details."""
    name = m.get("name") or m.get("id") or "?"
    print(f"\n{name}")
    print("-" * 40)
    if m.get("monster_type"):
        print(f"  Type:  {m.get('monster_type')}")
    if m.get("rank"):
        print(f"  Rank:  {m.get('rank')}")
    if m.get("dungeon_id"):
        print(f"  Dungeon: {m.get('dungeon_id')}")
    if m.get("description"):
        print(f"\n  {m.get('description')}")
    print()


def cmd_who(args: list[str]) -> int:
    """Look up a character by name or id."""
    if not args:
        print("Usage: who <name_or_id>")
        print("Example: who blue")
        return 1
    name_or_id = " ".join(args)
    c = _find_character(name_or_id)
    if not c:
        print(f"No character found: {name_or_id}")
        return 1
    print(f"\n{c.name}")
    print("-" * 40)
    if c.get("race"):
        print(f"  Race:  {c.get('race')}")
    if c.get("class"):
        print(f"  Class: {c.get('class')}")
    if c.get("age") is not None:
        print(f"  Age:   {c.get('age')}")
    if c.get("lineage"):
        print(f"  Lineage: {c.get('lineage')}")
    roles = c.get("roles") or []
    if roles:
        print(f"  Roles: {', '.join(roles)}")
    tags = c.get("tags") or []
    if tags:
        print(f"  Tags:  {', '.join(tags)}")
    if c.description:
        print(f"\n  {c.description}")
    print()
    return 0


def cmd_where(args: list[str]) -> int:
    """Look up a location (dungeon, tower, settlement, region) by name or id."""
    if not args:
        print("Usage: where <name_or_id>")
        print("Example: where \"Cave of Spilled Crystals\"")
        return 1
    name_or_id = " ".join(args)
    found = _find_location(name_or_id)
    if not found:
        print(f"No location found: {name_or_id}")
        return 1
    kind, ent = found
    name = ent.get("name") or ent.get("id") or "?"
    if kind == "settlement":
        loc_id = ent.get("location_id")
        if loc_id:
            for loc in Location.all():
                if loc.get("id") == loc_id:
                    name = loc.get("name") or name
                    break
    print(f"\n{name}")
    print("-" * 40)
    if kind == "dungeon":
        print(f"  Type:   Dungeon")
        if ent.get("danger_level") is not None:
            print(f"  Danger: {ent.get('danger_level')}/10")
        if ent.get("master_type"):
            print(f"  Master: {ent.get('master_type')}")
        if ent.get("has_artificial_tree_of_life") is not None:
            print(f"  Has Artificial Tree: {ent.get('has_artificial_tree_of_life')}")
    elif kind == "tower":
        print(f"  Type:   Tower")
        if ent.get("danger_level") is not None:
            print(f"  Danger: {ent.get('danger_level')}/10")
    elif kind == "settlement":
        print(f"  Type:   {ent.get('settlement_type', 'Settlement')}")
        if ent.get("population_estimate") is not None:
            print(f"  Population: ~{ent.get('population_estimate'):,}")
        if ent.get("rule_type"):
            print(f"  Rule:   {ent.get('rule_type')}")
        income = ent.get("main_income_sources") or []
        if income:
            print(f"  Income: {', '.join(income)}")
    else:
        print(f"  Kind:   {ent.get('kind', 'Location')}")
        if ent.get("danger_level") is not None:
            print(f"  Danger: {ent.get('danger_level')}/10")
    if ent.get("description"):
        print(f"\n  {ent.get('description')}")
    tags = ent.get("tags") or []
    if tags:
        print(f"\n  Tags: {', '.join(tags)}")
    print()
    return 0


def cmd_quests(args: list[str]) -> int:
    """List quests, optionally filtered by status."""
    status_filter = None
    i = 0
    while i < len(args):
        if args[i] == "--status" and i + 1 < len(args):
            status_filter = args[i + 1].lower()
            i += 2
            continue
        i += 1
    quests = Quest.all()
    if status_filter:
        quests = [q for q in quests if (q.get("status") or "").lower() == status_filter]
    print("\nQuests")
    print("=" * 50)
    for q in quests:
        title = q.get("title") or q.get("id") or "?"
        status = q.get("status") or "?"
        qtype = q.get("quest_type") or ""
        print(f"\n  [{status}] {title}")
        if qtype:
            print(f"    Type: {qtype}")
        desc = q.get("description") or ""
        if desc:
            print(f"    {desc[:100]}{'...' if len(desc) > 100 else ''}")
        participants = q.get("participants") or []
        if participants:
            names = [_get_character_name(p.get("character_id", "")) for p in participants]
            print(f"    Participants: {', '.join(names)}")
    print()
    return 0


def cmd_contracts(args: list[str]) -> int:
    """List all contracts (oaths, pacts)."""
    contracts = Contract.all()
    print("\nContracts")
    print("=" * 50)
    for c in contracts:
        ctype = c.get("contract_type") or "Contract"
        parties = c.get("parties") or []
        party_names = [_get_character_name(p) for p in parties]
        print(f"\n  {ctype}")
        print(f"    Parties: {' <-> '.join(party_names)}")
        if c.get("conditions"):
            print(f"    Conditions: {c.get('conditions')[:80]}{'...' if len(c.get('conditions', '')) > 80 else ''}")
        if c.get("consequences"):
            print(f"    Consequences: {c.get('consequences')[:80]}{'...' if len(c.get('consequences', '')) > 80 else ''}")
        if c.description:
            print(f"    {c.description[:80]}{'...' if len(c.description) > 80 else ''}")
    print()
    return 0


def cmd_world(args: list[str]) -> int:
    """Show world overview."""
    w = World.main()
    print("\nBlue's Myth World")
    print("=" * 50)
    print(f"  Name:    {w.get('world_name') or w.get('id')}")
    print(f"  Era:     {w.get('era') or '?'}")
    print(f"  Threat:  {w.get('main_threat') or '?'}")
    if w.description:
        print(f"\n  {w.description}")
    tags = w.get("tags") or []
    if tags:
        print(f"\n  Tags: {', '.join(tags)}")
    print()
    return 0


def cmd_characters(args: list[str]) -> int:
    """List all characters."""
    chars = Character.all()
    print("\nCharacters")
    print("=" * 50)
    for c in chars:
        name = c.name or c.get("id") or "?"
        race = c.get("race") or ""
        cls = c.get("class") or ""
        extra = f" ({race}, {cls})" if race and cls else f" ({race})" if race else f" ({cls})" if cls else ""
        print(f"  {c.get('id') or '?'}: {name}{extra}")
    print(f"\n  Total: {len(chars)}")
    print()
    return 0


def cmd_locations(args: list[str]) -> int:
    """List all locations (regions, roads, villages, etc.)."""
    locs = Location.all()
    print("\nLocations")
    print("=" * 50)
    for loc in locs:
        name = loc.get("name") or loc.get("id") or "?"
        kind = loc.get("kind") or "?"
        danger = loc.get("danger_level")
        dstr = f" [D{danger}]" if danger is not None else ""
        print(f"  {loc.get('id') or '?'}: {name} ({kind}){dstr}")
    print(f"\n  Total: {len(locs)}")
    print()
    return 0


def cmd_dungeons(args: list[str]) -> int:
    """List all dungeons."""
    dungeons = Dungeon.all()
    print("\nDungeons")
    print("=" * 50)
    for d in dungeons:
        name = d.get("name") or d.get("id") or "?"
        danger = d.get("danger_level")
        dstr = f" [D{danger}]" if danger is not None else ""
        print(f"  {d.get('id') or '?'}: {name}{dstr}")
    print(f"\n  Total: {len(dungeons)}")
    print()
    return 0


def _resolve_entity(entity_type: str, key: str) -> object | None:
    """Resolve entity by type and name/id. Returns entity or None."""
    entity_type = entity_type.lower()
    if entity_type.endswith("s"):
        entity_type = entity_type[:-1]
    key = key.strip()
    if entity_type == "world":
        return World.main()
    if entity_type == "character":
        return _find_character(key)
    if entity_type in ("location", "dungeon", "tower", "settlement"):
        found = _find_location(key)
        return found[1] if found else None
    if entity_type == "quest":
        return _find_quest(key)
    if entity_type == "contract":
        return _find_contract(key)
    if entity_type == "item":
        return _find_item(key)
    if entity_type == "monster":
        return _find_monster(key)
    return None


def cmd_action(args: list[str]) -> int:
    """Run an XWQS action on an entity. Usage: action <entity_type> <entity> <action_name>"""
    if len(args) < 3:
        print("Usage: action <entity_type> <entity_name_or_id> <action_name>")
        print("Example: action character blue summary")
        print("Example: action world . describe_world")
        print("Example: action quest 1 summary")
        return 1
    entity_type, entity_key, action_name = args[0], args[1], args[2]
    ent = _resolve_entity(entity_type, entity_key)
    if not ent:
        print(f"Entity not found: {entity_type} '{entity_key}'")
        return 1
    actions = getattr(ent, "list_actions", lambda: [])()
    if action_name not in actions:
        print(f"Action '{action_name}' not found. Available: {', '.join(actions) or 'none'}")
        return 1
    try:
        result = ent.execute_action(action_name)
        if result is not None:
            results = result.get("results", result) if isinstance(result, dict) else result
            if isinstance(results, dict):
                for k, v in results.items():
                    print(f"  {k}: {v}")
            elif isinstance(results, (list, tuple)) and results and isinstance(results[0], dict):
                for row in results:
                    for k, v in row.items():
                        print(f"  {k}: {v}")
            elif isinstance(results, (list, tuple)):
                for item in results:
                    print(f"  {item}")
            else:
                print(f"  {results}")
        return 0
    except Exception as e:
        print(f"Action failed: {e}")
        return 1


def cmd_reload(args: list[str]) -> int:
    """Clear entity cache so next access reloads from disk."""
    invalidate_bluesmyth_cache()
    print("Cache cleared. Data will reload on next access.")
    return 0


def cmd_help(args: list[str]) -> int:
    """Show help."""
    print(__doc__)
    print("Commands:")
    print("  who <name_or_id>        Look up a character")
    print("  where <name_or_id>      Look up a location, dungeon, tower, or settlement")
    print("  quests [--status STATUS] List quests (status: active, planned, completed)")
    print("  contracts               List all contracts and oaths")
    print("  world                   Show world overview")
    print("  characters              List all characters")
    print("  locations               List all locations")
    print("  dungeons                List all dungeons")
    print("  list <entity_type>      List entities; select by number for details")
    print("  action <type> <entity> <action>  Run XWQS action (e.g. action character blue summary)")
    print("  reload                  Refresh cache (data files are auto-reloaded on change)")
    print("  help                    Show this help")
    print("  exit, quit              End the explorer")
    return 0
# Entity type -> (cls, label, id_key, name_key)
# name_key: str = data key, or callable(entity) -> str for derived names (e.g. settlement -> location name)


def _settlement_display_name(s: object) -> str:
    loc_id = s.get("location_id")
    if loc_id:
        for loc in Location.all():
            if loc.get("id") == loc_id:
                return loc.get("name") or loc_id
    return s.get("id") or "?"


def _list_entities(
    cls: type,
    id_key: str = "id",
    name_key: str | Callable[[object], str] = "name",
) -> list[tuple[str, str, object]]:
    """Generic: list all entities from cls as (id, display_name, entity)."""
    out = []
    for e in cls.all():
        eid = e.get(id_key) or "?"
        if callable(name_key):
            name = name_key(e)
        else:
            name = e.get(name_key) or e.get(id_key) or "?"
        out.append((eid, name or eid, e))
    return out
# Entity type -> (cls, label, id_key, name_key)
# name_key: str = data key, or callable for derived names
# Plural (e.g. "characters") is normalized by stripping trailing "s"
_LIST_CONFIG: dict[str, tuple] = {
    "character": (Character, "Character", "id", "name"),
    "location": (Location, "Location", "id", "name"),
    "dungeon": (Dungeon, "Dungeon", "id", "name"),
    "tower": (Tower, "Tower", "id", "name"),
    "settlement": (Settlement, "Settlement", "id", _settlement_display_name),
    "quest": (Quest, "Quest", "id", "title"),
    "contract": (Contract, "Contract", "id", "contract_type"),
    "item": (Item, "Item", "id", "name"),
    "monster": (Monster, "Monster", "id", "name"),
}


def _show_detail_for_entity_type(
    entity_type: str, key: str, entity: object
) -> bool:
    """Show detail for selected entity. Returns True if shown."""
    if entity_type == "character":
        return run_command("who", [key]) == 0
    if entity_type in ("location", "dungeon", "tower", "settlement"):
        return run_command("where", [key]) == 0
    if entity_type == "quest":
        _show_quest_detail(entity)
        return True
    if entity_type == "contract":
        _show_contract_detail(entity)
        return True
    if entity_type == "item":
        _show_item_detail(entity)
        return True
    if entity_type == "monster":
        _show_monster_detail(entity)
        return True
    return False


def cmd_list(args: list[str]) -> int:
    """List entities by type; in interactive mode, prompt to select one for details."""
    if not args:
        print("Usage: list <entity_type>")
        print("Types: character, location, dungeon, tower, settlement, quest, contract, item, monster")
        return 1
    entity_type = args[0].lower()
    if entity_type not in _LIST_CONFIG and entity_type.endswith("s"):
        entity_type = entity_type[:-1]
    if entity_type not in _LIST_CONFIG:
        print(f"Unknown entity type: {args[0]}")
        print("Types: character, location, dungeon, tower, settlement, quest, contract, item, monster")
        return 1
    cls, label, id_key, name_key = _LIST_CONFIG[entity_type]
    items = _list_entities(cls, id_key, name_key)
    if not items:
        print(f"No {label.lower()}s found.")
        return 0
    print(f"\n{label}s ({len(items)})")
    print("=" * 50)
    for i, (key, name, _) in enumerate(items, 1):
        print(f"  {i}. {key} - {name}")
    print()
    if sys.stdin.isatty():
        try:
            choice = input("Enter number or name for details (or Enter to skip): ").strip()
        except EOFError:
            return 0
        if not choice:
            return 0
        key_or_num = choice
        # Try as number first
        if key_or_num.isdigit():
            idx = int(key_or_num)
            if 1 <= idx <= len(items):
                key, name, entity = items[idx - 1]
                _show_detail_for_entity_type(entity_type, key, entity)
                return 0
        # Try as name/id
        key_lower = key_or_num.lower()
        for key, name, entity in items:
            if (key or "").lower() == key_lower or (name or "").lower() == key_lower:
                _show_detail_for_entity_type(entity_type, key, entity)
                return 0
        print(f"Not found: {key_or_num}")
    return 0
COMMANDS = {
    "who": cmd_who,
    "where": cmd_where,
    "list": cmd_list,
    "quests": cmd_quests,
    "contracts": cmd_contracts,
    "world": cmd_world,
    "characters": cmd_characters,
    "locations": cmd_locations,
    "dungeons": cmd_dungeons,
    "action": cmd_action,
    "reload": cmd_reload,
    "help": cmd_help,
}


def run_command(cmd_name: str, cmd_args: list[str]) -> int:
    """Execute a command. Returns 0 on success, 1 on error."""
    if cmd_name not in COMMANDS:
        print(f"Unknown command: {cmd_name}")
        print("Use 'help' for available commands.")
        return 1
    return COMMANDS[cmd_name](cmd_args)


def repl() -> None:
    """Interactive REPL loop. Type 'exit' or 'quit' to end."""
    prompt = "bluesmyth> "
    print("Bluesmyth Lore Explorer -- type 'help' for commands, 'exit' to quit.\n")
    run_command("help", [])
    while True:
        try:
            line = input(prompt).strip()
        except EOFError:
            print()
            break
        if not line:
            continue
        parts = line.split()
        cmd_name = parts[0].lower()
        cmd_args = parts[1:]
        if cmd_name in ("exit", "quit"):
            break
        run_command(cmd_name, cmd_args)


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        repl()
        return 0
    cmd_name = argv[0].lower()
    cmd_args = argv[1:]
    if cmd_name in ("exit", "quit"):
        return 0
    return run_command(cmd_name, cmd_args)
if __name__ == "__main__":
    sys.exit(main())
