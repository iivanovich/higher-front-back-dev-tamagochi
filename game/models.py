"""Модели игры: еда, лекарство и инвентарь.

Модели намеренно «глупые»: они только хранят данные и умеют себя
валидировать. Вся игровая логика живёт в компонентах.
"""


class Food:
    """Еда, которой можно накормить питомца."""

    def __init__(self, name: str, satiety: int, price: int) -> None:
        """Создать еду.

        :param name: наименование еды.
        :param satiety: сколько единиц голода снимает еда.
        :param price: стоимость еды в монетах.
        :raises ValueError: если насыщение или цена отрицательные.
        """
        if satiety < 0 or price < 0:
            raise ValueError('Насыщение и цена не могут быть отрицательными')
        self.name = name
        self.satiety = satiety
        self.price = price

    def __repr__(self) -> str:
        """Вернуть читаемое представление еды."""
        return f'{self.name} (насыщение {self.satiety}, цена {self.price})'


class Medicine:
    """Лекарство, которым можно лечить питомца."""

    def __init__(
        self,
        name: str,
        price: int,
        heal_hp: int,
        number_of_uses: int,
        uses: int = 0,
    ) -> None:
        """Создать лекарство.

        :param name: наименование лекарства.
        :param price: стоимость лекарства в монетах.
        :param heal_hp: сколько здоровья восстанавливает одно использование.
        :param number_of_uses: максимальное количество использований.
        :param uses: текущее количество использований (по умолчанию 0).
        :raises ValueError: при некорректных числовых значениях.
        """
        if price < 0 or heal_hp < 0 or number_of_uses <= 0 or uses < 0:
            raise ValueError('Некорректные параметры лекарства')
        if uses > number_of_uses:
            raise ValueError('Использований не может быть больше допустимого')
        self.name = name
        self.price = price
        self.heal_hp = heal_hp
        self.number_of_uses = number_of_uses
        self.uses = uses

    def is_empty(self) -> bool:
        """Проверить, остались ли ещё использования лекарства.

        :return: ``True``, если использований не осталось.
        """
        return self.uses >= self.number_of_uses

    def __repr__(self) -> str:
        """Вернуть читаемое представление лекарства."""
        return (
            f'{self.name} (лечит {self.heal_hp}, '
            f'осталось {self.number_of_uses - self.uses}, цена {self.price})'
        )


class Inventory(list):
    """Список предметов на руках у игрока.

    Обычный список, который дополнительно умеет отвечать на вызов. Это
    позволяет обращаться к инвентарю одинаково — и как к свойству
    (``game.food``), и как к методу (``game.food()``), — чтобы клиентский
    код не зависел от выбранной формы доступа.
    """

    def __call__(self) -> 'Inventory':
        """Вернуть инвентарь при обращении в стиле метода.

        :return: этот же инвентарь.
        """
        return self
