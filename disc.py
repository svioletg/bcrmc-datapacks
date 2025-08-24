from argparse import ArgumentParser
import json
from pathlib import Path
import sys
from typing import Any

DATA_PATH = Path('bcrmc7-data/data/bcrmc7/')
RES_PATH = Path('bcrmc7-resources/assets/bcrmc7/')

TMPL_DATA_JUKEBOX_SONG: str = """{
    "sound_event": {
        "sound_id": "bcrmc7:music_disc.$NAME"
    },
    "description": {
        "translate": "jukebox_song.bcrmc7.$NAME"
    },
    "length_in_seconds": 0.0,
    "comparator_output": 10
}
"""

TMPL_DATA_RECIPE: str = """{
  "type": "minecraft:crafting_shaped",
  "pattern": [
    "...",
    ".*.",
    "..."
  ],
  "key": {
    ".": "minecraft:black_dye",
    "*": "#bcrmc7:valid_for_record_$NAME"
  },
  "result": {
    "id": "minecraft:music_disc_far",
    "components": {
      "minecraft:jukebox_playable": "bcrmc7:$NAME",
      "minecraft:item_model": "bcrmc7:music_disc_$NAME"
    }
  },
  "show_notification": true
}
"""

TMPL_DATA_ITEM_TAGS: str = """{
    "values": [
    ]
}
"""

TMPL_RES_ITEM: str = """{
    "model": {
        "type": "minecraft:model",
        "model": "bcrmc7:item/music_disc_$NAME"
    }
}
"""

TMPL_RES_MODEL: str = """{
    "parent": "minecraft:item/template_music_disc",
    "textures": {
        "layer0": "bcrmc7:item/music_disc_$NAME"
    }
}
"""

def main() -> int | None:
    parser = ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('description')

    args = parser.parse_args()
    name: str = args.name
    mdname: str = f'music_disc_{name}'
    desc: str = args.description

    input('You should commit before continuing so you can roll back!')

    if (fp := (DATA_PATH / 'jukebox_song' / f'{name}.json')).is_file():
        print(f'Exists: {fp}')
    else:
        fp.touch()
        print(f'Created: {fp}')
        fp.write_text(TMPL_DATA_JUKEBOX_SONG.replace('$NAME', name))

    if (fp := (DATA_PATH / 'recipe' / f'{mdname}.json')).is_file():
        print(f'Exists: {fp}')
    else:
        fp.touch()
        print(f'Created: {fp}')
        fp.write_text(TMPL_DATA_RECIPE.replace('$NAME', name))

    if (fp := (DATA_PATH / 'tags/item' / f'valid_for_record_{name}.json')).is_file():
        print(f'Exists: {fp}')
    else:
        fp.touch()
        print(f'Created: {fp}')
        fp.write_text(TMPL_DATA_ITEM_TAGS)

    if (fp := (RES_PATH / 'items' / f'{mdname}.json')).is_file():
        print(f'Exists: {fp}')
    else:
        fp.touch()
        print(f'Created: {fp}')
        fp.write_text(TMPL_RES_ITEM.replace('$NAME', name))

    with open(RES_PATH / 'lang/en_us.json', 'r', encoding='utf-8') as f:
        lang: dict[str, str] = json.load(f)
    lang[f'jukebox_song.bcrmc7.{name}'] = desc
    with open(RES_PATH / 'lang/en_us.json', 'w', encoding='utf-8') as f:
        json.dump(lang, f, indent=4)

    if (fp := (RES_PATH / 'models/item' / f'{mdname}.json')).is_file():
        print(f'Exists: {fp}')
    else:
        fp.touch()
        print(f'Created: {fp}')
        fp.write_text(TMPL_RES_MODEL.replace('$NAME', name))

    with open(RES_PATH / 'models/item/music_disc_far.json', 'r', encoding='utf-8') as f:
        discmodel: dict[str, Any] = json.load(f)
    highest = max(i['predicate']['custom_model_data'] for i in discmodel['overrides'])
    if not any(i['model'] == f'bcrmc7:item/music_disc_{name}' for i in discmodel['overrides']):
        discmodel['overrides'].append(
            {'predicate': {'custom_model_data': highest + 1}, 'model': f'bcrmc7:item/music_disc_{name}'}
        )
        with open(RES_PATH / 'models/item/music_disc_far.json', 'w', encoding='utf-8') as f:
            json.dump(discmodel, f, indent=4)

    with open(RES_PATH / 'sounds.json', 'r', encoding='utf-8') as f:
        sounds: dict[str, Any] = json.load(f)

    if f'music_disc.{name}' not in sounds:
        sounds[f'music_disc.{name}'] = {'sounds': [{'name': f'bcrmc7:records/{name}', 'attenuation_distance': 16}]}
        with open(RES_PATH / 'sounds.json', 'w', encoding='utf-8') as f:
            json.dump(sounds, f, indent=4)

if __name__ == '__main__':
    sys.exit(main())
