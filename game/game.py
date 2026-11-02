import copy
from abc import ABC, abstractmethod
from copy import deepcopy

from .clicker import AbstractClicker
from .constants import START_COINS
from .exceptions import (
    GameOverError,
    InvalidActionError,
    NotEnoughMoney,
)
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """
        Создать игру с питомцем, кликером и доступными товарами.
        """

    @abstractmethod
    def work(self) -> int:
        """
        Пойти на работу.
        """

    @abstractmethod
    def buy_food(self, idx: int = 0) -> None:
        """
        Купить еду по индексу в списке all_food.
        """

    @abstractmethod
    def buy_medicine(self, idx: int = 0) -> None:
        """
        Купить лекарство по индексу в списке all_medicine.
        """

    @abstractmethod
    def feed_tamagochi(self, idx: int = 0) -> None:
        """
        Покормить питомца едой из инвентаря по индексу.
        """

    @abstractmethod
    def heal_tamagochi(self, idx: int = 0) -> None:
        """
        Вылечить питомца лекарством из инвентаря по индексу.
        """

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """
        Питомец отдыхает.
        """

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """
        Питомец играет.
        """

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        """
        Получение статуса игры.
        """

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """
        Еда в инвентаре.
        """

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """
        Лекарства в инвентаре.
        """


class SimpleGame(AbstractGame):
    """
    Основная логика игры: управление ресурсами и действиями.
    """

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        # защищённые поля
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._all_food = list(all_food)     # копия для безопасности
        self._all_medicine = list(all_medicine)
        self._coins = START_COINS
        self._inventory_food: list[Food] = []
        self._inventory_medicine: list[Medicine] = []

    @property
    def tamagochi(self):
        """Только для чтения, наружу отдаём интерфейс."""
        return self._tamagochi

    def _ensure_alive(self) -> None:
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена.")

    def work(self) -> int:
        """
        Имитирует работу: использует кликер для получения монет.
        """
        self._ensure_alive()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        self.tamagochi.update()
        return income

    def buy_food(self, idx: int = 0) -> None:
        self._ensure_alive()
        if not self._all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")
        if not 0 <= idx < len(self._all_food):
            raise InvalidActionError("Некорректный выбор еды.")
        food_to_buy = self._all_food[idx]
        if self._coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")
        self._coins -= food_to_buy.price
        self._inventory_food.append(copy.deepcopy(food_to_buy)) 

    def buy_medicine(self, idx: int = 0) -> None:
        """
        Покупает лекарство из списка доступных по индексу. Добавляется копия.
        """
        self._ensure_alive()
        if not self._all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")

        if not 0 <= idx < len(self._all_medicine):
            raise InvalidActionError("Некорректный выбор лекарства.")

        med_to_buy = self._all_medicine[idx]
        if self._coins < med_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")
        self._coins -= med_to_buy.price
        self._inventory_medicine.append(deepcopy(med_to_buy))

    def feed_tamagochi(self, idx: int = 0) -> None:
        self._ensure_alive()
        if not self._inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")
        if not 0 <= idx < len(self._inventory_food):
            raise InvalidActionError("Некорректный выбор еды для кормления.")
        food = self._inventory_food[idx]
        self.tamagochi.feed(food)
        del self._inventory_food[idx] 
        self.tamagochi.update()

    def heal_tamagochi(self, idx: int = 0) -> None:
        """
        Лечит питомца лекарством из инвентаря по индексу.
        """
        self._ensure_alive()
        if not self._inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")
        if not 0 <= idx < len(self._inventory_medicine):
            raise InvalidActionError("Некорректный выбор лекарства.")
        medicine = self._inventory_medicine[idx]
        if medicine.is_empty():
            raise InvalidActionError("Это лекарство закончилось.")
        self.tamagochi.heal(medicine)
        if medicine.is_empty():
            del self._inventory_medicine[idx]
        self.tamagochi.update()

    def rest_tamagochi(self) -> None:
        """
        Позволяет питомцу отдохнуть.
        """
        self._ensure_alive()
        self.tamagochi.rest()
        self.tamagochi.update()

    def play_with_tamagochi(self) -> None:
        """
        Играет с питомцем.
        """
        self._ensure_alive()
        self.tamagochi.play()
        self.tamagochi.update()

    def get_status(self) -> dict[str, int]:
        """
        Получает статус игры: показатели питомца и монеты.
        """
        status = self.tamagochi.status()
        status['coins'] = self._coins
        return status

    @property
    def food(self) -> list[Food]:
        """
        Возвращает список еды в инвентаре.
        """
        return list(self._inventory_food)

    @property
    def medicine(self) -> list[Medicine]:
        """
        Возвращает список лекарств в инвентаре.
        """
        return list(self._inventory_medicine)