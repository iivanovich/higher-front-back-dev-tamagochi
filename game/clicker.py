# game/clicker.py
import random
from abc import ABC, abstractmethod


class AbstractClicker(ABC):
    @abstractmethod
    def click(self) -> None:
        pass

    @property
    @abstractmethod
    def income_per_click(self) -> int:
        pass


class SimpleRandomClicker(AbstractClicker):
    """Кликер, который приносит случайное количество монет в заданном диапазоне."""

    def __init__(self, min_income: int, max_income: int) -> None:
        if min_income < 0 or max_income < 0 or min_income > max_income:
            raise ValueError("min_income и max_income должны быть неотрицательными, min <= max.")
        self._min_income = min_income
        self._max_income = max_income
        self._current_income = 0

    @property
    def income_per_click(self) -> int:
        """Возвращает текущий доход за клик (случайное значение)."""
        return self._current_income

    def click(self) -> None:
        """Выполняет клик и обновляет доход."""
        self._current_income = random.randint(self._min_income, self._max_income)
