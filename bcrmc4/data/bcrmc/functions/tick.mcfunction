# Run before main checks
function bcrmc:tick_before

# Track infested blocks as group
execute as @a run scoreboard players operation @s m.infestedBlock += @s m.infestedChiseledStoneBricks
execute as @a run scoreboard players operation @s m.infestedBlock += @s m.infestedCobblestone
execute as @a run scoreboard players operation @s m.infestedBlock += @s m.infestedCrackedStoneBricks
execute as @a run scoreboard players operation @s m.infestedBlock += @s m.infestedDeepslate
execute as @a run scoreboard players operation @s m.infestedBlock += @s m.infestedMossyStoneBricks
execute as @a run scoreboard players operation @s m.infestedBlock += @s m.infestedStone
execute as @a run scoreboard players operation @s m.infestedBlock += @s m.infestedStoneBricks 
execute as @a run scoreboard players operation @s p.infestedBlock += @s p.infestedChiseledStoneBricks
execute as @a run scoreboard players operation @s p.infestedBlock += @s p.infestedCobblestone
execute as @a run scoreboard players operation @s p.infestedBlock += @s p.infestedCrackedStoneBricks
execute as @a run scoreboard players operation @s p.infestedBlock += @s p.infestedDeepslate
execute as @a run scoreboard players operation @s p.infestedBlock += @s p.infestedMossyStoneBricks
execute as @a run scoreboard players operation @s p.infestedBlock += @s p.infestedStone
execute as @a run scoreboard players operation @s p.infestedBlock += @s p.infestedStoneBricks 

#
# Advancement Triggers
#

# Challenges

# Simple score checking
execute as @a[scores={c.musicDisc5=1..}] run advancement grant @s only bcrmc:ch_crafted_disc_five
execute as @a[scores={g.level=50..}] run advancement grant @s only bcrmc:ch_fifty_levels
execute as @a[scores={g.level=100..}] run advancement grant @s only bcrmc:ch_one_hundred_levels
execute as @a[scores={k.wanderingTrader=1..}] run advancement grant @s only bcrmc:egg_trader_killed
execute as @a[scores={m.infestedBlock=1..}] run advancement grant @s only bcrmc:egg_break_infested_block
execute as @a[scores={p.infestedBlock=1..}] run advancement grant @s only bcrmc:egg_get_infested_block

# Fish to height limit advancement
execute at @a as @a[nbt={Inventory:[{id:"minecraft:tropical_fish_bucket"}]},y=319,dy=400] run advancement grant @s only bcrmc:egg_take_fish_high_up

# Worldborder advancement
execute at @a as @a[x=5000,dx=5001] run advancement grant @s only bcrmc:ch_touch_worldborder
execute at @a as @a[x=-5000,dx=-5001] run advancement grant @s only bcrmc:ch_touch_worldborder
execute at @a as @a[z=5000,dz=5001] run advancement grant @s only bcrmc:ch_touch_worldborder
execute at @a as @a[z=-5000,dz=-5001] run advancement grant @s only bcrmc:ch_touch_worldborder

# Maximum damage advancement
execute as @a[tag=dealtDamage] run say Hi
execute as @a[tag=dealtDamage] run scoreboard players operation @s mathResult = @s g.damageDealt
execute as @a[tag=dealtDamage] run scoreboard players operation @s mathResult -= @s last.damageDealt
execute as @a[scores={mathResult=270..}] run advancement grant @s only bcrmc:ch_deal_max_damage

# Fall damage advancements; fall distance is slightly inaccurate, double-check with /tp
execute as @a[tag=!hasDied,tag=tookDamage,tag=hasFallen,scores={last.fallDistance=39..}] run advancement grant @s only bcrmc:ch_survive_long_fall
execute as @a[tag=!hasDied,tag=tookDamage,tag=hasFallen,scores={last.fallDistance=232..}] run advancement grant @s only bcrmc:ch_survive_longer_fall

# Collecting music discs
function bcrmc:disc_check
execute as @a[scores={bcrmc.discs=15..}] run advancement grant @s only bcrmc:ch_all_discs

# Easter Eggs
execute as @a[scores={g.deathCount=100..}] run advancement grant @s only bcrmc:egg_one_hundred_deaths

# Death by falling off scaffolding (OSHA Advancement)
execute as @a at @s if block ~ ~-1 ~ minecraft:scaffolding run tag @s add onScaffolding
execute as @a[tag=onScaffolding] at @s if block ~ ~-1 ~ minecraft:air run scoreboard players set @s bcrmc.DELAY_scaffoldCheck 10
execute as @a[tag=onScaffolding] at @s if block ~ ~-1 ~ minecraft:air run tag @s add wasOnScaffolding
execute as @a[tag=onScaffolding] at @s unless block ~ ~-1 ~ minecraft:scaffolding run tag @s remove onScaffolding
# Grant advancement
execute as @a[tag=heightChanged,tag=hasDied,tag=wasOnScaffolding] run advancement grant @s only bcrmc:egg_fall_off_scaffolding

# Other

# 100% advancement detection
execute as @a if score @s bcrmc.advUnlocked = bcrmc.vars bcrmc.advTotal run advancement grant @s only bcrmc:all_advancements_complete
execute as @a if score @s bcrmc.advUnlocked < bcrmc.vars bcrmc.advTotal run advancement revoke @s only bcrmc:all_advancements_complete

# Run after
function bcrmc:tick_after