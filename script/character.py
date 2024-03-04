
from enum import Enum
from dice import DiceRoll
from armor import Armor, ArmorType
from weapon import Weapon, WeaponType, DamageType
import math
from gamecontroller import GameController

class Condition(Enum):
    BLINDED = 0,
    CHARMED = 1,
    DEAFENED = 2,
    FRIGHTENED = 3,
    GRAPPLED = 4,
    INCAPACITATED = 5,
    INVISIBLE = 6,
    PARALYZED = 7,
    PETRIFIED = 8,
    POISONED = 9,
    PRONE = 10,
    RESTRAINED = 11,
    STUNNED = 12,
    UNCONSCIOUS = 13,
    STABLE = 14 # Only makes sense with unconscious

class Ability(Enum):
    STRENGTH = 0,
    DEXTERITY = 1,
    CONSTITUTION = 2,
    INTELLIGENCE = 3,
    WISDOM = 4,
    CHARISMA = 5

class Skill(Enum):
    ACROBATICS = 0,
    ANIMAL_HANDLING = 1,
    ARCANA = 2,
    ATHLETICS = 3,
    DECEPTION = 4,
    HISTORY = 5,
    INSIGHT = 6,
    INTIMIDATION = 7,
    INVESTIGATION = 8,
    MEDICINE = 9,
    NATURE = 10,
    PERCEPTION = 11,
    PERFORMANCE = 12,
    PERSUASION = 13,
    RELIGION = 14,
    SLEIGHT_OF_HAND = 15
    STEALTH = 16,
    SURVIVAL = 17

class Character:

    def __init__(self):
        self.name = 'Character'
        self.class_id = None
        self.race_id = None
        self.subrace_id = None
        self.experience = 4000
        self.ability_scores = {Ability.CHARISMA: 10, 
                               Ability.CONSTITUTION: 10,
                               Ability.DEXTERITY: 10,
                               Ability.INTELLIGENCE: 10,
                               Ability.STRENGTH: 10,
                               Ability.WISDOM: 10}
                
        self.saving_throw_proficiencies = []
        self.skill_proficiencies = []
        self.armor_type_proficiencies = []
        self.weapon_type_proficiencies = []
        self.weapon_proficiencies = []

        self.hitpoints = 30
        self.max_hitpoints = 30
        self.hit_dice = DiceRoll.from_string('1d8')
        self.temporary_hitpoints = 0
        self.num_hit_dice = 1
        self.vulnerabilities = []
        self.resistances = []
        self.immunities = []
        self.base_speed = 30
        self.equipped_armor_id = ''
        self.equipped_shield_id = ''
        self.active_conditions = set()

        self.num_death_save_failure = 0
        self.num_death_save_success = 0

    ## Generic attributes
    ## ==================

    """The name of the character."""
    name: str

    """The class ID of the character."""
    class_id: str

    """The race ID of the character."""
    race_id: str

    """The subrace ID of the character."""
    subrace_id: str

    ## Experience, level and proficiency bonus
    ## =======================================

    """The current experience of the character."""
    experience: int

    """Dictionary relating levels to their minimum XP and proficiency bonus."""
    _LEVEL_TO_XP_AND_PROFICIENCY = {
        # Level: (Required XP, Proficiency bonus)
        1:  (0,      2),
        2:  (300,    2),
        3:  (900,    2),
        4:  (2700,   2),
        5:  (6500,   3),
        6:  (14000,  3),
        7:  (23000,  3),
        8:  (34000,  3),
        9:  (48000,  4),
        10: (64000,  4),
        11: (85000,  4),
        12: (100000, 4),
        13: (120000, 5),
        14: (140000, 5),
        15: (165000, 5),
        16: (195000, 5),
        17: (225000, 6),
        18: (265000, 6),
        19: (305000, 6),
        20: (355000, 6)
    }

    @property
    def level(self) -> int:
        """The current level of the character."""
        return next(level for level, (xp_threshold, _) in reversed(self._LEVEL_TO_XP_AND_PROFICIENCY.items())
                    if self.experience > xp_threshold)
    
    @property
    def proficiency_bonus(self) -> int:
        """The current proficiency bonus of the character."""
        return next(proficiency for (xp_threshold, proficiency) in reversed(self._LEVEL_TO_XP_AND_PROFICIENCY.values())
                    if self.experience > xp_threshold)

    ## Ability scores
    ## ==============

    """The ability scores of the character."""
    ability_scores: dict[Ability, int]

    @property
    def ability_modifiers(self):
        """The ability modifiers of the character."""
        modifiers = {}
        for ability, score in self.ability_scores.items():
            modifiers[ability] = math.floor((score - 10) / 2.0)
        return modifiers

    ## Proficiencies
    ## =============

    """The list of saving throws the character is proficient in."""
    saving_throw_proficiencies: list[Ability]

    """The list of skills the character is proficient in."""
    skill_proficiencies: list[Skill]

    """The list of armor types the character is proficient in."""
    armor_type_proficiencies: list[ArmorType]

    """The list of weapon types the character is proficient in."""
    weapon_type_proficiencies: list[WeaponType]

    """The list of specific weapons the character is proficient in."""
    weapon_proficiencies: list[str]

    ## Hitpoints
    ## =========

    """The current hitpoints of the character."""
    hitpoints: int

    """The maximum hitpoints of the character."""
    max_hitpoints: int

    """The hit dice type of the character."""
    hit_dice: DiceRoll

    """The current temporary hitpoints of the character."""
    temporary_hitpoints: int

    """The number of hit dice the character currently has."""
    num_hit_dice: int

    ## Vulnerabilities, resistances and immunity
    ## =========================================

    """List of damage types the character is vulnerable to."""
    vulnerabilities: list[DamageType]

    """List of damage types the character is resistant to."""
    resistances: list[DamageType]

    """List of damage types the character is immune to."""
    immunities: list[DamageType]

    ## Armor and speed
    ## ===============

    """The base movement speed of the character."""
    base_speed: int

    """The ID of the currently equipped armor of the character."""
    equipped_armor_id: str

    @property
    def equipped_armor(self) -> Armor | None:
        return GameController.armors.get(self.equipped_armor_id)

    """The ID of the currently equipped shield of the character."""
    equipped_shield_id = str

    @property
    def equipped_shield(self) -> Armor | None:
        return GameController.armors.get(self.equipped_shield_id)

    @property
    def speed(self) -> int:
        """The movement speed of the character."""

        # Wearing too heavy armor without sufficient STR slows down the character (PH. 144)
        if self.equipped_armor.min_strength > self.ability_scores[Ability.STRENGTH]:
            return self.base_speed - 10
        
        return self.base_speed

    @property
    def armor_class(self) -> int:
        """The current armor class of the character."""

        # While not wearing armor the base armor class is 10 + DEX modifier (PH. 14)
        if self.equipped_armor is None:
            return 10 + self.ability_modifiers[Ability.DEXTERITY]
        
        total = 0
        if self.equipped_shield is not None:
            total += self.equipped_shield.armor_class

        if self.equipped_armor is not None:
            match self.equipped_armor.type:
                case ArmorType.HEAVY:
                    total += self.equipped_armor.armor_class
                case ArmorType.MEDIUM:
                    # Medium armor allows adding the DEX modifier 
                    # capped at +2 to the armor class (PH. 144)
                    total += self.equipped_armor.armor_class \
                             + min(2, self.ability_modifiers[Ability.DEXTERITY])
                case ArmorType.LIGHT:
                    # Light armor allows adding the DEX modifier
                    # to the armor class (PH. 144)
                    total +=self.equipped_armor.armor_class \
                            + self.ability_modifiers[Ability.DEXTERITY]
                case _:
                    raise AssertionError(f'Invalid equipped armor type: {self.equipped_armor.type}')
                
        return total
        
    ## Weapons
    ## =======

    """The ID of the currently equipped weapon of the character."""
    equipped_weapon_id: str

    """The equipped weapon of the character."""
    @property
    def equipped_weapon(self) -> Weapon | None:
        return GameController.weapons.get(self.equipped_weapon_id, None)

    ## Rolls, checks and saving throws
    ## ===============================

    _SKILL_TO_ABILITY_SCORE = {
        Skill.ATHLETICS: Ability.STRENGTH,
        Skill.ACROBATICS: Ability.DEXTERITY,
        Skill.SLEIGHT_OF_HAND: Ability.DEXTERITY,
        Skill.STEALTH: Ability.DEXTERITY,
        Skill.ARCANA: Ability.INTELLIGENCE,
        Skill.HISTORY: Ability.INTELLIGENCE,
        Skill.INVESTIGATION: Ability.INTELLIGENCE,
        Skill.NATURE: Ability.INTELLIGENCE,
        Skill.RELIGION: Ability.INTELLIGENCE,
        Skill.ANIMAL_HANDLING: Ability.WISDOM,
        Skill.INSIGHT: Ability.WISDOM,
        Skill.MEDICINE: Ability.WISDOM,
        Skill.PERCEPTION: Ability.WISDOM,
        Skill.SURVIVAL: Ability.WISDOM,
        Skill.DECEPTION: Ability.CHARISMA,
        Skill.INTIMIDATION: Ability.CHARISMA,
        Skill.PERFORMANCE: Ability.CHARISMA,
        Skill.PERSUASION: Ability.CHARISMA
    }

    def roll_ability_check(self, ability: Ability, has_disadvantage = False) -> int:
        """Rolls an ability check with the specified ability."""

        # Wearing an armor type without proficiency causes disadvantage
        # on Dexterity and Strength ability checks and saving throws (PH. 144)
        if (ability == Ability.STRENGTH or ability == Ability.DEXTERITY) \
            and self.equipped_armor is not None \
            and self.equipped_armor.type not in self.armor_type_proficiencies:
            has_disadvantage = True

        dice = DiceRoll.from_string('1d20')
        base_value = dice.roll_disadvantage() if has_disadvantage else dice.roll()
        return base_value + self.ability_modifiers[ability]
        
    def roll_skill_check(self, skill: Skill) -> int:
        """Rolls a skill check with the specified skill."""

        # Wearing certain armor variants cause disadvantage 
        # on Dexterity (Stealth) checks (PH. 144)
        has_disadvantage = skill == Skill.STEALTH and self.equipped_armor is not None \
                           and self.equipped_armor.has_stealth_disadvantage

        ability = self._SKILL_TO_ABILITY_SCORE[skill]
        if skill in self.skill_proficiencies:
            return self.roll_ability_check(ability, has_disadvantage) + self.proficiency_bonus
        else:
            return self.roll_ability_check(ability, has_disadvantage)

    def do_saving_throw(self, ability: Ability):
        """Rolls a saving throw with the specified skill."""

        if ability in self.saving_throw_proficiencies:
            return self.roll_ability_check(ability) + self.proficiency_bonus
        else:
            return self.roll_ability_check(ability)
        
    def roll_attack(self) -> tuple[int, int]:
        """Rolls an attack with the currently equipped weapon."""
        dice = DiceRoll.from_string('1d20')
        base_value = dice.roll()
        value = base_value
        
        ## When attacking without a weapon using an "Unarmed Strike" 
        ## it counts as a melee attack (STR modifier applies) and the
        ## character is proficient (PH. 195).
        if self.equipped_weapon is None:
            value += self.ability_modifiers[Ability.STRENGTH] + self.proficiency_bonus
            return base_value, value

        ## Finesse weapons allow to choose between STR and DEX modifier (PH. 147)
        ## Here we choose the bigger one assuming a player would do so
        if self.equipped_weapon.is_finesse:
            value += max(self.ability_modifiers[Ability.DEXTERITY],
                         self.ability_modifiers[Ability.STRENGTH])
            
        ## For non-finesse weapons: ranged weapons use the DEX modifier and 
        ## melee weapons use the STR modifier (PH. 194)
        elif self.equipped_weapon.is_ranged:
            value += self.ability_modifiers[Ability.DEXTERITY]
        else:
            value += self.ability_modifiers[Ability.STRENGTH]

        ## When the character is proficient with the specific weapon 
        ## or weapon type the proficiency bonus is also added (PH. 194)
        if self.equipped_weapon_id in self.weapon_proficiencies \
           or self.equipped_weapon.type in self.weapon_type_proficiencies:
            value += self.proficiency_bonus

        return base_value, value

    def roll_damage(self, is_critical = False) -> tuple[int, DamageType]:
        """Rolls damage with the currently equipped weapon."""

        ## When attacking without a weapon using an "Unarmed Strike" 
        ## the character deals 1 + STR modifier bludgeoning damage (PH. 195)
        if self.equipped_weapon is None:
            return 1 + self.ability_modifiers[Ability.STRENGTH], DamageType.BLUDGEONING
        
        ## Apply the same ability score modifier as used for the attack roll (PH. 196)
        modifier = 0
        if self.equipped_weapon.is_finesse:
            modifier = max(self.ability_modifiers[Ability.DEXTERITY], 
                           self.ability_modifiers[Ability.STRENGTH])
        elif self.equipped_weapon.is_ranged:
            modifier = self.ability_modifiers[Ability.DEXTERITY]
        else:
            modifier = self.ability_modifiers[Ability.STRENGTH]

        ## On critical hits the character can roll the damage dice twice and add the 
        ## relevant modifier once (PH. 196)
        damage1, type = self.equipped_weapon.roll_damage()
        if is_critical:
            damage2, type = self.equipped_weapon.roll_damage()
            return damage1 + damage2 + modifier, type
        
        return damage1 + modifier, type

    def roll_initiative(self):
        """Rolls initiative for combat."""
        return self.roll_ability_check(Ability.DEXTERITY)

    ## Receiving damage and healing
    ## ============================

    def suffer_damage(self, damage_amount: int, damage_type: DamageType, is_critical_hit = False):
        """Deals the specified amount of damage to the character."""

        if damage_type in self.immunities:
            return
        
        if self.hitpoints == 0:

            ## A stabilized character stops being stable upon receiving damage (PH. 197)
            if Condition.STABLE in self.active_conditions:
                self.active_conditions.remove(Condition.STABLE)

            ## A character receiving damage while at zero hitpoints gains one (two from 
            ## critical attacks) death save failure (PH. 197)
            if is_critical_hit:
                self.num_death_save_failure += 2
            else:
                self.num_death_save_failure += 1

            ## See note at rolling death saves
            if self.num_death_save_failure >= 3:
                raise NotImplementedError(f'The character should die...') 
        
        ## Vulnerability to a damage type doubles its value, while resistance to it
        ## halves its value (PH. 197)
        if damage_type in self.vulnerabilities:
            damage_amount = damage_amount * 2
        elif damage_type in self.resistances:
            damage_amount = math.floor(damage_amount / 2.0)

        remaining_damage = damage_amount - self.hitpoints        
        self.hitpoints = max(0, self.hitpoints - damage_amount)

        ## The character dies if the remaining damage after reaching zero hitpoints
        ## exceeds its maximum hitpoints, called instant-death (PH. 197)
        if remaining_damage >= self.max_hitpoints:
            raise NotImplementedError(f'The character should die...')

    def heal(self, amount: int):
        """Heals the character with the specified amount of hitpoints."""

        ## Unconsciousness (and being stabilized) effects are removed
        ## if the character is healed while at zero hitpoints. Death
        ## save counters are also reset (PH. 197)
        if self.hitpoints == 0:
            self.active_conditions.discard(Condition.STABLE)
            self.active_conditions.discard(Condition.UNCONSCIOUS)
            self.num_death_save_failure = 0
            self.num_death_save_success = 0

        self.hitpoints = min(self.max_hitpoints, self.hitpoints + amount)

    ## Death saves and conditions
    ## ==========================
        
    active_conditions = set[Condition]
    
    """The number of failed death saves since unconscious."""
    num_death_save_failure: int

    """The number of succesful death saves since unconscious."""
    num_death_save_success: int

    def roll_death_save(self):
        """Rolls a death saving throw."""

        ## Abilities are not considered for death saves, a roll at least 10
        ## counts as a success, a roll below 10 counts as a failure (PH. 197)
        value = DiceRoll.from_string('1d20').roll()
        if value >= 10:
            self.num_death_save_success += 1
        else:
            self.num_death_save_failure += 1

        ## A roll of one counts as two failures, a roll of twenty instantly 
        ## heals one hitpoint and ends the unconsciousness (PH. 197)
        if value == 1:
            self.num_death_save_failure += 1
        elif value == 20:
            self.active_conditions.remove(Condition.UNCONSCIOUS)
            self.active_conditions.discard(Condition.STABLE)
            self.num_death_save_success = 0
            self.num_death_save_failure = 0
            self.heal(1)

        ## The character dies upon reaching 3 failed death saves.
        ## The character becomes stable upon reaching 3 successful saves (PH. 197)
        if self.num_death_save_failure >= 3:
            raise NotImplementedError('The character should die.')
        elif self.num_death_save_success == 3:
            self.active_conditions.add(Condition.STABLE)
            self.num_death_save_success = 0
            self.num_death_save_failure = 0

    ## Resting
    ## =======

    def do_long_rest(self):
        pass

    def do_short_rest(self):
        pass

    ## Serialization
    ## =============

    def serialize(self):
        pass

    def deserialize(self):
        pass