execute as @a at @s run execute if biome ~ ~ ~ minecraft:dappled_forest run return run scoreboard players add @s bcrmc.ticks_in_autumn 1
execute as @a at @s run execute unless biome ~ ~ ~ minecraft:dappled_forest run return run scoreboard players set @s bcrmc.ticks_in_autumn 0
