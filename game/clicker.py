"""Кликер: единственный источник монет в игре."""

import random
from abc import ABC, abstractmethod

from game import constants
from game.exceptions import NotEnoughCoinsError


class AbstractClicker(ABC):
    """Интерфейс кликера.

    Кликер хранит кошелёк и умеет начислять доход за клик. Он ничего не
    знает про питомца и игру — только про монеты.
    """

    @abstractmethod
    def __init__(self) -> None:
        """Инициализировать кликер."""

    @abstractmethod
    def click(self) -> None:
        """Выполнить клик и начислить монеты."""

    @abstractmethod
    def income_per_click(self) -> int:
        """Вернуть доход за один клик."""

    @property
    @abstractmethod
    def coins(self) -> int:
        """Вернуть текущее количество монет."""

    @abstractmethod
    def spend(self, amount: int) -> None:
        """Списать монеты за покупку.

        :param amount: сколько монет нужно списать.
        """


class SimpleRandomClicker(AbstractClicker):
    """Кликер со случайным доходом в заданном диапазоне.

    Каждый клик приносит от ``min_income`` до ``max_income`` монет.
    Каждый :data:`constants.CLICK_BONUS_EVERY`-й клик даёт бонусный доход —
    это добавляет игре динамику и вознаграждает настойчивость игрока.
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
        self._coins = 0
        self._clicks = 0

    def income_per_click(self) -> int:
        """Вернуть доход за последний клик.

        :return: количество монет, начисленных за последний клик.
        """
        return self._income_per_click

    @property
    def coins(self) -> int:
        """Вернуть текущее количество монет."""
        return self._coins

    def click(self) -> None:
        """Сделать клик: начислить случайный доход и бонус каждый N-й клик."""
        income = random.randint(self._min_income, self._max_income)
        self._clicks += 1
        if self._clicks % constants.CLICK_BONUS_EVERY == 0:
            income *= constants.CLICK_BONUS_MULTIPLIER
        self._income_per_click = income
        self._coins += income

    def spend(self, amount: int) -> None:
        """Списать монеты за покупку.

        :param amount: сколько монет нужно списать.
        :raises ValueError: если сумма отрицательная.
        :raises NotEnoughCoinsError: если монет не хватает.
        """
        if amount < 0:
            raise ValueError('Сумма списания не может быть отрицательной')
        if amount > self._coins:
            raise NotEnoughCoinsError(
                f'Нужно {amount} монет, а есть только {self._coins}'
            )
        self._coins -= amount

    def __repr__(self) -> str:
        """Вернуть читаемое представление кликера."""
        return f'SimpleRandomClicker(coins={self._coins}, clicks={self._clicks})'


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
        self._coins = 0

    def income_per_click(self) -> int:
        """Вернуть доход за один клик.

        :return: количество монет за клик.
        """
        return self._income_per_click

    @property
    def coins(self) -> int:
        """Вернуть текущее количество монет."""
        return self._coins

    def click(self) -> None:
        """Сделать клик и начислить монеты."""
        self._coins += self._income_per_click

    def spend(self, amount: int) -> None:
        """Списать монеты за покупку.

        :param amount: сколько монет нужно списать.
        :raises ValueError: если сумма отрицательная.
        :raises NotEnoughCoinsError: если монет не хватает.
        """
        if amount < 0:
            raise ValueError('Сумма списания не может быть отрицательной')
        if amount > self._coins:
            raise NotEnoughCoinsError(
                f'Нужно {amount} монет, а есть только {self._coins}'
            )
        self._coins -= amount
