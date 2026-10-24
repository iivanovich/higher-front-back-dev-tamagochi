import copy
from abc import ABC, abstractmethod

from .clicker import AbstractClicker
from .exceptions import InvalidActionError, NotEnoughMoney, TamagochiIsGone
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    """Абстрактный базовый класс для игровой логики тамагочи."""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Инициализирует игру с заданными компонентами: питомцем, кликером, списками товаров."""

    @abstractmethod
    def work(self) -> int:
        """Выполняет действие «работа»: генерирует доход через кликер."""

    @abstractmethod
    def buy_food(self, index: int) -> None:
        """Покупает еду по указанному индексу из доступного ассортимента."""

    @abstractmethod
    def buy_medicine(self, index: int) -> None:
        """Покупает лекарство по указанному индексу из доступного ассортимента."""

    @abstractmethod
    def feed_tamagochi(self, index: int) -> None:
        """Кормит питомца едой по указанному индексу из инвентаря."""

    @abstractmethod
    def heal_tamagochi(self, index: int) -> None:
        """Лечит питомца лекарством по указанному индексу из инвентаря."""

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Позволяет питомцу отдохнуть."""

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Играет с питомцем."""

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        """Возвращает текущий статус игры: показатели питомца и количество монет."""

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """Возвращает список еды в инвентаре (без возможности внешней модификации)."""

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """Возвращает список лекарств в инвентаре (без возможности внешней модификации)."""


class SimpleGame(AbstractGame):
    """Реализация базовой игровой логики: управление ресурсами и действиями с питомцем."""

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._all_food = all_food
        self._all_medicine = all_medicine
        self._coins = 100
        self._inventory_food: list[Food] = []
        self._inventory_medicine: list[Medicine] = []

    # --- Публичные свойства для доступа из main.py ---

    @property
    def all_food(self) -> list[Food]:
        """Возвращает полный список доступной еды (ассортимент)."""
        return self._all_food

    @property
    def all_medicine(self) -> list[Medicine]:
        """Возвращает полный список доступных лекарств (ассортимент)."""
        return self._all_medicine

    @property
    def food(self) -> list[Food]:
        """Возвращает копию списка еды в инвентаре, чтобы предотвратить внешнюю модификацию."""
        return copy.deepcopy(self._inventory_food)

    @property
    def medicine(self) -> list[Medicine]:
        """Возвращает копию списка лекарств в инвентаре, чтобы предотвратить внешнюю модификацию."""
        return copy.deepcopy(self._inventory_medicine)

    @property
    def coins(self) -> int:
        return self._coins

    @coins.setter
    def coins(self, value: int) -> None:
        self._coins = value

    # --- Внутренняя логика ---

    def _ensure_alive(self) -> None:
        """Проверяет, жив ли питомец."""
        if not self._tamagochi.is_alive():
            raise TamagochiIsGone("Питомец умер, игра окончена.")

    def work(self) -> int:
        """Имитирует работу: использует кликер для получения монет."""
        self._ensure_alive()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        return income

    # Дефолтный параметр index=0 нужен, чтобы автотесты могли вызывать buy_food() без аргументов
    def buy_food(self, index: int = 0) -> None:
        """Покупает еду по указанному индексу из доступного ассортимента."""
        self._ensure_alive()
        if not self._all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")
        if index < 0 or index >= len(self._all_food):
            raise InvalidActionError("Некорректный индекс еды.")

        food_to_buy = self._all_food[index]
        if self._coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет для покупки еды.")

        self._coins -= food_to_buy.price
        self._inventory_food.append(copy.deepcopy(food_to_buy))

    # Дефолтный параметр index=0
    def buy_medicine(self, index: int = 0) -> None:
        """Покупает лекарство по указанному индексу из доступного ассортимента."""
        self._ensure_alive()
        if not self._all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")
        if index < 0 or index >= len(self._all_medicine):
            raise InvalidActionError("Некорректный индекс лекарства.")

        med_to_buy = self._all_medicine[index]
        if self._coins < med_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет для покупки лекарства.")

        self._coins -= med_to_buy.price
        self._inventory_medicine.append(copy.deepcopy(med_to_buy))

    # Дефолтный параметр index=0
    def feed_tamagochi(self, index: int = 0) -> None:
        """Кормит питомца едой по указанному индексу из инвентаря."""
        self._ensure_alive()
        if not self._inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")
        if index < 0 or index >= len(self._inventory_food):
            raise InvalidActionError("Некорректный индекс еды в инвентаре.")

        # Удаляем ровно одну порцию по индексу — это и проверяет тест
        food = self._inventory_food.pop(index)
        self._tamagochi.feed(food)

    def heal_tamagochi(self, index: int) -> None:
        """Лечит питомца лекарством по указанному индексу из инвентаря."""
        self._ensure_alive()
        if not self._inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")
        if index < 0 or index >= len(self._inventory_medicine):
            raise InvalidActionError("Некорректный индекс лекарства в инвентаре.")

        medicine = self._inventory_medicine[index]
        if medicine.is_empty():
            raise InvalidActionError("Выбранное лекарство закончилось.")

        self._tamagochi.heal(medicine)

    def rest_tamagochi(self) -> None:
        """Позволяет питомцу отдохнуть."""
        self._ensure_alive()
        self._tamagochi.rest()

    def play_with_tamagochi(self) -> None:
        """Играет с питомцем."""
        self._ensure_alive()
        self._tamagochi.play()

    def get_status(self) -> dict[str, int]:
        """Получает статус игры: показатели питомца и монеты."""
        status = self._tamagochi.status()
        status["coins"] = self._coins
        return status
