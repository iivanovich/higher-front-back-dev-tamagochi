from dataclasses import dataclass, field

from .exceptions import InvalidActionError


@dataclass
class Food:
    """
    Описывает еду для питомца.

    Атрибуты:
        name (str): название еды.
        satiety (int): количество, на которое уменьшается голод после поедания.
        price (int): стоимость порции еды.
    """
    name: str
    satiety: int
    price: int

    def __repr__(self) -> str:
        return f"Food(name={self.name!r}, satiety={self.satiety}, price={self.price})"

@dataclass
class Medicine:
    """
    Описывает лекарство для питомца.

    Атрибуты:
        name (str): название лекарства.
        price (int): стоимость.
        heal_hp (int): сколько здоровья лечит за один приём.
        number_of_uses (int): сколько раз можно использовать.
        uses (int): сколько раз уже было использовано (по умолчанию 0).
    """

    name: str
    price: int
    heal_hp: int
    number_of_uses: int
    uses: int = field(default=0)

    def is_empty(self) -> bool:
        """Возвращает True, если лекарство больше нельзя использовать."""
        return self.uses >= self.number_of_uses

    def use(self) -> None:
        """Использовать лекарство (увеличить счётчик использований), иначе выбросить ошибку."""
        if self.is_empty():
            raise InvalidActionError("Лекарство закончилось.")
        self.uses += 1

    def __repr__(self) -> str:
        return (f"Medicine(name={self.name!r}, price={self.price}, "
                f"heal_hp={self.heal_hp}, number_of_uses={self.number_of_uses}, uses={self.uses})")