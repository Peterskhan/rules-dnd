from __future__ import annotations
from enum import Enum
import re
import yaml
from dice import DiceRoll
from currency import Currency

class DamageType(Enum):
    ACID = 0,
    BLUDGEONING = 1,
    COLD = 2,
    FIRE = 3,
    FORCE = 4,
    LIGHTNING = 5,
    NECROTIC = 6,
    PIERCING = 7,
    POISION = 8,
    PSYCHIC = 9,
    RADIANT = 10,
    SLASHING = 11,
    THUNDER = 12

class DamageRoll:
    
    """The dice roll or fix value for the damage amount."""
    _value: DiceRoll | int

    """The damage type for the damage."""
    type: DamageType

    """Regular expression for validating damage rolls."""
    REGEX_PATTERN = r'^((\d{1,2}[dD](4|6|8|10|12|20|100))|(\d+))?\s*(.+)$'

    def __init__(self, value: DiceRoll | int, type: DamageType):
        """Constructs a damage roll."""
        self._value = value
        self.type = type

    def roll(self) -> int:
        """Rolls the damage value."""
        if isinstance(self._value, int):
            return self._value
        else:
            return self._value.roll()

    @classmethod
    def from_string(cls, damage_str: str) -> DamageRoll:
        """Parses the damage roll from the specified string."""

        match = re.match(cls.REGEX_PATTERN, damage_str)
        if match:
            dice_str = match.group(2)
            fix_str  = match.group(4)
            type_str = match.group(5)
            assert type_str.upper() in DamageType.__members__, f'Unrecognized damage type: "{type_str}"'
            type = DamageType[type_str.upper()]
            
            if fix_str is None:
                return DamageRoll(DiceRoll.from_string(dice_str), type)
            else:
                return DamageRoll(int(fix_str), type)
        else:
            raise AssertionError(f'Unrecognized damage roll format: "{damage_str}"')

class WeaponType(Enum):
    SIMPLE = 0,
    MARTIAL = 1

class Weapon:

    """The in-game name of the weapon."""
    name: str

    """The type of the weapon."""
    type: WeaponType

    """The cost of the weapon."""
    cost: Currency

    """The damage for the weapon."""
    damage: DamageRoll

    """The weight of the weapon."""
    weight: int

    """Whether the weapon is a ranged weapon."""
    is_ranged: bool

    """Whether the weapon is a finesse weapon."""
    is_finesse: bool

    def __init__(self, name: str, type: WeaponType, cost: Currency, 
                 damage: DamageRoll, weight: int, is_ranged: bool,
                 is_finesse: bool):
        self.name = name
        self.type = type
        self.cost = cost
        self.damage = damage
        self.weight = weight
        self.is_ranged = is_ranged
        self.is_finesse = is_finesse

    def roll_damage(self) -> tuple[int, DamageType]:
        return self.damage.roll(), self.damage.type
        
class WeaponReader:

    @staticmethod
    def read_weapons_from_file(filename: str) -> dict[str, Weapon]:
        with open(filename, 'r') as file:
            weapons = {}
            weapon_descriptors = yaml.safe_load(file)['weapons']
            for weapon_desc in weapon_descriptors:
                id = weapon_desc['id']
                name = weapon_desc['name']
                type = WeaponType[weapon_desc['type'].upper()]
                cost = Currency.from_string(weapon_desc['cost'])
                damage = DamageRoll.from_string(weapon_desc['damage'])
                weight = weapon_desc['weight']
                is_ranged = weapon_desc.get('ranged', False)
                is_finesse = weapon_desc.get('finesse', False)

                weapons[id] = Weapon(name, type, cost, damage, weight, is_ranged, is_finesse)
            return weapons