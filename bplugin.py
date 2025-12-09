from pathlib import Path

from beet import Advancement, Context, Function, LootTable, Recipe

WORLDS: list[str] = ['minecraft:overworld', 'minecraft:the_nether', 'minecraft:the_end']

GAMERULES: dict[str, str] = {
    'keep_inventory': 'true',
    'mob_griefing': 'false',
    'fire_spread_radius_around_player': '0',
}

def get_mcfunction_path(namespace: str, name: str) -> Path:
    return Path(f'datapack/data/{namespace}/function/{name}.mcfunction')

def build_functions(ctx: Context) -> None:
    ctx.data.functions[f'{ctx.project_name}:gamerules'] = (fn_gamerules := Function())
    for world in WORLDS:
        for rule, state in GAMERULES.items():
            fn_gamerules.lines.append(
                f'tellraw @a {{"text":"{ctx.project_name}: in {world}; gamerule {rule} {state}", "color": "yellow"}}',
            )
            fn_gamerules.lines.append(f'execute in {world} run gamerule {rule} {state}')

    ctx.data.functions[f'{ctx.project_name}:worldborder'] = (fn_worldborder := Function())
    for world in WORLDS:
        fn_worldborder.lines.append(f'execute in {world} run worldborder set 12000')

    ctx.data.functions[f'{ctx.project_name}:give_custom_discs'] = (fn_give_custom_discs := Function())
    for resource in ctx.data.jukebox_songs:
        namespace, song = resource.split(':')
        fn_give_custom_discs.lines.append(f'loot give @p loot {namespace}:disc_{song}')

def make_disc_loot_entries(ctx: Context) -> None:
    for resource in ctx.data.jukebox_songs:
        namespace, song = resource.split(':')

        loot_table = LootTable({
            'pools': [{'rolls': 1, 'entries': [{
                'type': 'minecraft:item',
                'name': 'minecraft:music_disc_far',
                'functions': [{
                    'function': 'set_components',
                    'components': {
                        'minecraft:jukebox_playable': resource,
                        'minecraft:item_model': f'{namespace}:music_disc_{song}',
                    },
                }],
            }]}],
        })

        ctx.data.loot_tables[f'{ctx.project_name}:disc_{song.split(':')[-1]}'] = loot_table

def make_disc_advancements(ctx: Context) -> None:
    raisebat_title_component: list[dict[str, str | bool]] = [
        {"text": "RAISE UP YOUR BAT FOR "},
        {"text": "THE BURNING FIGHT", "strikethrough": True},
        {"text": " BASEBALL DELIGHT", "bold": True},
    ]

    for resource in ctx.data.jukebox_songs:
        namespace, song = resource.split(':')

        adv = Advancement({
            "display": {
                "icon": {
                    "id": "minecraft:music_disc_far",
                    "components": {
                        "minecraft:item_model": f"{namespace}:music_disc_{song}",
                    },
                },
                "title":
                    raisebat_title_component if song == 'raisebat' else
                    {"translate": f"advancements.{namespace}.music_disc_{song}.title"}
                ,
                "description": {"translate": f"advancements.{namespace}.music_disc_{song}.description"},
                "show_toast": True,
                "announce_to_chat": False,
                "hidden": True,
            },
            "parent": f"{namespace}:root_discs",
            "criteria": {
                "requirement": {
                    "trigger": "minecraft:recipe_unlocked",
                    "conditions": {
                        "recipe": f"{namespace}:music_disc_{song}",
                    },
                },
            },
        })

        ctx.data.advancements[f'{namespace}:music_disc_{song}'] = adv

def make_disc_recipes(ctx: Context) -> None:
    for resource in ctx.data.jukebox_songs:
        namespace, song = resource.split(':')

        recipe = Recipe({
            "type": "minecraft:crafting_shaped",
            "pattern": [
                "...",
                ".*.",
                "...",
            ],
            "key": {
                ".": f"#{namespace}:record_wax",
                "*": f"#{namespace}:valid_for_record_{song}",
            },
            "result": {
                "id": "minecraft:music_disc_far",
                "components": {
                "minecraft:jukebox_playable": f"{namespace}:{song}",
                "minecraft:item_model": f"{namespace}:music_disc_{song}",
                },
            },
            "show_notification": True,
        })

        ctx.data.recipes[f'{namespace}:music_disc_{song}'] = recipe
