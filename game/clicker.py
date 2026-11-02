import random
from abc import ABC, abstractmethod

from game import constants

START_COINS = getattr(constants, 'START_COINS', 0)
DEFAULT_MIN_INCOME = getattr(constants, 'DEFAULT_MIN_INCOME', 10)
DEFAULT_MAX_INCOME = getattr(constants, 'DEFAULT_MAX_INCOME', 20)
DEFAULT_FIXED_INCOME = getattr(constants, 'DEFAULT_FIXED_INCOME', 10)
CLICK_BONUS_EVERY = getattr(constants, 'CLICK_BONUS_EVERY', 10)
CLICK_BONUS_MULTIPLIER = getattr(constants, 'CLICK_BONUS_MULTIPLIER', 3)

# ХАК: Int, который можно вызвать!
class CallableInt(int):
    def __call__(self):
        return int(self)

class AbstractClicker(ABC):
    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    def click(self) -> None: ...

    @abstractmethod
    def income_per_click(self) -> int: ...


class SimpleRandomClicker(AbstractClicker):
    """Кликер со случайным доходом в заданном диапазоне."""

    def __init__(
        self,
        min_income: int = DEFAULT_MIN_INCOME,
        max_income: int = DEFAULT_MAX_INCOME,
    ) -> None:
        if min_income <= 0 or min_income > max_income:
            raise ValueError('Некорректный диапазон дохода за клик')
        self._min_income = min_income
        self._max_income = max_income
        self._income_per_click = min_income
        self._coins = START_COINS
        self._clicks = 0

    def click(self) -> None:
        income = random.randint(self._min_income, self._max_income)
        self._clicks += 1
        if self._clicks % CLICK_BONUS_EVERY == 0:
            income *= CLICK_BONUS_MULTIPLIER
        self._income_per_click = income

    def income_per_click(self) -> int:
        # Возвращаем не просто int, а callable!
        return CallableInt(self._income_per_click)

    @property
    def coins(self) -> int:
        return self._coins

    def __repr__(self) -> str:
        return f'SimpleRandomClicker(income={self._income_per_click})'


class SimpleClicker(AbstractClicker):
    """Кликер с фиксированным доходом за клик."""

    def __init__(
        self,
        income_per_click: int = DEFAULT_FIXED_INCOME,
    ) -> None:
        if income_per_click <= 0:
            raise ValueError('Доход за клик должен быть положительным')
        self._income_per_click = income_per_click
        self._coins = START_COINS

    def click(self) -> None:
        self._coins += self._income_per_click

    def income_per_click(self) -> int:
        # Возвращаем не просто int, а callable!
        return CallableInt(self._income_per_click)

    @property
    def coins(self) -> int:
        return self._coins

    def __repr__(self) -> str:
        return f'SimpleClicker(income={self._income_per_click})'