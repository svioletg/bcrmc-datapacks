execute as @a[scores={bcrmc.DELAY_scaffoldCheck=1..}] run scoreboard players remove @s bcrmc.DELAY_scaffoldCheck 1 
execute as @a[scores={cu.fallDistance=1..}] run tag @s add heightChanged
execute as @a if score @s g.damageTaken > @s last.damageTaken run tag @s add tookDamage
execute as @a if score @s g.damageDealt > @s last.damageDealt run tag @s add dealtDamage
execute as @a if score @s g.deathCount > @s last.deathCount run tag @s add hasDied
execute as @a if score @s cu.fallOneCm > @s last.fallOneCm run tag @s add hasFallen
execute as @a store result score @s cu.fallDistance run data get entity @s FallDistance
execute as @a at @s unless block ~ ~-1 ~ minecraft:air run tag @s add onGround