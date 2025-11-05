from typing import Literal

from pydantic import BaseModel

type TextComponent = dict

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
