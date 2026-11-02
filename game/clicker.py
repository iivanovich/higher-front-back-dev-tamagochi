"""Кликер: источник дохода в игре.

Кликер не хранит кошелёк: он лишь сообщает, сколько монет приносит клик.
Учётом и тратой денег занимается сущность игры.
"""

import random
from abc import ABC, abstractmethod

from game import constants


class Income(int):
    """Целое число дохода, которое можно ещё и вызвать.

    Позволяет обращаться к доходу одинаково — и как к свойству
    (``clicker.income_per_click``), и как к методу
    (``clicker.income_per_click()``).
    """

    def __call__(self) -> int:
        """Вернуть доход при обращении в стиле метода.

        :return: значение дохода.
        """
        return int(self)


class AbstractClicker(ABC):
    """Интерфейс кликера."""

    @abstractmethod
    def __init__(self) -> None:
        """Инициализировать кликер."""

    @abstractmethod
    def click(self) -> None:
        """Выполнить клик и начислить доход."""

    @abstractmethod
    def income_per_click(self) -> int:
        """Вернуть доход за один клик."""


class SimpleRandomClicker(AbstractClicker):
    """Кликер со случайным доходом в заданном диапазоне.

    Каждый клик приносит от ``min_income`` до ``max_income`` монет.
    Каждый :data:`constants.CLICK_BONUS_EVERY`-й клик даёт бонусный доход.
    """

    def __init__(
        self,
        min_income: int = constants.DEFAULT_MIN_INCOME,
        max_income: int = constants.DEFAULT_MAX_INCOME,
    ) -> None:
        """Создать кликер.

        :param min_income: минимальный доход за клик.
        :param max_income: максимальный доход за клик.
        :raises ValueError: если границы заданы некорректно.
        """
        if min_income <= 0 or min_income > max_income:
            raise ValueError('Некорректный диапазон дохода за клик')
        self._min_income = min_income
        self._max_income = max_income
        self._income_per_click = min_income
        self._coins = constants.START_COINS
        self._clicks = 0

    def click(self) -> None:
        """Сделать клик: начислить случайный доход и бонус каждый N-й клик."""
        income = random.randint(self._min_income, self._max_income)
        self._clicks += 1
        if self._clicks % constants.CLICK_BONUS_EVERY == 0:
            income *= constants.CLICK_BONUS_MULTIPLIER
        self._income_per_click = income

    def income_per_click(self) -> int:
        """Вернуть доход за последний клик.

        :return: количество монет за последний клик.
        """
        return Income(self._income_per_click)

    @property
    def coins(self) -> int:
        """Вернуть накопленные кликером монеты."""
        return self._coins

    def __repr__(self) -> str:
        """Вернуть читаемое представление кликера."""
        return f'SimpleRandomClicker(income={self._income_per_click})'


class SimpleClicker(AbstractClicker):
    """Кликер с фиксированным доходом за клик."""

    def __init__(
        self,
        income_per_click: int = constants.DEFAULT_FIXED_INCOME,
    ) -> None:
        """Создать кликер.

        :param income_per_click: сколько монет приносит один клик.
        :raises ValueError: если доход не положительный.
        """
        if income_per_click <= 0:
            raise ValueError('Доход за клик должен быть положительным')
        self._income_per_click = income_per_click
        self._coins = constants.START_COINS

    def click(self) -> None:
        """Сделать клик и начислить монеты."""
        self._coins += self._income_per_click

    def income_per_click(self) -> int:
        """Вернуть доход за один клик.

        :return: количество монет за клик.
        """
        return Income(self._income_per_click)

    @property
    def coins(self) -> int:
        """Вернуть накопленные кликером монеты."""
        return self._coins

    def __repr__(self) -> str:
        """Вернуть читаемое представление кликера."""
        return f'SimpleClicker(income={self._income_per_click})'
