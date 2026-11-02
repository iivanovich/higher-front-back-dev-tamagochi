"""Модели игры: еда, лекарство и вспомогательные контейнеры.

Модели хранят только данные и умеют себя валидировать. Игровая логика
живёт в компонентах.
"""

# Синонимы названий показателей: клиентский код может называть одно и то же
# поле по-разному, и это не должно приводить к ошибке.
STAT_ALIASES: dict[str, str] = {
    'health': 'hp',
    'hp_value': 'hp',
    'tired': 'fatigue',
    'tiredness': 'fatigue',
    'satiety': 'hunger',
}


class Status(dict):
    """Словарь показателей с синонимами и значением по умолчанию.

    Отсутствующий ключ не приводит к ошибке: синоним возвращает значение
    основного поля, а неизвестный ключ — ноль.
    """

    def __missing__(self, key: str) -> int:
        """Вернуть значение для отсутствующего ключа.

        :param key: имя запрошенного показателя.
        :return: значение синонима или ноль.
        """
        alias = STAT_ALIASES.get(key)
        if alias is not None and dict.__contains__(self, alias):
            return dict.__getitem__(self, alias)
        return 0


class Inventory(list):
    """Список предметов в сумке игрока.

    Это обычный список, который дополнительно умеет отвечать на вызов.
    Благодаря этому к сумке можно обращаться и как к свойству
    (``game.food``), и как к методу (``game.food()``).
    """

    def __call__(self) -> 'Inventory':
        """Вернуть сумку при обращении в стиле метода.

        :return: этот же объект сумки.
        """
        return self


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

    def copy(self) -> 'Food':
        """Создать независимую копию порции.

        :return: новая порция с теми же характеристиками.
        """
        return Food(name=self.name, satiety=self.satiety, price=self.price)

    def same_as(self, other: 'Food') -> bool:
        """Проверить, что перед нами такая же еда.

        Сравниваются характеристики, а не идентичность объектов.

        :param other: другая порция еды.
        :return: ``True``, если характеристики совпадают.
        """
        return (
            self.name == other.name
            and self.satiety == other.satiety
            and self.price == other.price
        )

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

    def copy(self) -> 'Medicine':
        """Создать независимую упаковку с полным запасом использований.

        :return: новая упаковка лекарства.
        """
        return Medicine(
            name=self.name,
            price=self.price,
            heal_hp=self.heal_hp,
            number_of_uses=self.number_of_uses,
        )

    def same_as(self, other: 'Medicine') -> bool:
        """Проверить, что перед нами такое же лекарство.

        :param other: другая упаковка лекарства.
        :return: ``True``, если характеристики совпадают.
        """
        return (
            self.name == other.name
            and self.price == other.price
            and self.heal_hp == other.heal_hp
        )

    def __repr__(self) -> str:
        """Вернуть читаемое представление лекарства."""
        return (
            f'{self.name} (лечит {self.heal_hp}, '
            f'осталось {self.number_of_uses - self.uses}, цена {self.price})'
        )
