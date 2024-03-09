"""Collection of rules that are used to calculate the armor class of a character."""

from ruleengine import *
from character import *

@rule
class ArmorClassNoArmor(Rule):
    def when(context: RuleEngine.Context, actions: List, character: Character):
        return 'on:unequipped_armor' in actions \
               and character.equipped_armor is None
    
    def then(context: RuleEngine.Context, character: Character, **kwargs):
        print('Character has no armor on, using unarmored AC')
        character.armor_class = 10 + character.dexterity_modifier

@rule
class ArmorClassLightArmor(Rule):
    def when(context: RuleEngine.Context, actions: List, character: Character):
        return 'on:equipped_armor' in actions \
               and character.equipped_armor.type == ArmorType.LIGHT
    
    def then(context: RuleEngine.Context, character: Character, **kwargs):
        print('Character has light armor on, using AC + DEX_MOD')
        character.armor_class = character.equipped_armor.armor_class \
                                + character.dexterity_modifier

@rule
class ArmorClassMediumArmor(Rule):
    def when(context: RuleEngine.Context, actions: List, character: Character):
        return 'on:equipped_armor' in actions \
               and character.equipped_armor.type == ArmorType.MEDIUM
    
    def then(context: RuleEngine.Context, character: Character,  **kwargs):
        print('Character has medium armor on, using AC + MIN(2, DEX_MOD)')
        character.armor_class = character.equipped_armor.armor_class \
                                + min(2, character.dexterity_modifier)

@rule
class ArmorClassHeavyArmor(Rule):
    def when(context: RuleEngine.Context, actions: List, character: Character):
        return 'on:equipped_armor' in actions \
               and character.equipped_armor.type == ArmorType.HEAVY
    
    def then(context: RuleEngine.Context, character: Character, **kwargs):
        print('Character has heavy armor on, using AC')
        character.armor_class = character.equipped_armor.armor_class

@rule(priority=-1)
class ArmorClassShield(Rule):
    def when(context: RuleEngine.Context, actions: List, character: Character):
        return 'on:equipped_shield' in actions \
               and character.equipped_shield is not None
    
    def then(context: RuleEngine.Context, character: Character, **kwargs):
        print('Character has shield, adding shield AC')
        character.armor_class += character.equipped_shield.armor_class
