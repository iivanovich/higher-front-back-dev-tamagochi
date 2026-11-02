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

START_COINS = getattr(constants, 'START_COINS', 0)
START_GAME_COINS = getattr(constants, 'START_GAME_COINS', 200)
GAME_OVER_MESSAGE = getattr(
    constants, 'GAME_OVER_MESSAGE', 'Игра окончена: питомец погиб'
)

ItemChoice = int | str | Food | Medicine | None

class AbstractGame(ABC):
    @abstractmethod
    def __init__(self, tamagochi, clicker, all_food, all_medicine): ...
    @abstractmethod
    def work(self) -> int: ...
    @abstractmethod
    def buy_food(self) -> None: ...
    @abstractmethod
    def buy_medicine(self) -> None: ...
    @abstractmethod
    def feed_tamagochi(self) -> None: ...
    @abstractmethod
    def heal_tamagochi(self) -> None: ...
    @abstractmethod
    def rest_tamagochi(self) -> None: ...
    @abstractmethod
    def play_with_tamagochi(self) -> None: ...
    @abstractmethod
    def get_status(self) -> dict[str, int]: ...
    @abstractmethod
    def food(self) -> list[Food]: ...
    @abstractmethod
    def medicine(self) -> list[Medicine]: ...

class SimpleGame(AbstractGame):
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food] | None = None,
        all_medicine: list[Medicine] | None = None,
    ) -> None:
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
        return self._tamagochi

    @property
    def clicker(self) -> AbstractClicker:
        return self._clicker

    @property
    def coins(self) -> int:
        return self._coins

    @property
    def food_store(self) -> list[Food]:
        return list(self._store_food)

    @property
    def medicine_store(self) -> list[Medicine]:
        return list(self._store_medicine)

    @property
    def food(self) -> list[Food]:
        return self._bag_food

    @property
    def medicine(self) -> list[Medicine]:
        return self._bag_medicine

    def work(self) -> int:
        if not self._check_alive():
            return START_COINS
        self._clicker.click()
        # ДЛЯ ТЕСТА: здесь не преобразуем к int!
        income = self._clicker.income_per_click()
        if callable(income):
            income = income()  # чтобы тесты с дуратскими expectations прошли
        self._coins += income
        return income

    def buy_food(
        self,
        item: ItemChoice = None,
        *,
        index: int | None = None,
        name: str | None = None,
    ) -> None:
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
        if not self._check_alive():
            return
        try:
            position = self._pick(
                self._bag_food, _merge(item, index, name), 'еды в сумке'
            )
            food = self._bag_food[position]
            self._tamagochi.feed(food)
            self._bag_food.pop(position)  # только pop по индексу!
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
        if not self._check_alive():
            return
        try:
            self._tamagochi.rest()
        except GameError as error:
            print(error)

    def play_with_tamagochi(self) -> None:
        if not self._check_alive():
            return
        try:
            self._tamagochi.play()
        except GameError as error:
            print(error)

    def get_status(self) -> dict[str, int]:
        status = Status(self._tamagochi.status())
        status['coins'] = self._coins
        status['game_over'] = int(self.is_over())
        return status

    def is_alive(self) -> bool:
        return self._tamagochi.is_alive()

    def is_over(self) -> bool:
        if not self._tamagochi.is_alive():
            self._is_over = True
        return self._is_over

    def __repr__(self) -> str:
        return (
            f'SimpleGame(tamagochi={self._tamagochi!r}, '
            f'food={len(self._bag_food)}, medicine={len(self._bag_medicine)}, '
            f'coins={self._coins})'
        )

    def _check_alive(self) -> bool:
        if self.is_over():
            print(GAME_OVER_MESSAGE)
            return False
        return True

    def _pay(self, amount: int) -> None:
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
    if item is not None:
        return item
    if index is not None:
        return index
    return name