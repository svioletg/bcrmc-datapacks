from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.theme import Theme


def setup_rich_console() -> Console:
    class Highlighter(RegexHighlighter):
        base_style = 'autohl.'
        highlights = [ # noqa: RUF012
            r'\b(?P<true>True)\b',
            r'\b(?P<false>False)\b',
        ]

    theme = Theme({
        'info': 'cyan',
        'info2': 'bright_cyan',
        'ok': 'bright_green',
        'warn': 'yellow',
        'err': 'red',
        'low': 'grey70',
        'path': 'magenta',
        'path2': 'bright_magenta',
        'ignored_path': 'bright_black',

        'autohl.true': 'green',
        'autohl.false': 'red',
    })

    return Console(
        highlighter=Highlighter(),
        theme=theme,
    )

console: Console = setup_rich_console()
