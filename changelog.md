# Changelog

## [bcrmc7-26.3]

### Datapack

- `min_format` and `max_format` are now 11.0
- Haste potion crafting table recipes have been replaced with proper brewing recipes
  - Use cocoa beans to brew

### Resource pack

- `min_format` and `max_format` are now 91.0

## [bcrmc7-2026.01.06] - 2026-01-06

### Datapack

- Added advancement introducing manual copper oxidation (`manual_oxidation`)
  - Unlocks all copper oxidation smelting recipes
- Added advancement introducing Haste potions (`haste_potion`)
  - Unlocks all Potion of Haste recipes
- Changed score checking in function `check_disc_criteria` to use entity selectors instead of `if` tests
- Function `init` now runs on datapack load
- Added "flag" scoreboard objectives for certain triggered criteria
- Added ability to define and parse "comment macros" (lines starting with `#$`) in mcfunction files during the build step in `pack.py`
- Added recipes `potion_haste`, `potion_haste_long`, and `potion_haste_ii`

## [bcrmc7-2025.12.23] - 2025-12-23

### Datapack

- Added advancement criteria to one music disc
  <details>
  <summary>(Secret content spoilers; click to reveal)</summary>

  - `raisebat`: *Raise Up Your Bat*, Toby Fox
    - Now unlocked when granted the "Return to Sender" advancement
  </details>

## [bcrmc7-2025.12.09a] - 2025-12-09

### Datapack

- Fixed custom music disc recipes not being unlocked upon being granted the corresponding advancement
- Fixed recipes mistakenly not being included as a result of missing the recipe build step in `beet.json`

## [bcrmc7-2025.12.09] - 2025-12-09

### Datapack

- 2 new music discs added
  <details>
  <summary>(Secret content spoilers; click to reveal)</summary>

  - `dreams`: *Dreams*, Fleetwood Mac
  - `tickride`: *Ticket To Ride*, The Beatles
  - `yesheart`: *Owner of a Lonely Heart*, Yes
  </details>

- `min_format` and `max_format` changed to 94.1
- Removed functions `jukebox_check`, `jukebox_click`, and `jukebox_raycast`
- Updated gamerule names per 25w44a changes
  - `doFireTick` removed, added rule for `fire_spread_radius_around_player`
- Custom music disc recipes now use the `#bcrmc7:record_wax` tag for the border item instead of only Black Dye
  - Dried Kelp added to the `#bcrmc7:record_wax` tag
- Loot table entries have been added for all custom music discs, for consistent usage
- Certain custom music discs can now have their recipes unlocked by meeting secret criteria instead of only crafting the disc
- Custom music disc advancements, loot table entries, and recipes are now generated with [`beet`](https://github.com/mcbeet/beet/)

### Resource pack

- `max_format` changed to 75.0
- Remove `music_disc_far` item model, no longer necessary to override it
- Added `lang/en_us.json` entries for advancement titles and descriptions

## [bcrmc7-2025.10.10a] - 2025-10-10

### Datapack

- Re-added advancements for crafting hidden music discs
  - New advancements added for the 7 new music discs added in `bcrmc7-2025.08.30`

## [bcrmc7-2025.10.10] - 2025-10-10

Tested and working for 1.21.10.

### Datapack
- `max_format` bumped to 69.0

### Resource pack
- `max_format` bumped to 88.0

## [bcrmc7-2025.08.30a] - 2025-08-30

Tested and working with version 25w35a.

### Datapack

- Pack format changed to 85.0
  - Accordingly, `"pack_format"` field replaced with `"min_format"` and `"max_format"`
- Added oxidation smelting recipes for:
  - Copper Bars (`copper_bars`)
  - Copper Chain (`copper_chain`)
  - Copper Chest (`copper_chest`)
  - Copper Golem Statue (`copper_golem_statue`)
  - Copper Lantern (`copper_lantern`)

## [bcrmc7-2025.08.30] - 2025-08-30

Tested and working with 1.21.8 and 25w35a.

- 7 new jukebox song entries
- Music disc lore is no longer hidden before playing
- Advancements related to playing discs have been removed
