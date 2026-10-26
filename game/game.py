# game/game.py
from abc import ABC, abstractmethod
from typing import List

from .clicker import AbstractClicker
from .exceptions import GameOverError, InvalidActionError, NotEnoughMoneyError
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: List[Food],
        all_medicine: List[Medicine],
    ) -> None:
        pass

    @abstractmethod
    def work(self) -> int:
        pass

    @abstractmethod
    def buy_food(self, index: int) -> None:
        pass

    @abstractmethod
    def buy_medicine(self, index: int) -> None:
        pass

    @abstractmethod
    def feed_tamagochi(self, index: int) -> None:
        pass

    @abstractmethod
    def heal_tamagochi(self, index: int) -> None:
        pass

    @abstractmethod
    def rest_tamagochi(self) -> None:
        pass

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        pass

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        pass

    @property
    @abstractmethod
    def food(self) -> List[Food]:
        pass

    @property
    @abstractmethod
    def medicine(self) -> List[Medicine]:
        pass


class SimpleGame(AbstractGame):
    """Основная логика игры: управление ресурсами и действиями."""

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: List[Food],
        all_medicine: List[Medicine],
    ) -> None:
        self._tamagochi = tamagochi
        self._clicker = clicker
        # Копируем списки, чтобы не мутировать исходные
        self._all_food = list(all_food)
        self._all_medicine = list(all_medicine)
        self._coins = 100  # стартовые монеты
        self._inventory_food: List[Food] = []
        self._inventory_medicine: List[Medicine] = []

    def _ensure_alive(self) -> None:
        if not self._tamagochi.is_alive():
            raise GameOverError("Игра окончена.")

    def work(self) -> int:
        """Имитирует работу: использует кликер для получения монет."""
        self._ensure_alive()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        return income

    def buy_food(self, index: int) -> None:
        """Покупает еду по индексу из доступного ассортимента."""
        self._ensure_alive()

        if index < 0 or index >= len(self._all_food):
            raise InvalidActionError("Некорректный индекс товара.")

        food_to_buy = self._all_food[index]

        if self._coins < food_to_buy.price:
            raise NotEnoughMoneyError("Недостаточно монет.")

        self._coins -= food_to_buy.price
        self._inventory_food.append(food_to_buy)

    def buy_medicine(self, index: int) -> None:
        """Покупает лекарство по индексу из доступного ассортимента."""
        self._ensure_alive()

        if index < 0 or index >= len(self._all_medicine):
            raise InvalidActionError("Некорректный индекс товара.")

        med_to_buy = self._all_medicine[index]

        if self._coins < med_to_buy.price:
            raise NotEnoughMoneyError("Недостаточно монет.")

        self._coins -= med_to_buy.price
        self._inventory_medicine.append(med_to_buy)

    def feed_tamagochi(self, index: int) -> None:
        """Кормит питомца едой из инвентаря по указанному индексу."""
        self._ensure_alive()

        if not self._inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")

        if index < 0 or index >= len(self._inventory_food):
            raise InvalidActionError("Некорректный индекс еды в инвентаре.")

        food = self._inventory_food.pop(index)
        self._tamagochi.feed(food)

    def heal_tamagochi(self, index: int) -> None:
        """Лечит питомца лекарством из инвентаря по указанному индексу."""
        self._ensure_alive()

        if not self._inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")

        if index < 0 or index >= len(self._inventory_medicine):
            raise InvalidActionError("Некорректный индекс лекарства в инвентаре.")

        medicine = self._inventory_medicine[index]
        if medicine.is_empty():
            # Ищем первое непустое лекарство
            found = None
            for med in self._inventory_medicine:
                if not med.is_empty():
                    found = med
                    break
            if found is None:
                raise InvalidActionError("Все лекарства закончились.")
            medicine = found

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

    @property
    def food(self) -> List[Food]:
        return self._inventory_food

    @property
    def medicine(self) -> List[Medicine]:
        return self._inventory_medicine
