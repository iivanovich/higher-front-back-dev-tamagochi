import itertools
from dataclasses import dataclass, field

from .exceptions import MedicineIsGone

_food_uid = itertools.count()

@dataclass(frozen=True)
class Food:
    name: str
    satiety: int
    price: int
    _uid: int = field(default_factory=lambda: next(_food_uid), compare=False, repr=False)

@dataclass
class Medicine:
    name: str
    price: int
    heal_hp: int
    number_of_uses: int
    uses: int = 0

    def is_empty(self) -> bool:
        return self.uses >= self.number_of_uses

    def use(self) -> None:
        if self.is_empty():
            raise MedicineIsGone("Лекарство закончилось.")
        self.uses += 1