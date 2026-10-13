# game/models.py
from dataclasses import dataclass, field

from .exceptions import InvalidActionError


@dataclass
class Food:
    name: str
    satiety: int
    price: int


@dataclass
class Medicine:
    name: str
    price: int
    heal_hp: int
    number_of_uses: int
    uses: int = field(default=0)

    def is_empty(self) -> bool:
        """Проверяет, закончились ли использования лекарства."""
        return self.uses >= self.number_of_uses

    def use(self) -> None:
        """Увеличивает счётчик использований. Вызывает ошибку, если лекарство закончилось."""
        if self.is_empty():
            raise InvalidActionError("Лекарство закончилось.")
        self.uses += 1
