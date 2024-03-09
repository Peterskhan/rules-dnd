"""Collection of rules that are used to calculate the armor class of a character."""

from ruleengine import *
from character import *

@rule
class RollAbilityCheck(Rule):
    """When rolling an ability check we roll a 1d20 and add a modifier."""

    def when(context: RuleEngine.Context, actions: List, character: Character, ability: Ability) -> bool:
        return 'roll_ability_check' in actions

    def then(context: RuleEngine.Context, character: Character, ability: Ability, **kwargs) -> None:
        context.update('result', character.roll_ability_check(ability))
        context.set_flag('rolled_ability_check')

@rule
class RollSkillCheck(Rule):
    pass

@rule
class StealthCheckDisadvantageFromArmor(Rule):
    """When the character wears unstealthy armor, it has disadvantage on stealth checks."""

    def when(context: RuleEngine.Context, actions: List, skill: Skill, character: Character):
        return 'roll_skill_check' in actions \
               and skill == Skill.STEALTH \
               and character.equipped_armor is not None \
               and character.equipped_armor.has_stealth_disadvantage

    def then(context: RuleEngine.Context, **kwargs):
        context.set_flag('has_disadvantage')
        
@rule
class RollInitiative(Rule):
    """When rolling initiative we roll a dexterity check."""

    def when(context: RuleEngine.Context, actions: List) -> bool:
        return 'roll_initiative' in actions
    
    def then(context: RuleEngine.Context, actions: List) -> None:
        actions.append('roll_ability_check')
        context.update('actions', actions)
        context.update('ability', Ability.DEXTERITY)

## Character rule action tests
## ===========================

@rule
class PrintExperienceGained(Rule):
    def when(context: RuleEngine.Context, 
             actions: List, 
             character: Character, 
             gained_experience: int) -> bool:
        return 'on:experience_gained' in actions
    
    def then(context: RuleEngine.Context, 
             character: Character,
             gained_experience: int, 
             **kwargs):
        print(f'{character.name} gained {gained_experience} XP.')

@rule
class PrintLevelGained(Rule):
    def when(context: RuleEngine.Context, 
             actions: List, 
             character: Character, 
             previous_level: int,
             reached_level: int) -> bool:
        return 'on:level_gained' in actions
    
    def then(context: RuleEngine.Context, 
             character: Character,
             previous_level: int,
             reached_level: int, 
             **kwargs):
        print(f'{character.name} levelled-up from {previous_level} to {reached_level}.')

@rule
class PrintEquippedArmor(Rule):
    def when(context: RuleEngine.Context,
             actions: List,
             character: Character) -> bool:
        return 'on:equipped_armor' in actions
    
    def then(context, character: Character, **kwargs):
        print(f'{character.name} equipped {character.equipped_armor.name}.')

@rule
class PrintUnequippedArmor(Rule):
    def when(context: RuleEngine.Context,
             actions: List,
             character: Character) -> bool:
        return 'on:unequipped_armor' in actions
    
    def then(context, character: Character, **kwargs):
        print(f'{character.name} unquipped his/her armor.')

@rule
class PrintEquippedShield(Rule):
    def when(context: RuleEngine.Context,
             actions: List,
             character: Character) -> bool:
        return 'on:equipped_shield' in actions
    
    def then(context, character: Character, **kwargs):
        print(f'{character.name} equipped {character.equipped_shield.name}.')

@rule
class PrintUnequippedShield(Rule):
    def when(context: RuleEngine.Context,
             actions: List,
             character: Character) -> bool:
        return 'on:unequipped_shield' in actions
    
    def then(context, character: Character, **kwargs):
        print(f'{character.name} unquipped his/her shield.')