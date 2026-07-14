from typing import Literal

from pydantic import BaseModel

type ItemModifier = ItemModifierCopyName | ItemModifierSetComponents
type TextComponent = dict # TODO: create TextComponent model
type Predicate = dict # TODO: create Predicate model

class Icon(BaseModel):
    id: str
    count: int = 1
    components: dict

class AdvancementDisplay(BaseModel):
    icon: Icon
    title: TextComponent
    description: TextComponent
    frame: Literal['challenge', 'goal', 'task'] = 'task'
    background: str
    show_toast: bool = True
    announce_to_chat: bool = True
    hidden: bool = False

# Definition sourced from: https://minecraft.wiki/w/Advancement_definition#File_format
class Advancement(BaseModel):
    parent: str | None = None
    display: AdvancementDisplay
    criteria: dict[str, 'Criterion']
    requirements: list[list[str]] | None = None
    rewards: ... # TODO
    sends_telemetry_event: bool = False

class Criterion(BaseModel):
    trigger: str
    conditions: ... # TODO

# Definition sourced from: https://minecraft.wiki/w/Item_modifier#Format
class ItemModifierBase(BaseModel):
    function: str
    conditions: list[Predicate] = []

class ItemModifierCopyName(ItemModifierBase):
    function: Literal['copy_name'] = 'copy_name'
    source: Literal[
        'block_entity',
        'this',
        'attacking_entity',
        'last_damage_player',
        'direct_attacker',
        'target_entity',
        'interacting_entity',
    ]

class ItemModifierSetComponents(ItemModifierBase):
    function: Literal['set_components'] = 'set_components'
    components: dict[str, str]

# Definition sourced from: https://minecraft.wiki/w/Loot_table#Entry
class LootEntry(BaseModel):
    type: str
    conditions: list[Predicate] = []
    functions: list[ItemModifier] = []
    weight: int = 1
    quality: int = 0
    name: str
    # TODO: not bothering with the othres for now

# Definition sourced from: https://minecraft.wiki/w/Loot_table#Pool
class LootPool(BaseModel):
    conditions: list[Predicate] = []
    functions: list[ItemModifier] = []
    rolls: int
    bonus_rolls: float = 0.0
    entries: list[LootEntry]

# Definition sourced from: https://minecraft.wiki/w/Loot_table#Format
class LootTable(BaseModel):
    type: str = 'generic'
    functions: list[ItemModifier] = []
    pools: list[LootPool] = []

# Definition sourced from: https://minecraft.wiki/w/Sounds.json
class Sound(BaseModel):
    name: str
    """The path to this sound file from the `<namespace>/sounds` folder (excluding the .ogg file extension)."""
    volume: float = 1.0
    pitch: float = 1.0
    weight: int = 1
    stream: bool = True
    attenuation_distance: int = 16
    preload: bool = False
    type: Literal['file', 'event'] = 'file'

# Definition sourced from: https://minecraft.wiki/w/Sounds.json
class SoundEvent(BaseModel):
    replace: bool = False
    subtitle: str
    sounds: list[str | Sound]

# Definition sourced from: https://minecraft.wiki/w/Jukebox_song_definition
class JukeboxSong(BaseModel):
    sound_event: str | SoundEvent
    """Sound event ID or object. Only vanilla sound events can be referenced by ID."""
    description: str | TextComponent
    length_in_seconds: float
    comparator_output: int = 15
