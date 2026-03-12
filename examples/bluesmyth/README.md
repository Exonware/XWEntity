## Blue’s Myth – XWEntity World Example

This example shows how to model a story world – **Blue’s Myth** – using `XWEntity` as a flexible, JSON‑driven entity system.

It focuses on:

- **Story & world overview** – the setting and main conflicts.
- **Entity types** – characters, items, locations, dungeons, guilds, etc.
- **How these types map to `XWEntity` schemas** – so you can query and manipulate the world with XW tools.

---

## 1. Story Overview – Blue’s Myth

**Premise**

- After a **5000‑year war**, humans win against demi‑humans (elves, dwarves, etc.) with help from **demons**.
- Once victorious, humans **turn on their demon masters** and also **enslave the demi‑humans**, reducing them to second‑class citizens and slave stock.
- The world’s economy and survival revolve around **living Dungeons and Towers** – arcane structures that spawn monsters, resources, and entire ecosystems.
- The planet is wrapped by a **crystal shell** that mimics sun, moon, and stars, forged long ago by **sacrificial fairies** to shield the world from external horrors.

**Cosmic layer**

- At the **planet’s core** stands the **Tree of Life**, guarded by a powerful **Guardian** sharing one soul with the tree.
- Guardians:
  - Provide **mana**, protect the planet, nudge **evolution**, and can repel even cosmic threats.
  - Are a special race created by **Exonalixe Deolopia**, a vanished ancient being.
  - **Cannot fight each other**; even “invincible” creatures avoid fighting them directly.

**Dungeons and Towers**

- **Dungeons** and **Towers** are semi‑sentient arcane structures:
  - They create **ecosystems** and **attract adventurers**.
  - They can be so large that **cities exist inside them**.
  - They recycle monsters via **artificial Trees of Life** (not as strong as the true core Tree).
  - Many **Dragons** act as dungeon masters.
- **Overflow / breaks** happen if local authorities and adventurers fail to manage them, causing **monster spills** into nearby lands.

**The protagonist: the blacksmith boy (“Blue”)**

- **Mother**: an **Elven royal magic knight**.
- **Father**: a **Dwarven hero and master blacksmith**.
- The boy grows up in a **dangerous demi‑human village** near a dungeon, under constant monster threat.
- He loves:
  - **Blacksmithing**
  - **Dungeons**
  - **Adventuring**
  and dreams of forging the **best weapons** from dungeon/tower materials and testing them everywhere.

**Inciting incident**

- At **5 years old**, a war leaves:
  - Father **one‑armed**.
  - Mother apparently **gone** (taken by the Elf King, though he doesn’t know yet).
- The boy **resents** his father, thinking he failed to save her, and refuses to learn smithing from him.

**The miracle and the fairy**

- At **9 years old**, he and his friends gather materials near a dungeon.
- A **monster break** occurs; a strong monster slips through and attacks:
  - The boy fights, crying, while protecting his **childhood friend (a girl)**.
  - His father rushes in with only one arm to save him.
  - The boy, seeing his father’s resolve, **sacrifices himself** to save him, gouging out the monster’s eye.
- As the boy is about to die, the girl **prays**, and a **huge crystal** falls from the sky, killing the monster.
- Inside the crystal is a **light‑blue fairy**:
  - She forms a **contract** with the boy.
  - Condition: she saves him and the others now; in **9 years** he must take her to the **Guardian of the Tree of Life**.
  - The fairy moves in with the boy and his father; their relationships **heal and deepen**.

**Growth arc**

- The boy learns:
  - **Blacksmithing, adventuring, fighting, and mining** from his father.
  - **Magic** from a teacher (inherited affinity from his mother).
- At **11**, he joins the **Adventurer Guild**.
- By **12**, he becomes a **proper adventurer**:
  - Crafts his own weapons and armor.
  - Forges gear for his **party**.
  - Gains deep expertise in **dungeons, towers, and materials**.

**Revelation about his mother**

- When the father deems him ready, he reveals:
  - The **Elf King** took the boy’s mother.
  - Father lost his arm; she offered herself (via an **oath**) to save him.
  - If the father breaks his promise to **live on and protect their children**, she **dies by the oath**.
  - So he stayed to **raise the boy and his little sister**, instead of going on a suicidal rescue.
- The boy is shaken, but now understands his father’s sacrifice.
  - Father stays in the village with the sister.
  - The boy sets out on a **world‑spanning journey**.

**Long‑term arc (high level)**

- Phase 1: Become strong enough to **challenge the Elf Kingdom** and rescue his mother.
- Phase 2: Confront the **demons** and learn that **dungeons and towers** are crucial to keeping the world alive.
- Phase 3: Descend to the **Tree of Life**:
  - Learn about **ancient civilizations** and **golems**.
  - Understand why **space is dangerous** beyond the crystal shell.
- Phase 4: Go **outside the shell**, fighting cosmic monsters on its surface using **self‑made golems**.
- Phase 5: Discover **other planets** with advanced blacksmithing tech – seeds for another story with new characters.

Throughout, **guilds, clans, and parties** are core: they structure society, adventurer life, and the economy.

---

## 2. XWEntity Type Taxonomy for Blue’s Myth

We describe entity kinds using a readable colon style:

- `Dungeon:ArcaneStructure:Location`
- `Sword:Weapon:Equipment:Item`
- `PlayerCharacter:Character`
- `MainCharacter:Character`

These are **conceptual types** you can map to `schema.name` values and `properties` in `XWEntity`.

### 2.1 Story structure

- `Story`
- `StorySeries:StoryCollection`
- `StoryArc:StoryPart`
- `Scene:StoryPart`
- `Event:StoryBeat`
- `Flashback:StoryBeat`
- `Quest:StoryBeat`
- `ContractEvent:StoryBeat`

Use these when you want to model **narrative units** (whole book, arc, specific scene, a key event, etc.) as entities.

### 2.2 World / cosmos / meta

- `World:Setting`
- `Planet:World:Setting`
- `CrystalShell:CosmicStructure`
- `TreeOfLife:WorldCore`
- `ArtificialTreeOfLife:WorldCoreFragment`
- `Guardian:WorldSpirit`
- `PlanetGuardian:Guardian:WorldSpirit`
- `Dungeon:ArcaneStructure:Location`          ← **given**
- `Tower:ArcaneStructure:Location`            ← **given**
- `DungeonFloor:SubLocation`
- `TowerFloor:SubLocation`
- `Ecosystem:WorldSystem`
- `WeatherPattern:WorldSystem`
- `Era:TimelineSegment`
- `War:HistoricalEvent`
- `Faction:Organization`
- `Race:Species`

These cover **cosmic structures** (shell, Tree, Guardian), **macro‑locations** (dungeons, towers), and **long‑term history** (wars, eras).

### 2.3 Locations & settlements

- `Location`
- `Region:Location`
- `Village:Settlement:Location`
- `City:Settlement:Location`
- `TowerCity:City:Location`
- `CapitalCity:City:Location`
- `DungeonEntrance:SubLocation`
- `CombatZone:SubLocation`
- `SafeZone:SubLocation`
- `CoreChamber:SubLocation`

Use these to represent **places** your characters can visit, live in, or fight in (village, dungeon entrance, tower floors, etc.).

### 2.4 Characters & roles

- `Character`
- `PlayerCharacter:Character`                 ← **given**
- `NonPlayerCharacter:Character`              ← **given**
- `MainCharacter:Character`                   ← **given**
- `SupportingCharacter:Character`
- `Antagonist:Character`
- `Mentor:Character`
- `GuardianSpirit:Character`
- `Fairy:Character`
- `DemiHuman:Character`
- `Human:Character`
- `Elf:Character`
- `Dwarf:Character`
- `MixedBlood:Character`

Roles & professions:

- `GuildMember:CharacterRole`
- `ClanMember:CharacterRole`
- `Blacksmith:Profession`
- `MagicKnight:Profession`
- `Adventurer:Profession`
- `DungeonMaster:Profession`
- `TowerMaster:Profession`

These cover the **boy**, his **parents**, the **fairy**, **friends**, **guild members**, and big figures like dungeon/tower masters.

### 2.5 Organizations (guilds, clans, factions)

- `Organization`
- `Guild:Organization`
- `AdventurerGuild:Guild`
- `Clan:Organization`
- `SmithingClan:Clan`
- `RoyalHouse:Organization`
- `Army:Organization`
- `DemonFaction:Organization`
- `HumanEmpire:Organization`
- `DemiHumanResistance:Organization`
- `Party:Organization`
- `AdventurerParty:Party`
- `RaidGroup:Party`

Use these for **guilds, clans, political powers, and parties** that the protagonist interacts with or joins.

### 2.6 Items, equipment, materials

- `Item`
- `Equipment:Item`
- `Weapon:Equipment:Item`
- `Armor:Equipment:Item`
- `Accessory:Equipment:Item`
- `Consumable:Item`
- `CraftingMaterial:Item`
- `Ore:CraftingMaterial:Item`
- `CrystalShard:CraftingMaterial:Item`
- `Relic:Item`
- `Artifact:Relic:Item`

Specific weapons (given and extended):

- `Sword:Weapon:Equipment:Item`               ← **given**
- `Axe:Weapon:Equipment:Item`                 ← **given**
- `Hammer:Weapon:Equipment:Item`
- `Dagger:Weapon:Equipment:Item`
- `Spear:Weapon:Equipment:Item`
- `Bow:Weapon:Equipment:Item`
- `MagicStaff:Weapon:Equipment:Item`

Blacksmithing / crafting support:

- `Blueprint:CraftingRecipe`
- `Forge:Workshop`
- `Enhancement:UpgradeStep`

These are perfect for **the boy’s weapons**, his father’s **warhammer**, his mother’s **royal blade**, **fairy crystal**, ores, etc.

### 2.7 Magic, contracts, systems

- `MagicSystem:WorldRuleSet`
- `Spell:ActionTemplate`
- `Enchantment:Modifier`
- `Curse:Modifier`
- `Blessing:Modifier`
- `Contract:Bond`
- `LifeOath:Contract:Bond`
- `FairyContract:Contract:Bond`
- `QuestContract:Contract:Bond`
- `Skill:ActionTemplate`
- `Technique:Skill`

These model **oaths**, **contracts with fairies**, **quest contracts**, and the **spell / skill** system characters use.

### 2.8 Economy / meta‑systems (dungeons, guilds, ranking)

- `DungeonRuleSet:WorldRuleSet`
- `TowerRuleSet:WorldRuleSet`
- `Monster:Entity`
- `BossMonster:Monster`
- `Dragon:BossMonster`
- `LootTable:SystemConfig`
- `DropRule:SystemConfig`
- `Rank:ProgressionStep`
- `AdventurerRank:Rank`
- `GuildRank:Rank`

These capture the **mechanical side**: dungeon spawning rules, monster classifications, loot, and rank systems for guilds and adventurers.

---

## 2.9 Which extends which (Python: `bluesmyth_entities.py`)

The example implements the taxonomy above with **class inheritance**. Every entity class extends **at least** `XWEntity` (via `_BluesmythBaseEntity(XWEntity)` or a subclass). Use this as the reference for “which extends which” in code.

| Base (root) | Extends base | Notes |
|-------------|--------------|--------|
| **Story** | StorySeries, StoryArc, Scene, Event, Flashback, Quest, ContractEvent | §2.1 |
| **World** | Planet | §2.2 |
| **Location** | Settlement, Dungeon, Tower, DungeonFloor, TowerFloor | §2.2, §2.3 |
| **Character** | PlayerCharacter, MainCharacter | §2.4 |
| **Organization** | Country, Faction | §2.2, §2.5 |
| **Guardian** | PlanetGuardian | §2.2 (PlanetGuardian:Guardian:WorldSpirit) |

All of the above roots extend `_BluesmythBaseEntity(XWEntity)`. Types not listed in the table (CrystalShell, TreeOfLife, ArtificialTreeOfLife, Race, Item, Contract, Monster, Era, War, etc.) also extend `_BluesmythBaseEntity` directly.

#### Complete entity class list (each extends XWEntity)

| Entity class | Extends | type_id |
|--------------|---------|-----------|
| `_BluesmythBaseEntity` | `XWEntity` | — |
| **Story** | _BluesmythBaseEntity | bluesmyth.story |
| StorySeries | Story | bluesmyth.story_series |
| StoryArc | Story | bluesmyth.story_arc |
| Scene | Story | bluesmyth.scene |
| Event | Story | bluesmyth.event |
| Flashback | Story | bluesmyth.flashback |
| Quest | Story | bluesmyth.quest |
| ContractEvent | Story | bluesmyth.contract_event |
| **World** | _BluesmythBaseEntity | bluesmyth.world |
| Planet | World | bluesmyth.planet |
| **Location** | _BluesmythBaseEntity | bluesmyth.location |
| Settlement | Location | bluesmyth.settlement |
| Dungeon | Location | bluesmyth.dungeon |
| Tower | Location | bluesmyth.tower |
| DungeonFloor | Location | bluesmyth.dungeon_floor |
| TowerFloor | Location | bluesmyth.tower_floor |
| **Character** | _BluesmythBaseEntity | bluesmyth.character |
| PlayerCharacter | Character | bluesmyth.player_character |
| MainCharacter | Character | bluesmyth.main_character |
| **Organization** | _BluesmythBaseEntity | bluesmyth.organization |
| Country | Organization | bluesmyth.country |
| Faction | Organization | bluesmyth.faction |
| **Guardian** | _BluesmythBaseEntity | bluesmyth.guardian |
| PlanetGuardian | Guardian | bluesmyth.planet_guardian |
| CrystalShell | _BluesmythBaseEntity | bluesmyth.crystal_shell |
| TreeOfLife | _BluesmythBaseEntity | bluesmyth.tree_of_life |
| ArtificialTreeOfLife | _BluesmythBaseEntity | bluesmyth.artificial_tree_of_life |
| Race | _BluesmythBaseEntity | bluesmyth.race |
| Item | _BluesmythBaseEntity | bluesmyth.item |
| Contract | _BluesmythBaseEntity | bluesmyth.contract |
| Monster | _BluesmythBaseEntity | bluesmyth.monster |
| Era | _BluesmythBaseEntity | bluesmyth.era |
| War | _BluesmythBaseEntity | bluesmyth.war |

### 2.10 Place and cosmic scale (relevant to the story)

Blue’s Myth is a **single‑planet** story. Only the following scales are modelled as entity types; the rest are either absent or folded into these.

| Scale / place type | In the example? | Story relevance |
|--------------------|-----------------|------------------|
| **Universe, galaxy** | No | Story stays on one world. |
| **Stars, suns, moons** | No (as entities) | The **crystal shell** mimics sun, moon, and stars; they are not separate entities. |
| **Planet** | Yes (`Planet`, extends `World`) | The physical world; Tree of Life at its core; Phase 5 hints at other planets. |
| **Continent** | No | Not used in the narrative. |
| **Country** | Yes (`Country`, extends `Organization`) | Elf Kingdom, human/demi‑human lands, political units. |
| **State** | No | Not used; countries are the main political level. |
| **City, town, village** | Yes (as **Settlement**) | `Settlement` has `settlement_type`; used for Blue’s village, cities inside dungeons/towers. |
| **Settlement** | Yes (`Settlement`, extends `Location`) | Villages, cities, tower cities. |
| **Location** | Yes (root type) | Generic places; dungeons, towers, floors, regions. |
| **Ocean, sea, river, lake** | No | Not central to the story. |
| **Mountain, forest, jungle, desert** | No | Not modelled; story focuses on dungeons, towers, villages, guilds. |

So in code we have: **World → Planet**; **Location → Settlement, Dungeon, Tower, DungeonFloor, TowerFloor**. Villages and cities are represented as `Settlement` (with type or naming as needed). We do **not** have separate entity types for universe, galaxy, star, sun, moon, continent, state, town, ocean, sea, river, lake, mountain, forest, jungle, or desert.

---

## 3. Mapping Types to XWEntity Schemas

In code, we usually map a conceptual type to a `schema.name` and define properties for it.  
For example, a **world‑level entity**:

```python
from exonware.xwentity import XWEntity

world_entity = XWEntity(
    schema={
        "name": "bluesmyth.world",
        "type": "object",
        "properties": {
            "world_name": {"type": "string"},
            "era": {"type": "string"},
            "main_threat": {"type": "string"},
            "locations": {"type": "array"},
            "factions": {"type": "array"},
            "guilds": {"type": "array"},
            "characters": {"type": "array"},
            "items": {"type": "array"},
            "parties": {"type": "array"}
        }
    },
    data={
        "world_name": "Blue's Myth",
        "era": "Post‑Demi‑Human War",
        "main_threat": "Runaway dungeons, demon legacies, and human supremacy",
        "locations": [],
        "factions": [],
        "guilds": [],
        "characters": [],
        "items": [],
        "parties": []
    },
    actions={
        "describe_world": {
            "query": {
                "format": "xwqs",
                "query": "SELECT world_name, era, main_threat"
            }
        }
    }
)
```

Similarly, a **character entity**:

```python
character_entity = XWEntity(
    schema={
        "name": "bluesmyth.character",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "race": {"type": "string"},
            "lineage": {"type": "string"},
            "age": {"type": "number"},
            "class": {"type": "string"},
            "roles": {"type": "array"},
            "goals": {"type": "array"}
        }
    },
    data={
        "id": "blue",
        "name": "Blue",
        "race": "Half‑Elf, Half‑Dwarf",
        "lineage": "Elven royal magic knight mother × dwarven hero blacksmith father",
        "age": 12,
        "class": "Blacksmith‑Knight",
        "roles": ["protagonist", "blacksmith", "dungeon_explorer", "party_leader"],
        "goals": [
            "Forge the best weapons from dungeon and tower materials",
            "Rescue his mother from the Elf King",
            "Protect his village and family",
            "Reach the Tree of Life guardian and understand the world's truth"
        ]
    },
    actions={
        "summary": {
            "query": {
                "format": "xwqs",
                "query": "SELECT name, race, class, goals"
            }
        }
    }
)
```

You can repeat this pattern for other types:

- `bluesmyth.Dungeon`
- `bluesmyth.Tower`
- `bluesmyth.AdventurerGuild`
- `bluesmyth.Weapon`
- `bluesmyth.Party`

Each gets:

- A **schema** matching the conceptual type.
- **Data** instances tied to the Blue’s Myth story.
- Optional **actions / queries** (e.g., list Blue’s items, show guild ranks, summarize a dungeon).

---

## 4. How to Use This Example

- **As world‑building reference**  
  Use the taxonomy as a checklist when adding new content: “Is this a Character, Guild, Dungeon, Weapon, Contract, or something else?”

- **As an XWEntity modeling guide**  
  For each conceptual type, decide:
  - `schema.name` (e.g., `bluesmyth.character`, `bluesmyth.dungeon`).
  - Minimal **properties** needed to express it.
  - Helpful **actions** (`xwqs` queries, handlers) to explore and simulate the world.

- **For future extensions**  
  You can:
  - Add more `Story`, `Scene`, or `Event` entities for specific arcs.
  - Model golems, world‑shell battles, or other planets as separate `World` or `Story` entities.

This README is the **narrative + design overview** for the Blue’s Myth XWEntity example. Future Python example files in this folder can directly create entities based on the types described here.

### 4.1 Bluesmyth Lore Explorer (CLI)

The `bluesmyth_explorer.py` script is a CLI tool to browse the world.

**Interactive mode** (no args): runs a loop; type `exit` or `quit` to end.

```bash
python bluesmyth_explorer.py
# bluesmyth> who blue
# bluesmyth> quests
# bluesmyth> exit
```

**One-shot mode** (with args):

```bash
python bluesmyth_explorer.py who blue
python bluesmyth_explorer.py where "Cave of Spilled Crystals"
python bluesmyth_explorer.py quests --status active
python bluesmyth_explorer.py contracts
python bluesmyth_explorer.py world
python bluesmyth_explorer.py characters
python bluesmyth_explorer.py locations
python bluesmyth_explorer.py dungeons
python bluesmyth_explorer.py list character   # lists all; in interactive mode, prompts to select one for details
```

