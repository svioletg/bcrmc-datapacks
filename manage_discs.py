import json
import re
from pathlib import Path
from re import Pattern
from typing import Annotated

import colorama
import typer
from colorama import Fore, Style

colorama.init(autoreset=True)

app = typer.Typer()

def highlighted(string: str, fg_color: str, pattern: str | Pattern):
    if isinstance(pattern, str):
        pattern = pattern.replace('.', r"\.")
    return re.sub(pattern, fr"{fg_color}\g<0>{Style.RESET_ALL}", string)

def server_path(server: str) -> dict[str, Path]:
    return {
        'data': Path(server + '-data', 'data', server),
        'res': Path(server + '-resources', 'assets', server)
    }

@app.command()
def show(server: str):
    """Lists every jukebox disc found in data/<namespace>/jukebox_song for the given datapack."""
    cwd = server_path(server)
    discs_found = [*cwd['data'].glob('jukebox_song/*.json')]
    if not discs_found:
        print(f'No discs found in {cwd['data']}')
    else:
        for d in sorted(discs_found):
            print(highlighted(str(d), Fore.CYAN, d.parts[-1]))

@app.command()
def new(server: str,
    name: Annotated[str, typer.Argument(help='OGG file name for this disc.')]
    ):
    """
    Create a new jukebox disc with the given <name>.

    <name> should be the correct file name (not full path!) of an OGG file this disc will play.
    This name will be used for the sound event and any other relevant naming areas.
    """
    cwd = server_path(server)
    print(f'Make sure {name}.ogg will be in mono!\n')
    print('Creating entry in sounds.json...')
    with open(cwd['res'] / 'sounds.json', 'r', encoding='utf-8') as f:
        sounds = json.load(f)
    sounds[f'music_disc.{name}'] = {
        'sounds': [
            {
                'name': f'{server}:records/{name}',
                'attenuation_distance': 16
            }
        ]
    }
    with open(cwd['res'] / 'sounds.json', 'w', encoding='utf-8') as f:
        json.dump(sounds, f, indent=4)

    print('Making jukebox_song JSON...')
    translation = input('Disc description: (Artist - Title) ').strip()
    artist, title = translation.split(' - ')
    with open(cwd['res'] / 'lang/en_us.json', 'r', encoding='utf-8') as f:
        lang_en_us = json.load(f)
    lang_en_us[f'jukebox_song.{server}.{name}'] = translation
    with open(cwd['res'] / 'lang/en_us.json', 'w', encoding='utf-8') as f:
        json.dump(lang_en_us, f, indent=4)

    song_entry = {
        'sound_event': {'sound_id': f'{server}:music_disc.{name}'},
        'description': {'translate': f'jukebox_song.{server}.{name}'},
        'length_in_seconds': float(input('Song length in seconds (float): ')),
        'comparator_output': 10
    }
    with open(cwd['data'] / f'jukebox_song/{name}.json', 'w', encoding='utf-8') as f:
        json.dump(song_entry, f, indent=4)

    print('Preparing custom model...')
    with open(cwd['res'] / 'models/item/music_disc_far.json', 'r', encoding='utf-8') as f:
        base_model = json.load(f)
    exists_flag = False
    for i in base_model['overrides']:
        if i['model'] == f'bcrmc6:item/music_disc_{name}':
            model_number = i['predicate']['custom_model_data']
            exists_flag = True
            break
    if not exists_flag:
        model_number = max(obj['predicate']['custom_model_data'] for obj in base_model['overrides']) + 1
        base_model['overrides'].append({'predicate': {'custom_model_data': model_number}, 'model': f'bcrmc6:item/music_disc_{name}'})

    with open(cwd['res'] / 'models/item/music_disc_far.json', 'w', encoding='utf-8') as f:
        json.dump(base_model, f, indent=4)

    custom_model = {
        'parent': 'minecraft:item/template_music_disc',
        'textures': {
            'layer0': f'bcrmc6:item/music_disc_{name}'
        }
    }

    with open(cwd['res'] / f'models/item/music_disc_{name}.json', 'w', encoding='utf-8') as f:
        json.dump(custom_model, f, indent=4)

    print('Making recipe...')
    items = input('Enter the IDs for every valid item, ' +
        'separated by comma (e.g. item$minecraft:iron_ingot):\n').split(', ')
    tagpaths: dict[str, list[str]] = {}
    for i in items:
        cat, res = i.split('$')
        if cat not in tagpaths:
            tagpaths[cat] = [res]
            continue
        tagpaths[cat].append(res)
    for cat, resources in tagpaths.items():
        for res in resources:
            Path(cwd['data'] / f'tags/{cat}').mkdir(parents=True, exist_ok=True)
            with open(cwd['data'] / f'tags/{cat}/valid_for_record_{name}.json', 'w', encoding='utf-8') as f:
                json.dump({'values': resources}, f, indent=4)
    with open(cwd['data'] / f'recipe/music_disc_{name}.json', 'w', encoding='utf-8') as f:
        json.dump(
            {
                "type": "minecraft:crafting_shaped",
                "pattern": [
                    "...",
                    ".*.",
                    "..."
                ],
                "key": {
                    ".": "minecraft:black_dye",
                    "*": f"#{server}:valid_for_record_{name}"
                },
                "result": {
                    "id": "minecraft:music_disc_far",
                    "components": {
                        "minecraft:jukebox_playable": {
                            "song": f"{server}:{name}",
                            "show_in_tooltip": True
                        },
                        "minecraft:item_model": f"bcrmc6:music_disc_{name}"
                    }
                },
                "show_notification": True
            }, f, indent=4)

    print('Making advancement for recipe unlock...')
    adv_title = input('Advancement title: ')
    with open(cwd['data'] / f'advancement/music_disc_{name}.json', 'w', encoding='utf-8') as f:
        json.dump(
            {
                "display": {
                    "icon": {
                        "id": "minecraft:music_disc_far",
                        "components": {
                            "minecraft:item_model": f"bcrmc6:music_disc_{name}"
                        }
                    },
                    "title": adv_title,
                    "description": f"Crafted the \"{title}\" music disc",
                    "show_toast": True,
                    "announce_to_chat": False,
                    "hidden": True
                },
                "parent": "bcrmc6:root_discs",
                "criteria": {
                    "requirement": {
                        "trigger": "minecraft:recipe_unlocked",
                        "conditions": {
                            "recipe": f"bcrmc6:music_disc_{name}"
                        }
                    }
                }
            }, f, indent=4)
    print('Done!')

if __name__ == '__main__':
    app()
