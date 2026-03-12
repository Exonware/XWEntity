"""
Bluesmyth Entities
==================
Convenience layer on top of `XWEntity` that:
- Loads the JSON-based *.desc/*.data definitions from this folder.
- Creates ready-to-use `XWEntity` instances (or subclasses) for core types.
This is meant to be a simple example so users can see:
- How to organize entity metadata (`meta`), schema, actions, and data.
- How to hydrate `XWEntity` from JSON files.
- How to use XWEntity/XWObject features: id, uid, name, description, created_at,
  updated_at, state, type; get/set for data; validate(), execute_action(), list_actions().
NOTE:
- Identity (id, uid) and timestamps (created_at, updated_at, deleted_at) are
  handled by XWEntity/XWEntityMetadata; id/created_at/updated_at are synced from
  data when present. The JSON schemas focus on domain fields.
- Place/cosmic scale: see README §2.10. We have World→Planet; Location→Settlement,
  Dungeon, Tower, DungeonFloor, TowerFloor; Country (Organization). No universe,
  galaxy, star, sun, moon, continent, state, town, ocean, sea, river, lake,
  mountain, forest, jungle, or desert as entity types.
"""

from __future__ import annotations
import copy
from pathlib import Path
from typing import Any, Dict, List, Optional
from exonware.xwsystem import JsonSerializer
from exonware.xwentity import XWEntity
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
_JSON = JsonSerializer()
# When writing JSON, use _JSON.save_file(data, path, indent=2) for readable output.
# File-backed cache: type_name -> (data, mtime). Realtime link: reload when file changes.
_data_cache: Dict[str, tuple[Any, float]] = {}
_desc_cache: Dict[str, tuple[Dict[str, Any], float]] = {}


def _get_data_path(type_name: str) -> Path:
    """Path to *.data.json for a type name."""
    return DATA_DIR / f"{type_name}.data.json"


def _get_desc_path(type_name: str) -> Path:
    """Path to *.desc.json for a type name."""
    return DATA_DIR / f"{type_name}.desc.json"


def _file_mtime(path: Path) -> float:
    """File mtime, or 0 if missing/inaccessible."""
    try:
        return path.stat().st_mtime if path.exists() else 0.0
    except OSError:
        return 0.0


def _load_desc(type_name: str) -> Dict[str, Any]:
    """
    Load a *.desc.json definition for a given logical type name.
    Cached with mtime check: reloads when file changes (realtime link).
    """
    path = _get_desc_path(type_name)
    mtime = _file_mtime(path)
    if type_name in _desc_cache:
        cached, cached_mtime = _desc_cache[type_name]
        if cached_mtime >= mtime:
            return cached
    desc = _JSON.load_file(path)
    _desc_cache[type_name] = (desc, mtime)
    return desc


def _load_data(type_name: str) -> Any:
    """
    Load a *.data.json dataset for a given logical type name.
    Cached with mtime check: reloads when file changes (realtime link).
    """
    path = _get_data_path(type_name)
    mtime = _file_mtime(path)
    if type_name in _data_cache:
        cached, cached_mtime = _data_cache[type_name]
        if cached_mtime >= mtime:
            return cached
    data = _JSON.load_file(path)
    _data_cache[type_name] = (data, mtime)
    return data


def invalidate_bluesmyth_cache(type_name: str | None = None) -> None:
    """
    Clear file-backed cache. Pass type_name to clear one type, or None to clear all.
    Use when you need to force a reload without waiting for file change detection.
    """
    global _data_cache, _desc_cache
    if type_name is None:
        _data_cache.clear()
        _desc_cache.clear()
    else:
        _data_cache.pop(type_name, None)
        _desc_cache.pop(type_name, None)


def _create_entity_from_type(type_name: str, index: Optional[int] = None) -> XWEntity:
    """
    Generic helper:
    - Loads schema/actions from <type_name>.desc.json.
    - Loads data from <type_name>.data.json.
    - If `index` is provided and data is a list, pick that element.
    - Returns an `XWEntity` instance.
    """
    desc = _load_desc(type_name)
    raw_data = _load_data(type_name)
    # Some data files are arrays of instances. For a "single-entity" view,
    # we allow selecting one of them via index.
    data = raw_data
    if isinstance(raw_data, list) and index is not None:
        if 0 <= index < len(raw_data):
            data = raw_data[index]
        else:
            raise IndexError(f"Index {index} out of range for {type_name} data")
    schema = desc.get("schema")
    actions = desc.get("actions", {})
    entity_type = desc.get("meta", {}).get("entity_type") or type_name
    return XWEntity(
        schema=schema,
        data=data,
        actions=actions,
        entity_type=str(entity_type).lower(),
    )
# ==============================================================================
# CLASS-BASED (HARD-CODED) ENTITY DEFINITIONS
# ==============================================================================


class _BluesmythBaseEntity(XWEntity):
    """
    Base class for Bluesmyth entities that:
    - Knows its schema file key (type_id) for loading *.desc.json / *.data.json.
    - Lazily loads schema/actions from the corresponding *.desc.json file.
    - Accepts a single data object (dict) for initialization.
    Uses XWEntity's entity.type_id (from schema $id); does not shadow it.
    Uses XWEntity/XWObject identity and metadata (no duplication in schema):
    - id, uid: from entity metadata (id synced from data["id"] when present).
    - created_at, updated_at: from entity metadata (synced from data when present).
    - state, type, version: from XWEntityMetadata.
    - name/title/description: convenience properties that delegate to data via get().
    - get(path), set(path, value): data access; validate(), execute_action(): entity ops.
    """
    type_id: str = ""
    # Cache keyed by type_id so subclasses (e.g. Flashback) don't reuse parent (Story) schema
    _schema_cache: Dict[str, Any] = {}
    _actions_cache: Dict[str, Dict[str, Any]] = {}
    @classmethod

    def _ensure_schema_loaded(cls) -> None:
        if not cls.type_id:
            raise ValueError(f"{cls.__name__} must define type_id")
        if cls.type_id not in cls._schema_cache or cls.type_id not in cls._actions_cache:
            desc = _load_desc(cls.type_id)
            cls._schema_cache[cls.type_id] = desc.get("schema")
            cls._actions_cache[cls.type_id] = desc.get("actions", {}) or {}
    @classmethod

    def invalidate_cache(cls) -> None:
        """Clear file-backed cache for this entity type. Next .all() or .main() will reload from disk."""
        invalidate_bluesmyth_cache(cls.type_id)
    @classmethod

    def data_path(cls) -> Path:
        """Path to the *.data.json file for this entity type (realtime link target)."""
        return _get_data_path(cls.type_id)

    def __init__(self, data: Dict[str, Any] | None = None, **extra):
        """
        Initialize entity:
        - Ensures schema is loaded; sets schema $id so entity.type_id (XWEntity) works.
        - Sets XWEntity.entity_type from schema type.
        """
        cls = self.__class__
        cls._ensure_schema_loaded()
        # Deep copy schema so validation cannot mutate shared cache across entities
        schema_dict = copy.deepcopy(cls._schema_cache.get(cls.type_id) or {})
        type_name = cls.type_id or cls.__name__.lower()
        # Tag entity type at schema level (do not set root "title" – validators can treat it as required data)
        schema_dict.setdefault("x-entity-type", type_name)
        # XWEntity normalizes $id from schema.name when missing
        super().__init__(
            schema=schema_dict,
            data=data or {},
            actions=cls._actions_cache.get(cls.type_id) or {},
            entity_type=type_name,
            **extra,
        )
        # Also reflect type into XWSchema metadata (if available)
        try:
            from exonware.xwschema import XWSchema
            if isinstance(self.schema, XWSchema):
                meta = self.schema.metadata
                if isinstance(meta, dict):
                    meta.setdefault("entity_type", type_name)
                    meta.setdefault("name", type_name)
        except Exception:
            # Best-effort; schema metadata is optional for this example
            pass


class Story(_BluesmythBaseEntity):
    """Class-based representation of the main story entity."""
    type_id = "bluesmyth.story"
    @classmethod

    def main(cls) -> "Story":
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            data = data[0] if data else {}
        return cls(data=data)


class World(_BluesmythBaseEntity):
    """Setting-level entity. Blue's Myth is a single-planet story; see README §2.10."""
    type_id = "bluesmyth.world"
    @classmethod

    def main(cls) -> "World":
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            data = data[0] if data else {}
        return cls(data=data)


class Location(_BluesmythBaseEntity):
    """Generic place (root type). Dungeons, towers, floors, regions; see README §2.10."""
    type_id = "bluesmyth.location"
    @classmethod

    def all(cls) -> List["Location"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Character(_BluesmythBaseEntity):
    """Class-based representation of a single character."""
    type_id = "bluesmyth.character"
    @classmethod

    def all(cls) -> List["Character"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]
    @classmethod

    def main_character(cls) -> "Character":
        for c in cls.all():
            if c.id == "blue":
                return c
        # Fallback: first character
        return cls.all()[0]


class Quest(Story):
    """Class-based representation of a quest (main or sub quest); extends Story."""
    type_id = "bluesmyth.quest"
    @classmethod

    def all(cls) -> List["Quest"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]
# ---------------------------------------------------------------------------
# Additional entities – story structure
# ---------------------------------------------------------------------------


class StorySeries(Story):
    """Series/collection of related stories; extends Story."""
    type_id = "bluesmyth.story_series"
    @classmethod

    def all(cls) -> List["StorySeries"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class StoryArc(Story):
    """Major narrative arc (childhood, rising adventurer, etc.); extends Story."""
    type_id = "bluesmyth.story_arc"
    @classmethod

    def all(cls) -> List["StoryArc"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Scene(Story):
    """Concrete scene within an arc; extends Story."""
    type_id = "bluesmyth.scene"
    @classmethod

    def all(cls) -> List["Scene"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Event(Story):
    """Key story beat (turning points, reveals, etc.); extends Story."""
    type_id = "bluesmyth.event"
    @classmethod

    def all(cls) -> List["Event"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Flashback(Story):
    """Flashback beats referencing earlier events; extends Story."""
    type_id = "bluesmyth.flashback"
    @classmethod

    def all(cls) -> List["Flashback"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class ContractEvent(Story):
    """Events specifically centered on contracts / oaths; extends Story."""
    type_id = "bluesmyth.contract_event"
    @classmethod

    def all(cls) -> List["ContractEvent"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]
# ---------------------------------------------------------------------------
# World / cosmos / meta (place scale: README §2.10)
# ---------------------------------------------------------------------------


class Planet(World):
    """Physical world; Tree of Life at its core. Extends World. No universe/galaxy/star/sun/moon entities."""
    type_id = "bluesmyth.planet"
    @classmethod

    def all(cls) -> List["Planet"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class CrystalShell(_BluesmythBaseEntity):
    """Wraps the planet; mimics sun, moon, and stars (not separate entities). See README §2.10."""
    type_id = "bluesmyth.crystal_shell"
    @classmethod

    def all(cls) -> List["CrystalShell"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class TreeOfLife(_BluesmythBaseEntity):
    type_id = "bluesmyth.tree_of_life"
    @classmethod

    def all(cls) -> List["TreeOfLife"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Guardian(_BluesmythBaseEntity):
    type_id = "bluesmyth.guardian"
    @classmethod

    def all(cls) -> List["Guardian"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class PlanetGuardian(Guardian):
    """Planet-bound guardian; extends Guardian (README: PlanetGuardian:Guardian:WorldSpirit)."""
    type_id = "bluesmyth.planet_guardian"
    @classmethod

    def all(cls) -> List["PlanetGuardian"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class ArtificialTreeOfLife(_BluesmythBaseEntity):
    type_id = "bluesmyth.artificial_tree_of_life"
    @classmethod

    def all(cls) -> List["ArtificialTreeOfLife"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Dungeon(Location):
    """Semi-sentient arcane structure; extends Location. Cities can exist inside. No ocean/forest/desert etc."""
    type_id = "bluesmyth.dungeon"
    @classmethod

    def all(cls) -> List["Dungeon"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Tower(Location):
    """Semi-sentient arcane structure; extends Location. Story focuses on dungeons, towers, villages."""
    type_id = "bluesmyth.tower"
    @classmethod

    def all(cls) -> List["Tower"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class DungeonFloor(Location):
    """SubLocation: one floor inside a dungeon; extends Location."""
    type_id = "bluesmyth.dungeon_floor"
    @classmethod

    def all(cls) -> List["DungeonFloor"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class TowerFloor(Location):
    """SubLocation: one floor inside a tower; extends Location."""
    type_id = "bluesmyth.tower_floor"
    @classmethod

    def all(cls) -> List["TowerFloor"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Settlement(Location):
    """Village, city, tower city. Use settlement_type; no separate Town entity. Extends Location (README §2.10)."""
    type_id = "bluesmyth.settlement"
    @classmethod

    def all(cls) -> List["Settlement"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Organization(_BluesmythBaseEntity):
    type_id = "bluesmyth.organization"
    @classmethod

    def all(cls) -> List["Organization"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Country(Organization):
    """Political unit (e.g. Elf Kingdom, human/demi-human lands). No continent/state. Extends Organization (§2.10)."""
    type_id = "bluesmyth.country"
    @classmethod

    def all(cls) -> List["Country"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Faction(Organization):
    """Faction (e.g. political, racial); extends Organization (README §2.2)."""
    type_id = "bluesmyth.faction"
    @classmethod

    def all(cls) -> List["Faction"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Race(_BluesmythBaseEntity):
    type_id = "bluesmyth.race"
    @classmethod

    def all(cls) -> List["Race"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]
# ---------------------------------------------------------------------------
# Character roles and classifications
# ---------------------------------------------------------------------------


class PlayerCharacter(Character):
    """Player-controlled or main POV character; extends Character."""
    type_id = "bluesmyth.player_character"
    @classmethod

    def all(cls) -> List["PlayerCharacter"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class MainCharacter(Character):
    """Main protagonist; extends Character."""
    type_id = "bluesmyth.main_character"
    @classmethod

    def all(cls) -> List["MainCharacter"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]
# ---------------------------------------------------------------------------
# Items, contracts, monsters, history
# ---------------------------------------------------------------------------


class Item(_BluesmythBaseEntity):
    type_id = "bluesmyth.item"
    @classmethod

    def all(cls) -> List["Item"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Contract(_BluesmythBaseEntity):
    type_id = "bluesmyth.contract"
    @classmethod

    def all(cls) -> List["Contract"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Monster(_BluesmythBaseEntity):
    type_id = "bluesmyth.monster"
    @classmethod

    def all(cls) -> List["Monster"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class Era(_BluesmythBaseEntity):
    type_id = "bluesmyth.era"
    @classmethod

    def all(cls) -> List["Era"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]


class War(_BluesmythBaseEntity):
    type_id = "bluesmyth.war"
    @classmethod

    def all(cls) -> List["War"]:
        data = _load_data(cls.type_id)
        if isinstance(data, list):
            return [cls(d) for d in data]
        return [cls(data)]
__all__ = [
    "invalidate_bluesmyth_cache",
    "Story",
    "World",
    "Planet",
    "CrystalShell",
    "TreeOfLife",
    "Guardian",
    "PlanetGuardian",
    "ArtificialTreeOfLife",
    "Dungeon",
    "Tower",
    "DungeonFloor",
    "TowerFloor",
    "Location",
    "Settlement",
    "Country",
    "Faction",
    "Organization",
    "Race",
    "Character",
    "PlayerCharacter",
    "MainCharacter",
    "StorySeries",
    "StoryArc",
    "Scene",
    "Event",
    "Flashback",
    "Quest",
    "ContractEvent",
    "Item",
    "Contract",
    "Monster",
    "Era",
    "War",
]
