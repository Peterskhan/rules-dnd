"""Collection of rules that are used to calculate the armor class of a character."""

from ruleengine import *
from character import *

@rule
class RollAbilityCheck(Rule):
    """When rolling an ability check we roll a 1d20 and add a modifier."""

    def when(context: RuleEngine.Context, action: str, character: Character, ability: Ability) -> bool:
        return action == 'roll_ability_check'

    def then(context: RuleEngine.Context, character: Character, ability: Ability, **kwargs) -> None:
        context.result = character.roll_ability_check(ability)
        context.set_flag('rolled_ability_check')

@rule
class RollSkillCheck(Rule):
    pass

@rule
class StealthCheckDisadvantageFromArmor(Rule):
    """When the character wears unstealthy armor, it has disadvantage on stealth checks."""

    def when(context: RuleEngine.Context, action: str, skill: Skill, character: Character):
        return action == 'roll_skill_check' \
               and skill == Skill.STEALTH \
               and character.equipped_armor is not None \
               and character.equipped_armor.has_stealth_disadvantage

    def then(context: RuleEngine.Context, **kwargs):
        context.set_flag('has_disadvantage')
        
@rule
class RollInitiative(Rule):
    """When rolling initiative we roll a dexterity check."""

    def when(context: RuleEngine.Context, action: str) -> bool:
        return action == 'roll_initiative'
    
    def then(context: RuleEngine.Context, action: str) -> None:
        action = 'roll_ability_check'
        ability = Ability.DEXTERITY