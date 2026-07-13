import json
import re
import sys
from collections.abc import Callable
from operator import add, floordiv, mul, sub
from pathlib import Path
from typing import Any

from beet import Advancement, Context, Function, LootTable, Recipe
from loguru import logger

__version__ = 'bcrmc7-26.3snap3'

logger.remove()

logger.add(sys.stdout, level='INFO', format='<level>[{time:%H:%M:%S} {level}] {message}</level>')

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

MCFUNC_COMMENT_MACRO_PREFIX: str = '#$'

MCFUNC_COMMENT_MACRO_DEFS: dict[str, str | list[str] | Callable[[Context], str | list[str]]] = {
    'calc_disc_total':
        (lambda ctx:
            f'scoreboard players set $bcrmc bcrmc.CUSTOM_DISCS_TOTAL {len(ctx.data.jukebox_songs)}'),
    'create_criteria_flags': [
        f'scoreboard objectives add bcrmc.criteria_flag.{objname} {criteria}'
        for criteria, objname in FLAGGED_CRITERIA.items()
    ],
    'reset_criteria_flags': [
        f'scoreboard players set @a bcrmc.criteria_flag.{objname} 0'
        for _, objname in FLAGGED_CRITERIA.items()
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

def build_advancements(ctx: Context) -> None:
    adv_copper_oxidation: Advancement = ctx.data.advancements[f'{ctx.project_name}:manual_oxidation']
    adv_copper_oxidation.data['rewards'] = {'recipes': [
        recipe for recipe in ctx.data.recipes if ':oxidize_' in recipe
    ]}

def build_functions(ctx: Context) -> None:
    def parse_fn(mcfunction: Function) -> list[str]:
        parsed: list[str] = []
        for line in mcfunction.lines:
            if not line.startswith(MCFUNC_COMMENT_MACRO_PREFIX):
                parsed.append(line)
                continue
            key = line.removeprefix('#$')
            if key not in MCFUNC_COMMENT_MACRO_DEFS:
                logger.warning(f'Undefined: {key}')
                continue
            if isinstance(repl := MCFUNC_COMMENT_MACRO_DEFS[key], Callable):
                repl = repl(ctx)
            parsed.append(repl if isinstance(repl, str) else '\n'.join(repl))
        return parsed

    # init
    fn_init: Function = ctx.data.functions[f'{ctx.project_name}:init']
    fn_init.lines = parse_fn(fn_init)

    # tick
    fn_tick: Function = ctx.data.functions[f'{ctx.project_name}:tick']
    fn_tick_built: list[str] = []
    for ln in fn_tick.lines:
        if ln.startswith('#$reset_criteria_flags'):
            fn_tick_built.append(ln.replace(
                '#$reset_criteria_flags',
                '\n'.join(
                    f'scoreboard players set @a bcrmc.criteria_flag.{objname} 0'
                    for _, objname in FLAGGED_CRITERIA.items()
                ),
            ))
            continue
        fn_tick_built.append(ln)
    fn_tick.lines = fn_tick_built.copy()

    # gamerules
    ctx.data.functions[f'{ctx.project_name}:gamerules'] = (fn_gamerules := Function())
    for world in WORLDS:
        for rule, state in GAMERULES.items():
            fn_gamerules.lines.append(
                f'tellraw @a {{"text":"{ctx.project_name}: in {world}; gamerule {rule} {state}", "color": "yellow"}}',
            )
            fn_gamerules.lines.append(f'execute in {world} run gamerule {rule} {state}')

    # worldborder
    ctx.data.functions[f'{ctx.project_name}:worldborder'] = (fn_worldborder := Function())
    for world in WORLDS:
        fn_worldborder.lines.append(f'execute in {world} run worldborder set 12000')

    # give_custom_discs
    ctx.data.functions[f'{ctx.project_name}:give_custom_discs'] = (fn_give_custom_discs := Function())
    for resource in ctx.data.jukebox_songs:
        namespace, song = resource.split(':')
        fn_give_custom_discs.lines.append(f'loot give @p loot bcrmc:disc_{song}')

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
