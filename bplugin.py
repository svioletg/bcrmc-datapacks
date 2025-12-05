import json
from pathlib import Path

from beet import Context, Function, LootTable

from util import Maybe

WORLDS: list[str] = ['minecraft:overworld', 'minecraft:the_nether', 'minecraft:the_end']

GAMERULES: dict[str, str] = {
    'keep_inventory': 'true',
    'mob_griefing': 'false',
    'fire_spread_radius_around_player': '0',
}

def mcfunction_path(namespace: str, name: str) -> Path:
    return Path(f'datapack/data/{namespace}/function/{name}.mcfunction')

def build_functions(ctx: Context) -> None:
    namespace: str = ctx.project_name

    ctx.data.functions[f'{namespace}:gamerules'] = (fn_gamerules := Function())
    for world in WORLDS:
        for rule, state in GAMERULES.items():
            fn_gamerules.lines.append(
                f'tellraw @a {{"text":"{namespace}: in {world}; gamerule {rule} {state}", "color": "yellow"}}',
            )
            fn_gamerules.lines.append(f'execute in {world} run gamerule {rule} {state}')

    ctx.data.functions[f'{namespace}:worldborder'] = (fn_worldborder := Function())
    for world in WORLDS:
        fn_worldborder.lines.append(f'execute in {world} run worldborder set 12000')

    ctx.data.functions[f'{namespace}:give_custom_discs'] = (fn_give_custom_discs := Function())
    for song in ctx.data.jukebox_songs:
        fn_give_custom_discs.lines.append(
            f'give @p minecraft:music_disc_far[minecraft:jukebox_playable="{song}",'
            + f'minecraft:item_model="{namespace}:music_disc_{song.split(':')[-1]}"]',
        )

def make_disc_loot_entries(ctx: Context) -> None:
    for song in ctx.data.jukebox_songs:
        loot_table = LootTable({
            'pools': [{'rolls': 1, 'entries': [{
                'type': 'minecraft:item',
                'name': 'minecraft:music_disc_far',
                'functions': [{
                    'function': 'set_components',
                    'components': {
                        'minecraft:jukebox_playable': song,
                    },
                }],
            }]}],
        })
        ctx.data.loot_tables[f'{ctx.project_name}:disc_{song.split(':')[-1]}'] = loot_table
