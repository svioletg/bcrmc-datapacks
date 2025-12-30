import re

from loguru import logger

logger.remove()

WORLDS: list[str] = ['minecraft:overworld', 'minecraft:the_nether', 'minecraft:the_end']

GAMERULES: dict[str, str] = {
    'keep_inventory': 'true',
    'mob_griefing': 'false',
    'fire_spread_radius_around_player': '0',
}

CRITERIA_REGEX: re.Pattern[str] = re.compile(r"(\w+)\.(\w+):(\w+)\.(\w+)")

FLAGGED_CRITERIA: dict[str, str] = {
    criteria:CRITERIA_REGEX.sub('\\2.\\4', criteria)
    for criteria in (
        'minecraft.custom:minecraft.sleep_in_bed',
    )
}
