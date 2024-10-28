execute as @a[tag=wasOnScaffolding,scores={cu.fallDistance=0,bcrmc.DELAY_scaffoldCheck=0}] run tag @s remove wasOnScaffolding
execute as @a[scores={cu.fallDistance=0}] run tag @s remove heightChanged
execute as @a run scoreboard players operation @s last.fallDistance = @s cu.fallDistance
execute as @a if score @s cu.fallOneCm = @s last.fallOneCm run tag @s remove hasFallen
execute as @a run scoreboard players operation @s last.fallOneCm = @s cu.fallOneCm
execute as @a if score @s g.deathCount = @s last.deathCount run tag @s remove hasDied
execute as @a run scoreboard players operation @s last.deathCount = @s g.deathCount
execute as @a if score @s g.damageTaken = @s last.damageTaken run tag @s remove tookDamage
execute as @a run scoreboard players operation @s last.damageTaken = @s g.damageTaken
execute as @a if score @s g.damageDealt = @s last.damageDealt run tag @s remove dealtDamage
execute as @a run scoreboard players operation @s last.damageDealt = @s g.damageDealt
execute as @a at @s if block ~ ~-1 ~ minecraft:air run tag @s remove onGround