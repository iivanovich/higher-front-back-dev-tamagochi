from abc import ABC, abstractmethod
from copy import deepcopy

from .clicker import AbstractClicker
from .exceptions import GameOverError, InvalidActionError, NotEnoughMoney
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    """Базовый интерфейс для управления игрой Тамагочи."""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Инициализирует игру с компонентами: питомцем, кликером и каталогами товаров."""

    @abstractmethod
    def work(self) -> int:
        """Выполняет действие «работа»: получает монеты и обновляет состояние питомца."""

    @abstractmethod
    def buy_food(self) -> None:
        """Покупает еду (автоматически выбирает первый доступный товар)."""

    @abstractmethod
    def buy_medicine(self) -> None:
        """Покупает лекарство (автоматически выбирает первый доступный товар)."""

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Кормит питомца (автоматически использует первый предмет из инвентаря)."""

    @abstractmethod
    def heal_tamagochi(self) -> None:
        """Лечит питомца (автоматически использует первый предмет из инвентаря)."""

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Позволяет питомцу отдохнуть."""

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Играет с питомцем."""

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        """Возвращает словарь со статусом игры."""

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """Возвращает список еды в инвентаре."""

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """Возвращает список лекарств в инвентаре."""


class SimpleGame(AbstractGame):
    """Конкретная реализация игры."""

    START_COINS = 100

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._all_food = list(all_food)
        self._all_medicine = list(all_medicine)
        self._coins = self.START_COINS
        self._inventory_food: list[Food] = []
        self._inventory_medicine: list[Medicine] = []

    def _ensure_alive(self) -> None:
        if not self._tamagochi.is_alive():
            raise GameOverError("Игра окончена: питомец умер.")

    def work(self) -> int:
        self._ensure_alive()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        self._tamagochi.update()
        return income

    def buy_food(self) -> None:
        """Покупает первый доступный предмет из каталога."""
        self._ensure_alive()

        if not self._all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")

        food_to_buy = self._all_food[0]  # Берём первый предмет

        if self._coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self._coins -= food_to_buy.price
        self._inventory_food.append(deepcopy(food_to_buy))
        self._tamagochi.update()

    def buy_medicine(self) -> None:
        """Покупает первое доступное лекарство из каталога."""
        self._ensure_alive()

        if not self._all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")

        med_to_buy = self._all_medicine[0]  # Берём первое лекарство

        if self._coins < med_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self._coins -= med_to_buy.price
        self._inventory_medicine.append(deepcopy(med_to_buy))
        self._tamagochi.update()

    def feed_tamagochi(self) -> None:
        """Кормит питомца первым предметом из инвентаря."""
        self._ensure_alive()

        if not self._inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")

        food = self._inventory_food.pop(0)  # Удаляем и берём первый предмет
        self._tamagochi.feed(food)
        self._tamagochi.update()

    def heal_tamagochi(self) -> None:
        """Лечит питомца первым предметом из инвентаря."""
        self._ensure_alive()

        if not self._inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")

        medicine = self._inventory_medicine[0]

        if medicine.is_empty():
            # Если первое лекарство пустое, пробуем найти непустое
            found = None
            for i, med in enumerate(self._inventory_medicine):
                if not med.is_empty():
                    found = i
                    break
            
            if found is None:
                raise InvalidActionError("Все лекарства закончились.")
            
            medicine = self._inventory_medicine.pop(found)
        else:
            # Просто берём первое, если оно не пустое
            self._inventory_medicine.pop(0)

        self._tamagochi.heal(medicine)
        self._tamagochi.update()

    def rest_tamagochi(self) -> None:
        self._ensure_alive()
        self._tamagochi.rest()
        self._tamagochi.update()

    def play_with_tamagochi(self) -> None:
        self._ensure_alive()
        self._tamagochi.play()
        self._tamagochi.update()

    def get_status(self) -> dict[str, int]:
        status = self._tamagochi.status()
        status["coins"] = self._coins
        return status

    @property
    def food(self) -> list[Food]:
        return list(self._inventory_food)

    @property
    def medicine(self) -> list[Medicine]:
        return list(self._inventory_medicine)
