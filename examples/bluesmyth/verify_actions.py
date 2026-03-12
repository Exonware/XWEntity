#!/usr/bin/env python3
"""Verify XWQS actions execute correctly across Bluesmyth entities."""

import sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from bluesmyth_entities import (
    Character, World, Quest, Location, Dungeon, Item, Monster,
    Tower, Settlement, Contract, Story, StoryArc,
)
from bluesmyth_explorer import _resolve_entity
# Sample: test actions using known entity ids
SAMPLES = [
    ("character", "blue", "summary"),
    ("character", "blue", "full"),
    ("character", "blue", "roles_only"),
    ("world", ".", "describe_world"),
    ("world", ".", "full"),
    ("quest", "quest_rescue_mother", "summary"),
    ("quest", "quest_rescue_mother", "by_status"),
    ("location", "dangerous_demi_human_region", "summary"),
    ("location", "village_outskirts", "full"),
    ("dungeon", "cave_of_spilled_crystals", "summary"),
    ("dungeon", "cave_of_spilled_crystals", "tags"),
    ("item", "blue_first_knife", "summary"),
    ("item", "fairy_crystal", "by_rarity"),
    ("monster", "cave_crawler_common", "summary"),
    ("tower", "skyward_tower_city_core", "summary"),
    ("settlement", "settlement_ironcross_town", "summary"),
    ("contract", "fairy_life_oath_blue", "summary"),
]


def main():
    failed = []
    passed = 0
    for entity_type, entity_key, action_name in SAMPLES:
        ent = _resolve_entity(entity_type, entity_key)
        if not ent:
            failed.append((entity_type, entity_key, action_name, "Entity not found"))
            continue
        actions = getattr(ent, "list_actions", lambda: [])()
        if action_name not in actions:
            failed.append((entity_type, entity_key, action_name, f"Action not in {actions}"))
            continue
        try:
            result = ent.execute_action(action_name)
            if result is not None:
                results = result.get("results", result) if isinstance(result, dict) else result
                if results is not None:
                    passed += 1
                    print(f"OK {entity_type} {entity_key} {action_name}")
                else:
                    passed += 1
                    print(f"OK {entity_type} {entity_key} {action_name} (empty)")
            else:
                passed += 1
                print(f"OK {entity_type} {entity_key} {action_name} (None)")
        except Exception as e:
            failed.append((entity_type, entity_key, action_name, str(e)))
            print(f"FAIL {entity_type} {entity_key} {action_name}: {e}")
    print(f"\nPassed: {passed}, Failed: {len(failed)}")
    if failed:
        print("Failures:")
        for t, k, a, err in failed:
            print(f"  {t} {k} {a}: {err}")
        return 1
    return 0
if __name__ == "__main__":
    sys.exit(main())
