"""Collection of rules that are used to calculate the armor class of a character."""

from ruleengine import *
from character import *

@rule
class ArmorClassNoArmor(Rule):
    def when(context: RuleEngine.Context, action: str, character: Character):
        return action == 'get_armor_class' \
               and character.equipped_armor is None
    
    def then(context: RuleEngine.Context, character: Character, **kwargs):
        print('Character has no armor on, using unarmored AC')
        context.result = 10 + character.dexterity_modifier

@rule
class ArmorClassLightArmor(Rule):
    def when(context: RuleEngine.Context, action: str, character: Character):
        return action == 'get_armor_class' \
               and character.equipped_armor is not None \
               and character.equipped_armor.type == ArmorType.LIGHT
    
    def then(context: RuleEngine.Context, character: Character, **kwargs):
        print('Character has light armor on, using AC + DEX_MOD')
        context.result = character.equipped_armor.armor_class \
                         + character.dexterity_modifier

@rule
class ArmorClassMediumArmor(Rule):
    def when(context: RuleEngine.Context, action: str, character: Character):
        return action == 'get_armor_class' \
               and character.equipped_armor is not None \
               and character.equipped_armor.type == ArmorType.MEDIUM
    
    def then(context: RuleEngine.Context, character: Character,  **kwargs):
        print('Character has medium armor on, using AC + MIN(2, DEX_MOD)')
        context.result = character.equipped_armor.armor_class \
                         + min(2, character.dexterity_modifier)

@rule
class ArmorClassHeavyArmor(Rule):
    def when(context: RuleEngine.Context, action: str, character: Character):
        return action == 'get_armor_class' \
               and character.equipped_armor is not None \
               and character.equipped_armor.type == ArmorType.HEAVY
    
    def then(context: RuleEngine.Context, character: Character, **kwargs):
        print('Character has heavy armor on, using AC')
        context.result = character.equipped_armor.armor_class

@rule
class ArmorClassShield(Rule):
    def when(context: RuleEngine.Context, action: str, character: Character, result: int, no_shield: None):
        return action == 'get_armor_class' \
               and not context.has_flag('shield_ac_added') \
               and character.equipped_shield is not None
    
    def then(context: RuleEngine.Context, character: Character, **kwargs):
        print('Character has shield, adding shield AC')
        context.result += character.equipped_shield.armor_class
        context.set_flag('shield_ac_added')