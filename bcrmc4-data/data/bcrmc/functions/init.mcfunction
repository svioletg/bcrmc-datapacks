tellraw @a {"text":"[bcrmc4] Initializing!", "color":"gold"}

# Datapack "variables" are stored inside the dummy player "bcrmc.vars"

# Establish advancement counts - for now this must be manually counted
scoreboard objectives add bcrmc.chTotal dummy "BCRMC Total Challenges"
scoreboard players set bcrmc.vars bcrmc.chTotal 8
scoreboard objectives add bcrmc.chComplete dummy "BCRMC Challenges Completed"

scoreboard objectives add bcrmc.eggTotal dummy "BCRMC Total Easter Eggs"
scoreboard players set bcrmc.vars bcrmc.eggTotal 7
scoreboard objectives add bcrmc.eggFound dummy "BCRMC Easter Eggs Found"

scoreboard objectives add bcrmc.advUnlocked dummy "BCRMC Advancements Unlocked"

scoreboard objectives add bcrmc.advTotal dummy "BCRMC Total Advancements"
scoreboard players set bcrmc.vars bcrmc.advTotal 0
scoreboard players operation bcrmc.vars bcrmc.advTotal += bcrmc.vars bcrmc.eggTotal
scoreboard players operation bcrmc.vars bcrmc.advTotal += bcrmc.vars bcrmc.chTotal

# Disc tracking
scoreboard objectives add bcrmc.discs dummy
scoreboard objectives add bcrmc.music_disc_11 dummy
scoreboard objectives add bcrmc.music_disc_13 dummy
scoreboard objectives add bcrmc.music_disc_5 dummy
scoreboard objectives add bcrmc.music_disc_blocks dummy
scoreboard objectives add bcrmc.music_disc_cat dummy
scoreboard objectives add bcrmc.music_disc_chirp dummy
scoreboard objectives add bcrmc.music_disc_far dummy
scoreboard objectives add bcrmc.music_disc_mall dummy
scoreboard objectives add bcrmc.music_disc_mellohi dummy
scoreboard objectives add bcrmc.music_disc_otherside dummy
scoreboard objectives add bcrmc.music_disc_pigstep dummy
scoreboard objectives add bcrmc.music_disc_stal dummy
scoreboard objectives add bcrmc.music_disc_strad dummy
scoreboard objectives add bcrmc.music_disc_wait dummy
scoreboard objectives add bcrmc.music_disc_ward dummy

# Extra variables
scoreboard objectives add bcrmc.DELAY_scaffoldCheck dummy
scoreboard objectives add bcrmc.traveledInOneBreath
scoreboard objectives add mathResult dummy

# Extension for the record every stat pack
scoreboard objectives add c.musicDisc5 minecraft.crafted:minecraft.music_disc_5
scoreboard objectives add cu.fallDistance dummy
scoreboard objectives add m.infestedBlock dummy
scoreboard objectives add p.infestedBlock dummy

# Last tick checks
scoreboard objectives add last.damageDealt dummy
scoreboard objectives add last.damageTaken dummy
scoreboard objectives add last.deathCount dummy
scoreboard objectives add last.fallDistance dummy
scoreboard objectives add last.fallOneCm dummy