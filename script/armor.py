from __future__ import annotations
from enum import Enum
from currency import Currency
import yaml

class ArmorType(Enum):
    LIGHT = 0,
    MEDIUM = 1,
    HEAVY = 2,
    SHIELD = 3

class Armor:

    """The in-game name of the armor."""
    name: str

    """The cost of the armor."""
    cost: Currency

    """The base armor class of the armor."""
    armor_class: int

    """The type of the armor."""
    type: ArmorType

    """The weight of the armor."""
    weight: int

    """Minimum strength required for receiving no speed penalites."""
    min_strength: int

    """Whether the armor causes disadvantage in stealth checks."""
    has_stealth_disadvantage: bool

    def __init__(self, name: str, cost: Currency, armor_class: int,
                 type: ArmorType, weight: int, min_strenth: int,
                 has_stealth_disadvantage: bool):
        self.name = name
        self.cost = cost
        self.armor_class = armor_class
        self.type = type
        self.weight = weight
        self.min_strength = min_strenth
        self.has_stealth_disadvantage = has_stealth_disadvantage

class ArmorReader:

    @staticmethod
    def read_armors_from_file(filename: str) -> dict[str, Armor]:
        with open(filename, 'r') as file:
            armors = {}
            armor_descriptors = yaml.safe_load(file)['armors']
            for armor_desc in armor_descriptors:
                id = armor_desc['id']
                name = armor_desc['name']
                type = ArmorType[armor_desc['type'].upper()]
                cost = Currency.from_string(armor_desc['cost'])
                weight = armor_desc['weight']
                armor_class = armor_desc['armor_class']
                min_strength = armor_desc.get('minimum_strength', 0)
                stealth_disadvantage = armor_desc.get('stealth_disadvantage', False)

                armors[id] = Armor(name, cost, armor_class, type, weight, 
                                   min_strength, stealth_disadvantage)
            return armors