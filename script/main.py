import yaml
from character import *
from weapon import *
from armor import *
from gamecontroller import GameController

def attack_with_character(source: Character, target: Character):
    print(f'{source.name} attacks {target.name} with a {source.equipped_weapon.name}.')
    attack_roll_base, attack_roll = source.roll_attack()
    is_critical_hit = attack_roll_base == 20
    if is_critical_hit or attack_roll > target.armor_class:
        print(f'{source.name} scored a {"critical hit" if is_critical_hit else "hit"} on {target.name}! '
              f'({attack_roll} > {target.armor_class})')
        damage, damage_type = source.roll_damage(is_critical_hit)
        target.suffer_damage(damage, damage_type, is_critical_hit)
        print(f'{target.name} suffered {damage} {damage_type} damage and is now on {target.hitpoints} HP.')
    else:
        print(f'{source.name} missed ({attack_roll} <= {target.armor_class})')    
    print('------------------------------------------')
    print()

def simulate_fight():

    print('======================================')
    print('A new fight starts...')
    print('======================================')

    c1 = Character()
    c1.name = 'Barbarian'
    c1.equipped_armor_id = 'plate'
    c1.equipped_weapon_id = 'greatsword'
    c1.active_conditions.add(Condition.BLINDED)

    c2 = Character()
    c2.name = 'Monk'
    c2.equipped_armor_id = 'leather'
    c2.equipped_weapon_id = 'quarterstaff'

    source = c1
    target = c2
    while c1.hitpoints > 0 and c2.hitpoints > 0:
        attack_with_character(source, target)
        (source, target) = (target, source)

    winner = c1 if c1.hitpoints != 0 else c2
    loser = c1 if c1.hitpoints == 0 else c2
    print(f'{winner.name} won the fight with {winner.hitpoints} remaining HP.')
    return winner, loser

GameController.load_weapons_and_armors()
winner, loser = simulate_fight()
