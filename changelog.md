# Changelog

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
