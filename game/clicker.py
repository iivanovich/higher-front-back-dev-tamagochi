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
    def __init__(self, min_income: int, max_income: int):
        self._min_income = min_income
        self._max_income = max_income
        self._current_income = 0

    @property
    def income_per_click(self) -> int:
        return self._current_income

    def click(self) -> None:
        self._current_income = random.randint(self._min_income, self._max_income)