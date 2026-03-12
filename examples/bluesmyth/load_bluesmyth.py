#!/usr/bin/env python3
"""
Load all Bluesmyth entity types from data/desc JSON and verify they work with
the Python entity classes in bluesmyth_entities.py.
Ensures:
- Every *.desc.json and *.data.json in data/ has a matching entity class.
- Every entity class loads without error and (optionally) passes validate().
- Schema, data, and Python classes are aligned.
Run from repo root or from xwentity/examples/bluesmyth:
  python load_bluesmyth.py
  python -m xwentity.examples.bluesmyth.load_bluesmyth  # if run from repo root
"""

from __future__ import annotations
import sys
from pathlib import Path
from exonware.xwsystem import JsonSerializer
# Run from bluesmyth directory so local import works
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
DATA_DIR = SCRIPT_DIR / "data"
_JSON = JsonSerializer()


def main() -> int:
    from bluesmyth_entities import (
        Story,
        World,
        Location,
        Character,
        Quest,
        StorySeries,
        StoryArc,
        Scene,
        Event,
        Flashback,
        ContractEvent,
        Planet,
        CrystalShell,
        TreeOfLife,
        Guardian,
        PlanetGuardian,
        ArtificialTreeOfLife,
        Dungeon,
        Tower,
        DungeonFloor,
        TowerFloor,
        Settlement,
        Organization,
        Country,
        Faction,
        Race,
        PlayerCharacter,
        MainCharacter,
        Item,
        Contract,
        Monster,
        Era,
        War,
    )
    # Classes that use .main() return a single instance; others use .all()
    MAIN_CLASSES = (Story, World)
    ALL_CLASSES = (
        Location,
        Character,
        Quest,
        StorySeries,
        StoryArc,
        Scene,
        Event,
        Flashback,
        ContractEvent,
        Planet,
        CrystalShell,
        TreeOfLife,
        Guardian,
        PlanetGuardian,
        ArtificialTreeOfLife,
        Dungeon,
        Tower,
        DungeonFloor,
        TowerFloor,
        Settlement,
        Organization,
        Country,
        Faction,
        Race,
        PlayerCharacter,
        MainCharacter,
        Item,
        Contract,
        Monster,
        Era,
        War,
    )
    errors: list[str] = []
    total_entities = 0
    types_loaded = 0
    # 1) Check every .desc.json and .data.json has a matching class with type_id
    desc_files = sorted(DATA_DIR.glob("*.desc.json"))
    data_files = sorted(DATA_DIR.glob("*.data.json"))
    type_names_from_files = set()
    for f in desc_files:
        # bluesmyth.character.desc.json -> bluesmyth.character
        type_names_from_files.add(f.stem.replace(".desc", ""))
    for f in data_files:
        type_names_from_files.add(f.stem.replace(".data", ""))
    all_entity_classes = MAIN_CLASSES + ALL_CLASSES
    type_names_from_classes = {cls.type_id for cls in all_entity_classes}
    missing_class = type_names_from_files - type_names_from_classes
    if missing_class:
        errors.append(f"Data/desc files with no matching class type_id: {sorted(missing_class)}")
    extra_class = type_names_from_classes - type_names_from_files
    if extra_class:
        errors.append(f"Classes with no data/desc files: {sorted(extra_class)}")
    # 2) Load entities: .main() for Story/World, .all() for the rest
    for cls in MAIN_CLASSES:
        try:
            instance = cls.main()
            entities = [instance] if instance else []
        except Exception as e:
            errors.append(f"{cls.__name__}.main(): {e}")
            continue
        types_loaded += 1
        total_entities += len(entities)
        for i, ent in enumerate(entities):
            try:
                if not ent.validate():
                    errors.append(f"{cls.__name__}[{i}] (id={getattr(ent, 'id', '?')}): validate() returned False")
            except Exception as e:
                errors.append(f"{cls.__name__}[{i}] validate(): {e}")
            # Sanity: entity has id
            eid = getattr(ent, "id", None) or ent.get("id")
            if eid is None or (isinstance(eid, str) and eid.strip() == ""):
                errors.append(f"{cls.__name__}[{i}]: missing or empty id")
    for cls in ALL_CLASSES:
        try:
            entities = cls.all()
        except Exception as e:
            errors.append(f"{cls.__name__}.all(): {e}")
            continue
        types_loaded += 1
        total_entities += len(entities)
        for i, ent in enumerate(entities):
            try:
                if not ent.validate():
                    errors.append(f"{cls.__name__}[{i}] (id={getattr(ent, 'id', '?')}): validate() returned False")
            except Exception as e:
                errors.append(f"{cls.__name__}[{i}] validate(): {e}")
            eid = getattr(ent, "id", None) or ent.get("id")
            if eid is None or (isinstance(eid, str) and eid.strip() == ""):
                errors.append(f"{cls.__name__}[{i}]: missing or empty id")
    # 3) Ensure each desc schema required fields exist in corresponding data items (spot-check)
    for type_name in sorted(type_names_from_files):
        desc_path = DATA_DIR / f"{type_name}.desc.json"
        data_path = DATA_DIR / f"{type_name}.data.json"
        if not desc_path.exists() or not data_path.exists():
            continue
        try:
            desc = _JSON.load_file(desc_path)
            raw = _JSON.load_file(data_path)
        except Exception as e:
            errors.append(f"{type_name} load json: {e}")
            continue
        schema = desc.get("schema") or {}
        required = schema.get("required") or []
        items = raw if isinstance(raw, list) else [raw]
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            for field in required:
                if field not in item:
                    errors.append(f"{type_name} item[{idx}] missing required field '{field}'")
    # Report
    print("=== Bluesmyth load test ===")
    print(f"Types loaded: {types_loaded}")
    print(f"Total entities: {total_entities}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nAll schema, data, and entity classes loaded and validated successfully.")
    return 0
if __name__ == "__main__":
    sys.exit(main())
