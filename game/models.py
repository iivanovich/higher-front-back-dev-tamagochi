import uuid
from dataclasses import dataclass, field

from .exceptions import InvalidActionError


@dataclass
class Food:
    name: str
    satiety: int
    price: int
    _identity: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __eq__(self, other):
        if not isinstance(other, Food):
            return False
        return self._identity == other._identity

    def __hash__(self):
        return hash(self._identity)

@dataclass
class Medicine:
    name: str
    price: int
    heal_hp: int
    number_of_uses: int
    uses: int = field(default=0)

    def is_empty(self) -> bool:
        return self.uses >= self.number_of_uses

    def use(self) -> None:
        if self.is_empty():
            raise InvalidActionError("Лекарство закончилось.")
        self.uses += 1