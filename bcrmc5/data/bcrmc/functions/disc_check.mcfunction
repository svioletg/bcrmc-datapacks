execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_11"}] run scoreboard players set @s bcrmc.music_disc_11 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_13"}] run scoreboard players set @s bcrmc.music_disc_13 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_5"}] run scoreboard players set @s bcrmc.music_disc_5 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_blocks"}] run scoreboard players set @s bcrmc.music_disc_blocks 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_cat"}] run scoreboard players set @s bcrmc.music_disc_cat 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_chirp"}] run scoreboard players set @s bcrmc.music_disc_chirp 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_far"}] run scoreboard players set @s bcrmc.music_disc_far 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_mall"}] run scoreboard players set @s bcrmc.music_disc_mall 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_mellohi"}] run scoreboard players set @s bcrmc.music_disc_mellohi 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_otherside"}] run scoreboard players set @s bcrmc.music_disc_otherside 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_pigstep"}] run scoreboard players set @s bcrmc.music_disc_pigstep 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_stal"}] run scoreboard players set @s bcrmc.music_disc_stal 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_strad"}] run scoreboard players set @s bcrmc.music_disc_strad 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_wait"}] run scoreboard players set @s bcrmc.music_disc_wait 1
execute as @a if data entity @s Inventory[{id:"minecraft:music_disc_ward"}] run scoreboard players set @s bcrmc.music_disc_ward 1

execute as @a run scoreboard players set @s bcrmc.discs 0
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_11
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_13
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_5
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_blocks
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_cat
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_chirp
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_far
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_mall
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_mellohi
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_otherside
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_pigstep
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_stal
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_strad
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_wait
execute as @a run scoreboard players operation @s bcrmc.discs += @s bcrmc.music_disc_ward