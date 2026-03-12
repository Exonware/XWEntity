"""
Bluesmyth Files API
===================
This module exposes the *file-driven* way of working with Bluesmyth entities.
It mirrors the loader utilities and registry from `bluesmyth_entities.py`,
so you can see the JSON-based approach separately from the class-based one.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from exonware.xwsystem import JsonSerializer
from exonware.xwentity import XWEntity
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
_JSON = JsonSerializer()
# When writing JSON, use _JSON.save_file(data, path, indent=2) for readable output.


def load_desc(type_name: str) -> Dict[str, Any]:
    """Public wrapper around desc loader for a given logical type name."""
    path = DATA_DIR / f"{type_name}.desc.json"
    return _JSON.load_file(path)


def load_data(type_name: str) -> Any:
    """Public wrapper around data loader for a given logical type name."""
    path = DATA_DIR / f"{type_name}.data.json"
    return _JSON.load_file(path)


def create_entity_from_type(type_name: str, index: Optional[int] = None) -> XWEntity:
    """
    Generic helper:
    - Loads schema/actions from <type_name>.desc.json.
    - Loads data from <type_name>.data.json.
    - If `index` is provided and data is a list, pick that element.
    - Returns an `XWEntity` instance.
    """
    desc = load_desc(type_name)
    raw_data = load_data(type_name)
    data = raw_data
    if isinstance(raw_data, list) and index is not None:
        if 0 <= index < len(raw_data):
            data = raw_data[index]
        else:
            raise IndexError(f"Index {index} out of range for {type_name} data")
    schema = dict(desc.get("schema") or {})
    actions = desc.get("actions", {})
    entity_type = desc.get("meta", {}).get("entity_type") or type_name
    # Canonical schema $id (e.g. bluesmyth.Character); filenames use .lower()
    if "$id" not in schema and "id" not in schema:
        parts = type_name.split(".")
        schema["$id"] = ".".join(parts[:-1] + [parts[-1].capitalize()]) if parts else type_name
    return XWEntity(
        schema=schema,
        data=data,
        actions=actions,
        entity_type=str(entity_type).lower(),
    )
@dataclass


class BluesmythEntityBundle:
    """
    Simple struct representing:
    - The raw desc JSON (meta + schema + actions).
    - The raw data JSON (list or dict).
    - A mapping of instantiated entities (if you want them).
    """
    type_name: str
    desc: Dict[str, Any]
    data: Any
    entities: List[XWEntity]


class BluesmythEntities:
    """
    High-level access to all Bluesmyth entity types using file-based definitions.
    """
    CORE_TYPES: Tuple[str, ...] = (
        "bluesmyth.story",
        "bluesmyth.story_series",
        "bluesmyth.story_arc",
        "bluesmyth.scene",
        "bluesmyth.event",
        "bluesmyth.flashback",
        "bluesmyth.quest",
        "bluesmyth.contract_event",
        "bluesmyth.world",
        "bluesmyth.planet",
        "bluesmyth.crystal_shell",
        "bluesmyth.tree_of_life",
        "bluesmyth.guardian",
        "bluesmyth.planet_guardian",
        "bluesmyth.artificial_tree_of_life",
        "bluesmyth.dungeon",
        "bluesmyth.tower",
        "bluesmyth.dungeon_floor",
        "bluesmyth.tower_floor",
        "bluesmyth.location",
        "bluesmyth.settlement",
        "bluesmyth.country",
        "bluesmyth.faction",
        "bluesmyth.organization",
        "bluesmyth.race",
        "bluesmyth.character",
        "bluesmyth.player_character",
        "bluesmyth.main_character",
        "bluesmyth.item",
        "bluesmyth.contract",
        "bluesmyth.monster",
    )
    @classmethod

    def load_all(cls) -> Dict[str, BluesmythEntityBundle]:
        """
        Load all known Bluesmyth types into memory.
        Returns:
            Mapping:
                type_name -> BluesmythEntityBundle
        """
        bundles: Dict[str, BluesmythEntityBundle] = {}
        for type_name in cls.CORE_TYPES:
            desc = load_desc(type_name)
            data = load_data(type_name)
            entities: List[XWEntity] = []
            if isinstance(data, list):
                for row in data:
                    entities.append(
                        XWEntity(
                            schema=desc.get("schema"),
                            data=row,
                            actions=desc.get("actions", {}),
                            entity_type=str(desc.get("meta", {}).get("entity_type") or type_name).lower(),
                        )
                    )
            else:
                entities.append(
                    XWEntity(
                        schema=desc.get("schema"),
                        data=data,
                        actions=desc.get("actions", {}),
                        entity_type=str(desc.get("meta", {}).get("entity_type") or type_name).lower(),
                    )
                )
            bundles[type_name] = BluesmythEntityBundle(
                type_name=type_name,
                desc=desc,
                data=data,
                entities=entities,
            )
        return bundles
    # Convenience short-hands
    @classmethod

    def story(cls) -> XWEntity:
        """Return the main Blue's Myth story entity."""
        return create_entity_from_type("bluesmyth.story", index=0)
    @classmethod

    def world(cls) -> XWEntity:
        """Return the main world entity."""
        return create_entity_from_type("bluesmyth.world", index=0)
    @classmethod

    def characters(cls) -> List[XWEntity]:
        """Return all character entities."""
        desc = load_desc("bluesmyth.character")
        data = load_data("bluesmyth.character")
        schema = desc.get("schema")
        actions = desc.get("actions", {})
        entity_type = str(desc.get("meta", {}).get("entity_type") or "character").lower()
        entities: List[XWEntity] = []
        if isinstance(data, list):
            for row in data:
                entities.append(
                    XWEntity(schema=schema, data=row, actions=actions, entity_type=entity_type)
                )
        else:
            entities.append(
                XWEntity(schema=schema, data=data, actions=actions, entity_type=entity_type)
            )
        return entities
    @classmethod

    def quests(cls) -> List[XWEntity]:
        """Return all quest entities (main + sub quests)."""
        desc = load_desc("bluesmyth.quest")
        data = load_data("bluesmyth.quest")
        schema = desc.get("schema")
        actions = desc.get("actions", {})
        entity_type = str(desc.get("meta", {}).get("entity_type") or "quest").lower()
        entities: List[XWEntity] = []
        if isinstance(data, list):
            for row in data:
                entities.append(
                    XWEntity(schema=schema, data=row, actions=actions, entity_type=entity_type)
                )
        else:
            entities.append(
                XWEntity(schema=schema, data=data, actions=actions, entity_type=entity_type)
            )
        return entities
    @classmethod

    def settlements(cls) -> List[XWEntity]:
        """Return all settlements (villages, cities, tower cities)."""
        desc = load_desc("bluesmyth.settlement")
        data = load_data("bluesmyth.settlement")
        schema = desc.get("schema")
        actions = desc.get("actions", {})
        entity_type = "settlement"
        entities: List[XWEntity] = []
        if isinstance(data, list):
            for row in data:
                entities.append(
                    XWEntity(schema=schema, data=row, actions=actions, entity_type=entity_type)
                )
        else:
            entities.append(
                XWEntity(schema=schema, data=data, actions=actions, entity_type=entity_type)
            )
        return entities
    @classmethod

    def countries(cls) -> List[XWEntity]:
        """Return all country-level political units."""
        desc = load_desc("bluesmyth.country")
        data = load_data("bluesmyth.country")
        schema = desc.get("schema")
        actions = desc.get("actions", {})
        entity_type = "country"
        entities: List[XWEntity] = []
        if isinstance(data, list):
            for row in data:
                entities.append(
                    XWEntity(schema=schema, data=row, actions=actions, entity_type=entity_type)
                )
        else:
            entities.append(
                XWEntity(schema=schema, data=data, actions=actions, entity_type=entity_type)
            )
        return entities
__all__ = [
    "BluesmythEntities",
    "BluesmythEntityBundle",
    "load_desc",
    "load_data",
    "create_entity_from_type",
]
