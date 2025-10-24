from beet import Context, Function


def fn_give_custom_discs(ctx: Context) -> None:
    ctx.data.functions['bcrmc7:give_custom_discs'] = Function(
        [
            f'give @p minecraft:music_disc_far[minecraft:jukebox_playable="{song}", minecraft:item_model="bcrmc7:music_disc_{song.split(':')[-1]}"]'
            for song in ctx.data.jukebox_songs
        ],
    )
