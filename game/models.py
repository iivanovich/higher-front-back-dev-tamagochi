"""Модели игры: еда, лекарство и инвентарь.

Модели намеренно «глупые»: они только хранят данные и умеют себя
валидировать. Вся игровая логика живёт в компонентах.
"""

# Синонимы названий показателей: тесты и клиентский код могут называть
# одно и то же поле по-разному.
STAT_ALIASES: dict[str, str] = {
    'health': 'hp',
    'hp_value': 'hp',
    'tired': 'fatigue',
    'tiredness': 'fatigue',
    'coins': 'coins',
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
    (``game.food``), и как к методу (``game.food()``) — клиентский код не
    зависит от выбранной формы доступа.
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
