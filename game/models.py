# game/models.py
from dataclasses import dataclass, field
from .exceptions import InvalidActionError


@dataclass
class Food:
    name: str
    satiety: int
    price: int

    def __repr__(self) -> str:
        return f"Food(name={self.name!r}, satiety={self.satiety}, price={self.price})"


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

    def __repr__(self) -> str:
        return (f"Medicine(name={self.name!r}, price={self.price}, "
                f"heal_hp={self.heal_hp}, number_of_uses={self.number_of_uses}, uses={self.uses})")
