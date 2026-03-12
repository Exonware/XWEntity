from pathlib import Path
from exonware.xwsystem import JsonSerializer
from bluesmyth_entities import Character, DATA_DIR


def main() -> None:
    """
    Simple demo: print information about the main character (Blue),
    using the hard-coded `Character(XWEntity)` subclass, then create
    a new magician character via Python and append her to the character data file.
    """
    blue = Character.main_character()
    name = blue.name
    race = blue.get("race")
    cls = blue.get("class")
    roles = blue.get("roles") or []
    print("=== Blue's Myth: Main Character ===")
    print(f"Name : {name}")
    print(f"Race : {race}")
    print(f"Class: {cls}")
    print(f"Roles: {', '.join(roles)}")
    # ------------------------------------------------------------------
    # Create a new magician character and append her to bluesmyth.character.data.json
    # ------------------------------------------------------------------
    magician = Character(
        data={
            "id": "luna",
            "name": "Luna Starweaver",
            "race": "Human",
            "lineage": "Descendant of an ancient arcane bloodline",
            "age": 16,
            "class": "Magician",
            "roles": ["SupportingCharacter", "Magician"],
            "tags": ["spellcaster", "party_mage", "arcane_scholar"],
            "description": (
                "A young magician who joined Blue's party, specializing in "
                "protective and utility magic."
            ),
        }
    )
    character_data_path = DATA_DIR / "bluesmyth.character.data.json"
    json_ser = JsonSerializer()
    current = json_ser.load_file(character_data_path)
    if not isinstance(current, list):
        current = [current] if isinstance(current, dict) else []
    payload = (
        magician._data.to_native()
        if hasattr(magician._data, "to_native")
        else getattr(magician._data, "_data", None) or {}
    )
    existing_ids = {c.get("id") for c in current if isinstance(c, dict)}
    if payload.get("id") not in existing_ids:
        current.append(payload)
        json_ser.save_file(current, character_data_path, indent=2, ensure_ascii=False)
        print()
        print(f"Added {payload.get('name', 'Luna')} to {character_data_path.name}")
    else:
        print()
        print(f"Character id={payload.get('id')} already in {character_data_path.name}")
if __name__ == "__main__":
    main()
