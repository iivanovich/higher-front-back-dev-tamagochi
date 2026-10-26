import random
from abc import ABC, abstractmethod


class AbstractClicker(ABC):
    """Базовый абстрактный класс для кликеров в игре."""

    @abstractmethod
    def click(self) -> None:
        """Выполняет действие клика. Реализация зависит от типа кликера."""

    @property
    @abstractmethod
    def income_per_click(self) -> int:
        """Возвращает доход, получаемый за один клик."""


class SimpleRandomClicker(AbstractClicker):
    """Кликер, который приносит случайное количество монет."""

    def __init__(self, min_income: int, max_income: int) -> None:
        if min_income < 0 or max_income < 0 or min_income > max_income:
            raise ValueError("min_income и max_income должны быть неотрицательными, min <= max.")

        self._min_income = min_income
        self._max_income = max_income
        self._current_income = 0

    @property
    def income_per_click(self) -> int:
        """Возвращает доход, полученный при последнем клике."""
        return self._current_income

    def click(self) -> None:
        """Выполняет клик и обновляет доход."""
        self._current_income = random.randint(self._min_income, self._max_income)
