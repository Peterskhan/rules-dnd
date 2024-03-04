from abc import abstractclassmethod
from character import *

## Rule engine framework
## =====================

class Rule:

    @abstractclassmethod
    def when(self, context) -> bool:
        pass

    @abstractclassmethod
    def then(self, context) -> None:
        pass

class RuleEngine:
    
    rules = []
    required_tokens = {}

    class Context:
        pass

    @classmethod
    def has_required_tokens(cls, rule_class, context: dict) -> bool:
        for token, token_type in cls.required_tokens[rule_class].items():
            found = hasattr(context, token) and type(getattr(context, token)) == token_type
            if not found:
                return False
        return True

    @classmethod
    def evaluate_rules_once(cls, context) -> tuple[bool, Context]:
        found_eligible_rule = False
        for rule in cls.rules:
            if cls.has_required_tokens(rule, context) and rule.when(context):
                found_eligible_rule = True
                rule.then(context)

        return found_eligible_rule, context

    @classmethod
    def execute_rules(cls, context) -> Context:
        found_eligible_rule, context = cls.evaluate_rules_once(context)
        while found_eligible_rule:
            found_eligible_rule, context = cls.evaluate_rules_once(context)
        return context

def rule(*args, **kwargs):
    requires = kwargs.get('requires', {})

    def decorator(rule_class):
        RuleEngine.required_tokens[rule_class] = requires
        RuleEngine.rules.append(rule_class)
        return rule_class

    return decorator

## Rolling checks
## ==============

@rule(requires={'action': str, 'ability': Ability})
class RollAbilityCheck(Rule):
    """When rolling an ability check we roll a 1d20 and add a modifier."""

    def when(context: RuleEngine.Context) -> bool:
        return context.action == 'roll_ability_check' \
               and not hasattr(context, 'rolled_ability_check')

    def then(context: RuleEngine.Context) -> None:
        context.result = context.character.roll_ability_check(context.ability)
        context.rolled_ability_check = True

@rule
class RollSkillCheck(Rule):
    pass

@rule(requires={'action': str, 'skill': Skill, 'character': Character})
class StealthCheckDisadvantageFromArmor(Rule):
    """When the character wears unstealthy armor, it has disadvantage on stealth checks."""

    def when(context):
        return context.action == 'roll_skill_check' \
               and context.skill == Skill.STEALTH \
               and context.character.equipped_armor is not None \
               and context.character.equipped_armor.has_stealth_disadvantage

    def then(context):
        context.has_disadvantage = True
        
@rule(requires={'action': str})
class RollInitiative(Rule):
    """When rolling initiative we roll a dexterity check."""

    def when(context: RuleEngine.Context) -> bool:
        return context.action == 'roll_initiative'
    
    def then(context: RuleEngine.Context) -> None:
        context.action = 'roll_ability_check'
        context.ability = Ability.DEXTERITY

## Calculating armor class
## =======================

@rule(requires={'action': str, 'character': Character})
class ArmorClassNoArmor(Rule):
    def when(context: RuleEngine.Context):
        return context.action == 'get_armor_class' \
               and not hasattr(context, 'armor_ac_added') \
               and context.character.equipped_armor is None
    
    def then(context: RuleEngine.Context):
        print('Character has no armor on, using unarmored AC')
        context.result = 10 + context.character.ability_modifiers[Ability.DEXTERITY]
        context.armor_ac_added = True

@rule(requires={'action': str, 'character': Character})
class ArmorClassLightArmor(Rule):
    def when(context):
        return context.action == 'get_armor_class' \
               and not hasattr(context, 'armor_ac_added') \
               and context.character.equipped_armor is not None \
               and context.character.equipped_armor.type == ArmorType.LIGHT
    
    def then(context):
        print('Character has light armor on, using AC + DEX_MOD')
        context.result = context.character.equipped_armor.armor_class \
                         + context.character.ability_modifiers[Ability.DEXTERITY]
        context.armor_ac_added = True

@rule(requires={'action': str, 'character': Character})
class ArmorClassMediumArmor(Rule):
    def when(context):
        return context.action == 'get_armor_class' \
               and not hasattr(context, 'armor_ac_added') \
               and context.character.equipped_armor is not None \
               and context.character.equipped_armor.type == ArmorType.MEDIUM
    
    def then(context):
        print('Character has medium armor on, using AC + MIN(2, DEX_MOD)')
        context.result = context.character.equipped_armor.armor_class \
                         + min(2, context.character.ability_modifiers[Ability.DEXTERITY])
        context.armor_ac_added = True

@rule(requires={'action': str, 'character': Character})
class ArmorClassHeavyArmor(Rule):
    def when(context):
        return context.action == 'get_armor_class' \
               and not hasattr(context, 'armor_ac_added') \
               and context.character.equipped_armor is not None \
               and context.character.equipped_armor.type == ArmorType.HEAVY
    
    def then(context):
        print('Character has heavy armor on, using AC')
        context.result = context.character.equipped_armor.armor_class
        context.armor_ac_added = True

@rule(requires={'action': str, 'character': Character, 'result': int})
class ArmorClassShield(Rule):
    def when(context):
        return context.action == 'get_armor_class' \
               and not hasattr(context, 'shield_ac_added') \
               and context.character.equipped_shield is not None
    
    def then(context):
        print('Character has shield, adding shield AC')
        context.result += context.character.equipped_shield.armor_class
        context.shield_ac_added = True



GameController.load_weapons_and_armors()
character = Character()
character.equipped_armor_id = 'half_plate'
character.equipped_shield_id = 'shield'
character.ability_scores[Ability.DEXTERITY] = 16

context = RuleEngine.Context()
context.action = 'get_armor_class'
context.character = character
context = RuleEngine.execute_rules(context)

print(f'Armor class: {context.result}')