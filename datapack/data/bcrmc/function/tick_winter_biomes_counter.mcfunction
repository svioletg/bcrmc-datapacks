execute as @a at @s run execute if biome ~ ~ ~ #bcrmc:winter_biomes run return run scoreboard players add @s bcrmc.ticks_in_winter 1
execute as @a at @s run execute unless biome ~ ~ ~ #bcrmc:winter_biomes run return run scoreboard players set @s bcrmc.ticks_in_winter 0
