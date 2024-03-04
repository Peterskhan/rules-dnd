from __future__ import annotations
import random
import re

class Dice:

    @staticmethod
    def roll(num_rolls: int, num_sides: int) -> int:
        return sum([random.randint(1, num_sides) for _ in range(num_rolls)])

    @classmethod
    def roll_advantage(cls, num_rolls: int, num_sides: int) -> int:
        return max(cls.roll(num_rolls, num_sides), 
                   cls.roll(num_rolls, num_sides))

    @classmethod
    def roll_disadvantage(cls, num_rolls: int, num_sides: int) -> int:
        return min(cls.roll(num_rolls, num_sides), 
                   cls.roll(num_rolls, num_sides))

class DiceRoll:
    
    """The number of rolls for the dice."""
    num_rolls: int

    """The number of sides for the dice."""
    num_sides: int

    """Regular expression for validating dice rolls."""
    REGEX_PATTERN = r'^(\d{1,2})[dD](4|6|8|10|12|20|100)$'

    def __init__(self, num_rolls: int, num_sides: int):
        self.num_rolls = num_rolls
        self.num_sides = num_sides

    def roll(self) -> int:
        return Dice.roll(self.num_rolls, self.num_sides)
    
    def roll_advantage(self) -> int:
        return max(self.roll(), self.roll())

    def roll_disadvantage(self) -> int:
        return min(self.roll(), self.roll())

    def to_string(self) -> str:
        return f'{self.num_rolls}d{self.num_sides}'
    
    @classmethod
    def from_string(cls, dice_str: str) -> Dice:
        match = re.match(cls.REGEX_PATTERN, dice_str)
        if match:
            return DiceRoll(int(match.group(1)), int(match.group(2)))
        else:
            raise AssertionError(f'Unrecognized dice format: "{dice_str}"')