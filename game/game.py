"""Сущность игры: связывает питомца, кликер и ресурсы.

Класс игры знает только контракты компонентов. Что именно происходит
внутри ``click`` или ``feed`` — его не касается: он отдаёт команды, ведёт
кошелёк и следит за состоянием партии.
"""

from abc import ABC, abstractmethod

from game import constants
from game.clicker import AbstractClicker
from game.exceptions import (
    EmptyInventory,
    GameError,
    InvalidChoice,
    NotEnoughMoney,
)
from game.models import Food, Inventory, Medicine, Status
from game.tamagochi import AbstractTamagochi

# Настройки читаются из модуля констант, но имеют запасные значения:
# игра должна запускаться даже с устаревшей версией constants.py.
START_COINS = getattr(constants, 'START_COINS', 0)
START_GAME_COINS = getattr(constants, 'START_GAME_COINS', 200)
GAME_OVER_MESSAGE = getattr(
    constants, 'GAME_OVER_MESSAGE', 'Игра окончена: питомец погиб'
)

# Любой способ указать предмет: номер, название или сам объект.
ItemChoice = int | str | Food | Medicine | None


class AbstractGame(ABC):
    """Интерфейс игры."""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Инициализировать игру.

        :param tamagochi: питомец.
        :param clicker: кликер, выдающий монеты.
        :param all_food: доступный в магазине ассортимент еды.
        :param all_medicine: доступный в магазине ассортимент лекарств.
        """

    @abstractmethod
    def work(self) -> int:
        """Пойти на работу: заработать монеты кликом."""

    @abstractmethod
    def buy_food(self) -> None:
        """Купить еду."""

    @abstractmethod
    def buy_medicine(self) -> None:
        """Купить лекарство."""

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Покормить питомца едой из сумки."""

    @abstractmethod
    def heal_tamagochi(self) -> None:
        """Вылечить питомца лекарством из сумки."""

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Дать питомцу отдохнуть."""

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Поиграть с питомцем."""

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        """Получить статус игры."""

    @abstractmethod
    def food(self) -> list[Food]:
        """Вернуть сумку с едой."""

    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """Вернуть сумку с лекарствами."""


class SimpleGame(AbstractGame):
    """Конкретная реализация игры.

    Игровые ошибки (нехватка монет, пустая сумка, неверный выбор) не
    выбрасываются наружу: они перехватываются и печатаются сообщением,
    чтобы игровой цикл продолжался.
    """

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food] | None = None,
        all_medicine: list[Medicine] | None = None,
    ) -> None:
        """Создать игру.

        :param tamagochi: питомец.
        :param clicker: кликер, выдающий монеты.
        :param all_food: ассортимент магазина еды.
        :param all_medicine: ассортимент магазина лекарств.
        """
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._store_food = list(all_food or [])
        self._store_medicine = list(all_medicine or [])
        self._bag_food = Inventory()
        self._bag_medicine = Inventory()
        self._coins = START_GAME_COINS
        self._is_over = False

    @property
    def tamagochi(self) -> AbstractTamagochi:
        """Вернуть питомца."""
        return self._tamagochi

    @property
    def clicker(self) -> AbstractClicker:
        """Вернуть кликер."""
        return self._clicker

    @property
    def coins(self) -> int:
        """Вернуть количество монет в кошельке игры."""
        return self._coins

    @property
    def food_store(self) -> list[Food]:
        """Вернуть ассортимент еды в магазине."""
        return list(self._store_food)

    @property
    def medicine_store(self) -> list[Medicine]:
        """Вернуть ассортимент лекарств в магазине."""
        return list(self._store_medicine)

    @property
    def food(self) -> list[Food]:
        """Вернуть сумку с едой."""
        return self._bag_food

    @property
    def medicine(self) -> list[Medicine]:
        """Вернуть сумку с лекарствами."""
        return self._bag_medicine

    def work(self) -> int:
        """Пойти на работу и заработать монеты.

        Обновление состояния питомца выполняет вызывающий код (игровой
        цикл), чтобы за один ход происходил ровно один тик.

        :return: сколько монет заработано за клик.
        """
        if not self._check_alive():
            return START_COINS
        self._clicker.click()
        income = self._clicker.income_per_click()
        income = int(income() if callable(income) else income)
        self._coins += income
        return income

    def buy_food(
        self,
        item: ItemChoice = None,
        *,
        index: int | None = None,
        name: str | None = None,
    ) -> None:
        """Купить еду и положить её в сумку.

        :param item: номер, название или сам объект еды.
        :param index: номер товара в магазине (альтернатива ``item``).
        :param name: название товара (альтернатива ``item``).
        """
        if not self._check_alive():
            return
        try:
            food = self._store_food[
                self._pick(self._store_food, _merge(item, index, name), 'еды')
            ]
            self._pay(food.price)
            self._bag_food.append(food)
            print(f'Куплено: {food.name}')
        except GameError as error:
            print(f'Не удалось купить: {error}')

    def buy_medicine(
        self,
        item: ItemChoice = None,
        *,
        index: int | None = None,
        name: str | None = None,
    ) -> None:
        """Купить лекарство и положить его в сумку.

        :param item: номер, название или сам объект лекарства.
        :param index: номер товара в магазине (альтернатива ``item``).
        :param name: название товара (альтернатива ``item``).
        """
        if not self._check_alive():
            return
        try:
            medicine = self._store_medicine[
                self._pick(
                    self._store_medicine,
                    _merge(item, index, name),
                    'лекарств',
                )
            ]
            self._pay(medicine.price)
            self._bag_medicine.append(medicine)
            print(f'Куплено: {medicine.name}')
        except GameError as error:
            print(f'Не удалось купить: {error}')

    def feed_tamagochi(
        self,
        item: ItemChoice = None,
        *,
        index: int | None = None,
        name: str | None = None,
    ) -> None:
        """Покормить питомца едой из сумки.

        :param item: номер, название или сам объект еды из сумки.
        :param index: номер предмета в сумке (альтернатива ``item``).
        :param name: название предмета (альтернатива ``item``).
        """
        if not self._check_alive():
            return
        try:
            position = self._pick(
                self._bag_food, _merge(item, index, name), 'еды в сумке'
            )
            food = self._bag_food[position]
            self._tamagochi.feed(food)
            self._bag_food.pop(position)
            print(f'Питомец съел: {food.name}')
        except GameError as error:
            print(f'Не удалось покормить: {error}')

    def heal_tamagochi(
        self,
        item: ItemChoice = None,
        *,
        index: int | None = None,
        name: str | None = None,
    ) -> None:
        """Вылечить питомца лекарством из сумки.

        :param item: номер, название или сам объект лекарства из сумки.
        :param index: номер предмета в сумке (альтернатива ``item``).
        :param name: название предмета (альтернатива ``item``).
        """
        if not self._check_alive():
            return
        try:
            position = self._pick(
                self._bag_medicine,
                _merge(item, index, name),
                'лекарств в сумке',
            )
            medicine = self._bag_medicine[position]
            self._tamagochi.heal(medicine)
            if medicine.is_empty():
                self._bag_medicine.pop(position)
            print(f'Питомец вылечен: {medicine.name}')
        except GameError as error:
            print(f'Не удалось вылечить: {error}')

    def rest_tamagochi(self) -> None:
        """Дать питомцу отдохнуть."""
        if not self._check_alive():
            return
        try:
            self._tamagochi.rest()
        except GameError as error:
            print(error)

    def play_with_tamagochi(self) -> None:
        """Поиграть с питомцем."""
        if not self._check_alive():
            return
        try:
            self._tamagochi.play()
        except GameError as error:
            print(error)

    def get_status(self) -> dict[str, int]:
        """Собрать полный статус партии.

        :return: показатели питомца (``hunger``, ``fatigue``, ``hp``,
            ``energy``), ``coins`` и ``game_over``.
        """
        status = Status(self._tamagochi.status())
        status['coins'] = self._coins
        status['game_over'] = int(self.is_over())
        return status

    def is_alive(self) -> bool:
        """Проверить, жив ли питомец.

        :return: ``True``, если питомец ещё жив.
        """
        return self._tamagochi.is_alive()

    def is_over(self) -> bool:
        """Проверить, закончилась ли игра.

        :return: ``True``, если питомец погиб.
        """
        if not self._tamagochi.is_alive():
            self._is_over = True
        return self._is_over

    def __repr__(self) -> str:
        """Вернуть читаемое представление игры."""
        return (
            f'SimpleGame(tamagochi={self._tamagochi!r}, '
            f'food={len(self._bag_food)}, medicine={len(self._bag_medicine)}, '
            f'coins={self._coins})'
        )

    def _check_alive(self) -> bool:
        """Проверить, что питомец жив и игра продолжается.

        :return: ``True``, если действия доступны.
        """
        if self.is_over():
            print(GAME_OVER_MESSAGE)
            return False
        return True

    def _pay(self, amount: int) -> None:
        """Списать монеты за покупку.

        :param amount: стоимость покупки.
        :raises NotEnoughMoney: если монет не хватает.
        """
        if amount > self._coins:
            raise NotEnoughMoney(
                f'Нужно {amount} монет, а в кошельке только {self._coins}'
            )
        self._coins -= amount

    @staticmethod
    def _pick(
        items: list[Food] | list[Medicine],
        item: ItemChoice,
        what: str,
    ) -> int:
        """Определить номер предмета в списке.

        Поддерживается выбор по номеру, по названию и по самому объекту,
        поэтому вызывающий код может не знать, в каком виде хранится выбор.

        :param items: список доступных предметов.
        :param item: номер, название, объект предмета или ``None``.
        :param what: название категории для сообщений об ошибке.
        :return: индекс предмета в списке.
        :raises EmptyInventory: если список пуст.
        :raises InvalidChoice: если предмет не найден.
        """
        if not items:
            raise EmptyInventory(f'Нет доступной {what}')
        if item is None:
            return START_COINS
        if isinstance(item, int):
            if not -len(items) <= item < len(items):
                raise InvalidChoice(f'Нет предмета с номером {item}')
            return item % len(items)
        if isinstance(item, str):
            for number, candidate in enumerate(items):
                if candidate.name == item:
                    return number
            raise InvalidChoice(f'Нет предмета с названием {item}')
        for number, candidate in enumerate(items):
            if candidate is item:
                return number
        raise InvalidChoice(f'Такого предмета нет среди {what}')


def _merge(
    item: ItemChoice,
    index: int | None,
    name: str | None,
) -> ItemChoice:
    """Свести разные способы выбора предмета к одному значению.

    :param item: основной аргумент выбора.
    :param index: номер предмета, если передан.
    :param name: название предмета, если передано.
    :return: непустой способ выбора или ``None``.
    """
    if item is not None:
        return item
    if index is not None:
        return index
    return name
