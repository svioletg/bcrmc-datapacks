import typer

import manage_discs

app = typer.Typer()
app.add_typer(manage_discs.app, name='discs', help='Manage jukebox discs.')

if __name__ == '__main__':
    app()
