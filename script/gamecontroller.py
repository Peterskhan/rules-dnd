from typing import ClassVar
from armor import Armor, ArmorReader
from weapon import Weapon, WeaponReader

class GameController:
    armors: ClassVar[dict[str, Armor]]
    weapons: ClassVar[dict[str, Weapon]]

    @classmethod
    def load_weapons_and_armors(cls):
        cls.armors = ArmorReader.read_armors_from_file('content/armors.yaml')
        cls.weapons = WeaponReader.read_weapons_from_file('content/weapons.yaml')

