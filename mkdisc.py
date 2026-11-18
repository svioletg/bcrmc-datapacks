import json
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from collections.abc import Callable, Iterable
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Literal, Never, Self, overload
from warnings import warn

from loguru import logger
from more_itertools import one

from const import console
from errors import KeyExistsError, WrongFileSuffixError, WrongFileSuffixWarning
from models import JukeboxSong
from pack import DATAPACK_SOURCE, RESOURCE_PACK_SOURCE
from util import FFprobeStream, asserts, expect

AUDIO_FORMATS: tuple[str, ...] = ('.wav', '.ogg', '.mp3')
TEXTURE_FORMATS: tuple[str, ...] = ('.png',)

DPACK_ITEM_TAGS_DIR: Path = DATAPACK_SOURCE / 'data/bcrmc/tags/item/'
DPACK_JUKEBOX_SONG_DIR: Path = DATAPACK_SOURCE / 'data/bcrmc/jukebox_song/'

RPACK_ITEM_MODELS_DIR: Path = RESOURCE_PACK_SOURCE / 'assets/bcrmc/models/item/'
RPACK_ITEMS_DIR: Path = RESOURCE_PACK_SOURCE / 'assets/bcrmc/items/'
RPACK_LANG_DIR: Path = RESOURCE_PACK_SOURCE / 'assets/bcrmc/lang/'
RPACK_SOUNDS_DIR: Path = RESOURCE_PACK_SOURCE / 'assets/bcrmc/sounds/records/'
RPACK_SOUNDS_JSON: Path = RESOURCE_PACK_SOURCE / 'assets/bcrmc/sounds.json'
RPACK_TEXTURE_DIR: Path = RESOURCE_PACK_SOURCE / 'assets/bcrmc/textures/item/'

def abort(msg: str, status: int = 1) -> Never:
    console.print(f'[err]{msg}[/]')

    raise SystemExit(status)

@overload
def arg_type_comma_list(s: str, coerce: None = None) -> list[str]: ...
@overload
def arg_type_comma_list[T](s: str, coerce: Callable[[str], T]) -> list[T]: ...
def arg_type_comma_list[T](s: str, coerce: Callable[[str], T] | None = None) -> list[T]:
    return [coerce(i.strip()) for i in s.split(',')] if coerce else [i.strip() for i in s.split(',')]  # ty: ignore[invalid-explicit-return]

def arg_validator_filetype(types: Iterable[str]) -> Callable[[str], Path]:
    def _validate_arg(argval: str) -> Path:
        fp = Path(argval)
        if not fp.is_file():
            abort(f'error: file not found: {fp}')

        if fp.suffix not in types:
            abort(f'error: file type must be one of {types}: {fp}')

        return fp

    return _validate_arg

def get_duration(audio_file: str | Path) -> float:
    return expect(
        one(FFprobeStream.from_file(audio_file)).duration,
        f'Failed to get duration from file: {audio_file}',
    )

def to_ogg(
        audio_file: str | Path,
        *,
        mono: bool = True,
        sample_rate: int = 44100,
        overwrite: bool = False,
        wrong_suffix: Literal['warn', 'raise', 'pass'] = 'warn',
    ) -> Path:
    """Converts an audio file to OGG vorbis, returning the new file's path.

    If the file is already in OGG vorbis format, the path is returned unchanged and no conversion is done.

    :param wrong_suffix: What to do when the file's existing suffix is not ``.ogg``, but the file is in OGG vorbis
        format. ``'warn'`` emits :class:`WrongFileSuffixWarning`, ``'raise'`` raises :class:`WrongFileSuffixError`,
        ``'pass'`` does nothing.
    """
    audio_file = Path(audio_file)

    if not (ffmpeg_bin := shutil.which('ffmpeg')):
        raise FileNotFoundError("ffmpeg is not on the system's path")

    if one(FFprobeStream.from_file(audio_file)).codec_name == 'vorbis':
        if (audio_file.suffix != '.ogg') and (wrong_suffix != 'pass'):
            msg: str = f'File is in OGG vorbis format but suffix is not .ogg: {audio_file}'
            match wrong_suffix:
                case 'warn':
                    warn(WrongFileSuffixWarning(msg), stacklevel=2)
                case 'raise':
                    raise WrongFileSuffixError(msg)
                case _:
                    raise ValueError(f'Expected "warn", "raise", or "pass" for argument wrong_suffix: {wrong_suffix!r}')

        return audio_file

    dest: Path = audio_file.with_suffix('.ogg')
    proc = subprocess.run(  # noqa: S603
        (
            ffmpeg_bin, '-hide_banner', '-y' if overwrite else '-n',
            '-i', str(audio_file),
            '-c:a', 'libvorbis',
            *(('-ac', '1') if mono else ()),
            '-ar', str(sample_rate),
            str(dest),
        ),
        capture_output=True,
        check=False,
    )

    if proc.returncode != 0:
        console.print(f'FFmpeg returned non-zero exit code: {proc.returncode}')
        console.print('----- captured stderr -----')
        console.print(proc.stderr.decode('utf-8'))
        console.print('---------------------------')
        raise subprocess.CalledProcessError(proc.returncode, proc.args)

    asserts(dest.is_file(), FileNotFoundError(dest))

    return dest

@dataclass
class DiscTranslations:
    advancement_title: str
    advancement_description: str
    song_title: str

@dataclass
class DiscData:
    rid: str
    """Resource ID for this music disc and its related data."""
    audio_src: Path
    item: dict[str, Any]
    item_tag: dict[str, Any]
    """Content for the ``#valid_for_record_<name>`` item tag."""
    item_model: dict[str, Any]
    jukebox_song: dict[str, Any]
    sound_event: dict[str, Any]
    texture_src: Path
    translations: dict[str, dict[str, str]]

    @classmethod
    def make_data(cls,
            rid: str,
            *,
            audio_src: Path | str,
            texture_src: Path | str,
            recipe_items: list[str],
            trans: dict[str, DiscTranslations],
        ) -> Self:
        """Make data for a new record.

        :param rid: Resource ID for this disc.
        :param audio_src: Path to the audio file to use for this disc. If it is not already in OGG vorbis format, a
            converted copy of it is made.
        :param texture_src: Path to the texture file to use for this disc.
        :param recipe_items: A list of items that are valid as the middle item for this disc's recipe.
        :param trans: A dictionary of language strings (e.g. ``en_us``) to :class:`DiscTranslations` objects.
        """
        audio_src = Path(audio_src)
        texture_src = Path(texture_src)

        audio_src = to_ogg(audio_src, overwrite=True)

        translations: dict[str, dict[str, str]] = {
            lang: {
                f'advancements.bcrmc.music_disc_{rid}.title': tr.advancement_title,
                f'advancements.bcrmc.music_disc_{rid}.description': tr.advancement_description,
                f'jukebox_song.bcrmc.{rid}': tr.song_title,
            }
            for lang, tr in trans.items()
        }

        item: dict[str, Any] = {
            'model': {
                'type': 'minecraft:model',
                'model': f'bcrmc:item/music_disc_{rid}',
            },
        }

        item_model: dict[str, Any] = {
            'parent': 'minecraft:item/template_music_disc',
            'textures': {
                'layer0': f'bcrmc:item/music_disc_{rid}',
            },
        }

        item_tag: dict[str, Any] = {
            'values': recipe_items,
        }

        sound_event: dict[str, list[dict[str, Any]]] = {
            'sounds': [
                {
                    'name': f'bcrmc:records/{rid}',
                    'attenuation_distance': 16,
                },
            ],
        }

        jukebox_song: dict[str, Any] = JukeboxSong(
            sound_event={'sound_id': f'bcrmc:music_disc.{rid}'},
            description={'translate': f'jukebox_song.bcrmc.{rid}'},
            length_in_seconds=get_duration(audio_src),
        ).model_dump(mode='python')

        return cls(
            rid=rid,
            audio_src=audio_src,
            item=item,
            item_tag=item_tag,
            item_model=item_model,
            jukebox_song=jukebox_song,
            sound_event=sound_event,
            texture_src=Path(texture_src),
            translations=translations,
        )

    def put(self, *, key_exist_ok: bool = False, file_exist_ok: bool = False) -> None:  # noqa: PLR0915
        """Writes this disc data to disk in the relevant locations.

        :param key_exist_ok: Whether to overwrite existing keys in JSON data regarding this disc. If ``False``,
            :class:`KeyError` is raised in this case.
        :param file_exist_ok: Whether to overwrite existing files. If ``False``, :class:`FileExistsError` is raised in
            this case.
        """
        def _check_file_exists(fp: Path) -> None:
            if fp.exists():
                if not file_exist_ok:
                    raise FileExistsError(fp)

                logger.warning(f'Overwriting file {fp}')

        audio_dest: Path = RPACK_SOUNDS_DIR / (self.rid + '.ogg')
        texture_dest: Path = RPACK_TEXTURE_DIR / f'music_disc_{self.rid}.png'

        # Audio file
        logger.info(f'Copying: {self.audio_src} -> {audio_dest}')
        try:
            shutil.copy(self.audio_src, audio_dest)
        except shutil.SameFileError:
            logger.info('audio_src is already at the expected destination, no copying done')

        # Texture file
        logger.info(f'Copying: {self.texture_src} -> {texture_dest}')
        try:
            shutil.copy(self.texture_src, texture_dest)
        except shutil.SameFileError:
            logger.info('texture_src is already at the expected destination, no copying done')

        # Jukebox JSON
        jukebox_json_dest: Path = DPACK_JUKEBOX_SONG_DIR / (self.rid + '.json')
        logger.info(f'Writing jukebox song data to {jukebox_json_dest}')

        _check_file_exists(jukebox_json_dest)

        with open(jukebox_json_dest, 'w', encoding='utf-8') as f:
            json.dump(self.jukebox_song, f, indent=4)

        # Item tag JSON
        item_tag_json_dest: Path = DPACK_ITEM_TAGS_DIR / f'valid_for_record_{self.rid}.json'
        logger.info(f'Writing recipe item tag data to {item_tag_json_dest}')

        _check_file_exists(item_tag_json_dest)

        with open(item_tag_json_dest, 'w', encoding='utf-8') as f:
            json.dump(self.item_tag, f, indent=4)

        # Item JSON
        item_json_dest: Path = RPACK_ITEMS_DIR / f'music_disc_{self.rid}.json'
        logger.info(f'Writing item data to {item_json_dest}')

        _check_file_exists(item_json_dest)

        with open(item_json_dest, 'w', encoding='utf-8') as f:
            json.dump(self.item, f, indent=4)

        # Item model JSON
        item_model_json_dest: Path = RPACK_ITEM_MODELS_DIR / f'music_disc_{self.rid}.json'
        logger.info(f'Writing item model data to {item_model_json_dest}')

        _check_file_exists(item_model_json_dest)

        with open(item_model_json_dest, 'w', encoding='utf-8') as f:
            json.dump(self.item_model, f, indent=4)

        # sounds.json
        sound_event_key: str = f'music_disc.{self.rid}'
        logger.info(f'Adding sound event "{sound_event_key}" to sounds.json')

        with open(RPACK_SOUNDS_JSON, 'r', encoding='utf-8') as f:
            sounds_json: dict[str, Any] = json.load(f)

        if sound_event_key in sounds_json:
            if not key_exist_ok:
                raise KeyExistsError(f'Key already exists in {RPACK_SOUNDS_JSON}: {sound_event_key}')

            logger.warning(f'Overwriting existing key "{sound_event_key}" in {RPACK_SOUNDS_JSON}')

        sounds_json[sound_event_key] = self.sound_event

        with open(RPACK_SOUNDS_JSON, 'w', encoding='utf-8') as f:
            json.dump(sounds_json, f, indent=4)

        # Translations
        for lang, tr in self.translations.items():
            lang_json_dest: Path = RPACK_LANG_DIR / (lang + '.json')
            logger.info(f'Updating translations for {lang_json_dest}')

            lang_json: dict[str, Any]
            if lang_json_dest.exists():
                with open(lang_json_dest, 'r', encoding='utf-8') as f:
                    lang_json = json.load(f)
            else:
                lang_json = {}

            for k, v in tr.items():
                if k in lang_json:
                    if not key_exist_ok:
                        raise KeyExistsError(f'Key already exists in {lang_json_dest}: {k}')

                    logger.warning(f'Overwriting existing key "{k}" in {lang_json_dest}')

                lang_json[k] = v

            with open(lang_json_dest, 'w', encoding='utf-8') as f:
                json.dump(lang_json, f, indent=4)

def main() -> int:
    parser = ArgumentParser()
    parser.add_argument('name', type=str, help='Resource name of this disc')

    parser.add_argument('--audio', type=arg_validator_filetype(AUDIO_FORMATS), required=True,
        help='Audio file to use for this disc.')
    parser.add_argument('--texture', type=arg_validator_filetype(TEXTURE_FORMATS), required=True,
        help='Texture to use for this disc.')
    parser.add_argument('--items', type=arg_type_comma_list, required=True,
        help='Comma-separated list of center items that can be used to craft this disc.')

    parser.add_argument('-y', action='store_true', dest='overwrite',
        help='Overwrite existing files.')

    for fld in fields(DiscTranslations):
        parser.add_argument(f'--tr-{fld.name.replace('_', '-')}', dest=f'tr_{fld.name}', type=str)

    args = parser.parse_args()

    name: str = args.name
    audio_src: Path = args.audio
    texture_src: Path = args.texture
    recipe_items: list[str] = args.items
    overwrite: bool = args.overwrite

    console.print('Making disc data...')

    disc_data: DiscData = DiscData.make_data(
        name,
        audio_src=audio_src,
        texture_src=texture_src,
        trans={
            'en_us':
                DiscTranslations(
                    **{k.removeprefix('tr_'):v for k, v in args.__dict__.items() if k.startswith('tr_')},
                ),
        },
        recipe_items=recipe_items,
    )

    console.print('Writing to packs...')

    disc_data.put(key_exist_ok=overwrite, file_exist_ok=overwrite)

    console.print('Done!')

    return 0

if __name__ == '__main__':
    sys.exit(main())
