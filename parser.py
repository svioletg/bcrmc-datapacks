from collections.abc import Callable

from beet import Context, Function

from const import FLAGGED_CRITERIA, logger

#region COMMENT MACROS

MCFUNC_COMMENT_MACRO_PREFIX: str = '#>'

def macro_calc_disc_total(ctx: Context) -> str:
    return f'scoreboard players set $bcrmc7 bcrmc7.CUSTOM_DISCS_TOTAL {len(ctx.data.jukebox_songs)}'

def macro_create_criteria_flags(ctx: Context) -> list[str]:
    return [
        f'scoreboard objectives add bcrmc7.criteria_flag.{objname} {criteria}'
        for criteria, objname in FLAGGED_CRITERIA.items()
    ]

def macro_reset_criteria_flags(ctx: Context) -> list[str]:
    return [
        f'scoreboard players set @a bcrmc7.criteria_flag.{objname} 0'
        for _, objname in FLAGGED_CRITERIA.items()
    ]

MACRO_FUNCS: dict[str, Callable[[Context], str | list[str]]] = {
    name.removeprefix('macro_'):fn for name, fn in globals().items() if name.startswith('macro_')
}

def parse_comment_macro(line: str, ctx: Context) -> str:
    """Parses a comment expression (an mcfunction comment starting with `#>`) and returns the content to replace it."""
    key = line.removeprefix(MCFUNC_COMMENT_MACRO_PREFIX)
    if not (fn := MACRO_FUNCS.get(key.removeprefix('macro_'))):
        logger.warning(f'Undefined macro {key} from line: {line}')
        return line
    repl: str | list[str] = fn(ctx)
    return repl if isinstance(repl, str) else '\n'.join(repl)

#endregion COMMENT MACROS

def parse_fn(ctx: Context, mcfunction: Function) -> list[str]:
    parsed: list[str] = []
    for line in mcfunction.lines:
        if line.startswith(MCFUNC_COMMENT_MACRO_PREFIX):
            parsed.append(parse_comment_macro(line, ctx))
            continue
        # Append original line if nothing to parse
        parsed.append(line)
    return parsed
