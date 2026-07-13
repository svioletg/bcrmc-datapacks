import json
import os
import re
import sys
from collections.abc import Callable
from operator import add, floordiv, mul, sub
from pathlib import Path
from typing import Any

from beet import Advancement, Context, Function, LootTable, Recipe
from loguru import logger

__version__ = 'bcrmc-26.3snap3'

logger.remove()

logger.add(
    sys.stdout,
    level=os.environ.get('BCRMC_LOG_LEVEL', 'INFO'),
    format='<level>[{time:%H:%M:%S} {level}] {message}</level>',
)

DATAPACK_SOURCE: Path = Path('datapack').absolute()
RESOURCE_PACK_SOURCE: Path = Path('resources').absolute()

if not (DATAPACK_SOURCE / 'pack.mcmeta').is_file():
    raise FileNotFoundError(DATAPACK_SOURCE / 'pack.mcmeta')

if not (RESOURCE_PACK_SOURCE / 'pack.mcmeta').is_file():
    raise FileNotFoundError(RESOURCE_PACK_SOURCE / 'pack.mcmeta')

BEET_JSON: dict[str, Any] = json.loads(Path('beet.json').read_text('utf-8'))

WORLDS: list[str] = ['minecraft:overworld', 'minecraft:the_nether', 'minecraft:the_end']

GAMERULES: dict[str, str] = {
    'keep_inventory': 'true',
    'mob_griefing': 'false',
    'fire_spread_radius_around_player': '0',
}

FORLOOP_REGEX: re.Pattern[str] = re.compile(
    r"#for (?P<ivar>\w+) in (?P<items>\w+);(?P<content>.*)#endfor",
    flags=re.DOTALL | re.MULTILINE,
)
EXPR_REGEX: re.Pattern[str] = re.compile(r"{{(?P<expr>.+)}}")

EXPR_MATH_INFIX: dict[str, Callable[[int, int], int]] = {
    '+': add,
    '-': sub,
    '*': mul,
    '/': floordiv,
}

CRITERIA_REGEX: re.Pattern[str] = re.compile(r"(\w+)\.(\w+):(\w+)\.(\w+)")

FLAGGED_CRITERIA: dict[str, str] = {
    criteria:CRITERIA_REGEX.sub('\\2.\\4', criteria)
    for criteria in (
        'minecraft.custom:minecraft.sleep_in_bed',
    )
}

TRIGGERED_FUNCTIONS: dict[str, str] = {
    'bcrmc.version': 'bcrmc:version',
}

MCFUNC_COMMENT_MACRO_PREFIX: str = '#!'

MCFUNC_COMMENT_MACRO_DEFS: dict[str, list[str] | Callable[[Context], str | list[str]]] = {
    'calc_disc_total':
        (lambda ctx:
            f'scoreboard players set $bcrmc bcrmc.CUSTOM_DISCS_TOTAL {len(ctx.data.jukebox_songs)}'),
    'create_criteria_flags': [
        f'scoreboard objectives add bcrmc.criteria_flag.{objname} {criteria}'
        for criteria, objname in FLAGGED_CRITERIA.items()
    ],
    'do_triggered_functions': [
        f'execute as @a[scores={{{trigger}=1..}}] run function {func}'
        + f'\nscoreboard players set @a[scores={{{trigger}=1..}}] {trigger} 0'
        for trigger, func in TRIGGERED_FUNCTIONS.items()
    ],
    'gamerules':
        (lambda ctx:
            [f'tellraw @a {{"text":"[bcrmc] in {world}: gamerule {rule} {state}", "color": "yellow"}}'
            + f'\nexecute in {world} run gamerule {rule} {state}'
            for world in WORLDS for rule, state in GAMERULES.items()]
        ),
    'give_custom_discs':
        (lambda ctx:
            [f'loot give @s loot bcrmc:disc_{resource.split(':')[1]}'
            for resource in ctx.data.jukebox_songs]
        ),
    'register_triggered_functions': [
        f'scoreboard objectives add {trigger} trigger'
        + f'\nscoreboard players enable @a {trigger}'
        for trigger in TRIGGERED_FUNCTIONS
    ],
    'reset_criteria_flags': [
        f'scoreboard players set @a bcrmc.criteria_flag.{objname} 0'
        for _, objname in FLAGGED_CRITERIA.items()
    ],
    'tell_version': [
        f'tellraw @s {{"text": "[bcrmc] datapack version: {__version__}", "color": "yellow"}}',
    ],
    'worldborders': [
        f'execute in {world} run worldborder set 12000'
        for world in WORLDS
    ],
}

def parse_expr(expr: str, context: dict[str, Any]) -> Any:  # noqa: ANN401
    raise NotImplementedError
    if expr.startswith('#'):
        return len(context[expr.removeprefix('#')])
    if ops_in_expr := [op for op in EXPR_MATH_INFIX if op in expr]:
        if len(ops_in_expr) > 1:
            print(f'ERR: Expression can only have one math operator: {expr}')
            return None
        op: str = ops_in_expr[0]
        a, b = (parse_expr(e, context) for e in expr.split(op))
        if (not a) or (not b):
            print(f'ERR: One or both of the operands in this expression are empty: {expr}')
            return None
        return EXPR_MATH_INFIX[op](int(a), int(b))
    return context[expr]

def build_pack_mcmeta(ctx: Context) -> None:
    res, data = ctx.packs

    data.mcmeta.data['pack']['description'] = data.mcmeta.data['pack']['description'].format(version=__version__)
    res.mcmeta.data['pack']['description'] = res.mcmeta.data['pack']['description'].format(version=__version__)

def build_advancements(ctx: Context) -> None:
    adv_copper_oxidation: Advancement = ctx.data.advancements[f'{ctx.project_name}:manual_oxidation']
    adv_copper_oxidation.data['rewards'] = {'recipes': [
        recipe for recipe in ctx.data.recipes if ':oxidize_' in recipe
    ]}

def parse_fn(ctx: Context, mcfunction: Function, name: str | None = None) -> list[str]:
    name = name or '<unknown>'

    parsed: list[str] = []
    for lineno, line in enumerate(mcfunction.lines, 1):
        if not line.startswith(MCFUNC_COMMENT_MACRO_PREFIX):
            # If it's not a macro line, add as is and move on
            parsed.append(line)
            continue

        key = line.removeprefix(MCFUNC_COMMENT_MACRO_PREFIX).strip()

        if not key:
            logger.warning(f'{name}:{lineno}: no macro key given')
            continue

        if key not in MCFUNC_COMMENT_MACRO_DEFS:
            logger.warning(f'{name}:{lineno}: undefined macro: {key}')
            continue

        if isinstance(repl := MCFUNC_COMMENT_MACRO_DEFS[key], Callable):
            logger.debug(f'{name}:{lineno}: processing macro: {key}')
            repl = repl(ctx)
        parsed.append(repl if isinstance(repl, str) else '\n'.join(repl))

    return parsed

def build_functions(ctx: Context) -> None:
    # Parse macros
    for name, mcfunc in ctx.data.functions.items():
        ctx.data.functions[name].lines = parse_fn(ctx, mcfunc, name)

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
                        'minecraft:item_model': f'bcrmc:music_disc_{song}',
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
                        "minecraft:item_model": f"bcrmc:music_disc_{song}",
                    },
                },
                "title":
                    raisebat_title_component if song == 'raisebat' else
                    {"translate": f"advancements.bcrmc.music_disc_{song}.title"}
                ,
                "description": {"translate": f"advancements.bcrmc.music_disc_{song}.description"},
                "show_toast": True,
                "announce_to_chat": False,
                "hidden": True,
            },
            "parent": "bcrmc:root_discs",
            "criteria": {
                "requirement": {
                    "trigger": "minecraft:recipe_unlocked",
                    "conditions": {
                        "recipe": f"bcrmc:music_disc_{song}",
                    },
                },
            },
            "rewards": {
                "recipes": [
                    f"bcrmc:music_disc_{song}",
                ],
            },
        })

        ctx.data.advancements[f'bcrmc:music_disc_{song}'] = adv

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
                ".": "#bcrmc:record_wax",
                "*": f"#bcrmc:valid_for_record_{song}",
            },
            "result": {
                "id": "minecraft:music_disc_far",
                "components": {
                "minecraft:jukebox_playable": f"bcrmc:{song}",
                "minecraft:item_model": f"bcrmc:music_disc_{song}",
                },
            },
            "show_notification": True,
        })

        ctx.data.recipes[f'bcrmc:music_disc_{song}'] = recipe

def main() -> int:
    print(__version__)

    return 0

if __name__ == '__main__':
    sys.exit(main())
