from __future__ import annotations
from enum import Enum
import re

class CurrencyType(Enum):
    COPPER = 0,
    SILVER = 1,
    ELECTRUM = 2,
    GOLD = 3,
    PLATINUM = 4

class Currency:

    """The value of the currency (copper equivalent)."""
    value: int

    """Regular expression for validating currencies."""
    REGEX_PATTERN = r'^(\d+)\s(sp|gp|ep|cp|pp)$'

    def __init__(self, amount: int, type = CurrencyType.COPPER):
        match type:
            case CurrencyType.COPPER:
                self.value = amount
            case CurrencyType.SILVER:
                self.value = amount * 10
            case CurrencyType.ELECTRUM:
                self.value = amount * 50
            case CurrencyType.GOLD:
                self.value = amount * 100
            case CurrencyType.PLATINUM:
                self.value = amount * 1000
            case _:
                raise AssertionError(f'Unrecognized currency type: "{type}"')

    @classmethod
    def from_string(cls, currency_str: str) -> Currency:
        re_match = re.match(cls.REGEX_PATTERN, currency_str)
        if re_match:
            match re_match.group(2):
                case 'cp':
                    return Currency(int(re_match.group(1)), CurrencyType.COPPER)
                case 'sp':
                    return Currency(int(re_match.group(1)), CurrencyType.SILVER)
                case 'ep':
                    return Currency(int(re_match.group(1)), CurrencyType.ELECTRUM)
                case 'gp':
                    return Currency(int(re_match.group(1)), CurrencyType.GOLD)
                case 'pp':
                    return Currency(int(re_match.group(1)), CurrencyType.PLATINUM)
                case _:
                    raise AssertionError(f'Unrecognized currency type: "{type}"')
        else:
            raise AssertionError(f'Unrecognized currency format: "{currency_str}"')