"""Collection of rules that are used by characters to receive damage."""

from ruleengine import *
from character import *

@rule
class SufferDamage(Rule):
    def when(context: RuleEngine.Context, action: str, value: int):
        return action == 'get_suffered_damage'

    def then(context: RuleEngine.Context, value: int, **kwargs):
        context.result = value

@rule(priority=-1)
class SufferDamageResistance(Rule):
    def when(context: RuleEngine.Context, action: str, character: Character, value: int, damage_type: DamageType):
        return action == 'get_suffered_damage' \
               and damage_type in character.resistances

    def then(context: RuleEngine.Context, value: int, **kwargs):
        context.result = math.floor(value / 2)

@rule(priority=-1)
class SufferDamageImmunity(Rule):
    def when(context: RuleEngine.Context, action: str, character: Character, value: int, damage_type: DamageType):
        return action == 'get_suffered_damage' \
               and damage_type in character.immunities

    def then(context: RuleEngine.Context, **kwargs):
        context.result = 0

@rule(priority=-1)
class SufferDamageVulnerability(Rule):
    def when(context: RuleEngine.Context, action: str, character: Character, value: int, damage_type: DamageType):
        return action == 'get_suffered_damage' \
               and damage_type in character.vulnerabilities

    def then(context: RuleEngine.Context, value: int, **kwargs):
        context.result = value * 2

@rule
class InstantDeathTooMuchDamage(Rule):
    def when(context: RuleEngine.Context, action: str, character: Character, value: int, result: int):
        return action == 'get_suffered_damage' \
               and result >= character.hitpoints + character.max_hitpoints
    
    def then(context: RuleEngine.Context, **kwargs):
        print('The character should die... (instant-death)')

@rule
class FailDeathSaveWhenReceivingDamage(Rule):
    def when(context: RuleEngine.Context, action: str, character: Character):
        return action == 'get_suffered_damage' \
               and character.hitpoints == 0
    
    def then(context: RuleEngine.Context, character: Character, **kwargs):
        num_failures = 2 if context.has_flag('is_critical_hit') else 1
        character.num_death_save_failure += num_failures

@rule
class TooManyFailedDeathSaves(Rule):
    def when(context: RuleEngine.Context, character: Character):
        return character.num_death_save_failure >= 3
    
    def then(context: RuleEngine.Context, **kwargs):
        print('The character should die... (too many death saves failed)')
               