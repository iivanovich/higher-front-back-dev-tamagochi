from abc import ABC, abstractmethod

from .constants import START_COINS
from .exceptions import GameOverError, InvalidActionError, NotEnoughMoney
from .models import Food, Medicine


class AbstractGame(ABC):
    @abstractmethod
    def __init__(self, tamagochi, clicker, all_food, all_medicine):
        """Интерфейс игры"""

    @abstractmethod
    def work(self) -> int:
        """Работа"""

    @abstractmethod
    def buy_food(self, idx: int = 0) -> None:
        """Покупка еды"""

    @abstractmethod
    def buy_medicine(self, idx: int = 0) -> None:
        """Покупка лекарства"""

    @abstractmethod
    def feed_tamagochi(self, idx: int = 0) -> None:
        """Кормление питомца"""

    @abstractmethod
    def heal_tamagochi(self, idx: int = 0) -> None:
        """Лечение питомца"""

    @abstractmethod
    def rest_tamagochi(self) -> None: ...

    @abstractmethod
    def play_with_tamagochi(self) -> None: ...

    @abstractmethod
    def get_status(self) -> dict[str, int]: ...

    @property
    @abstractmethod
    def food(self) -> list[Food]: ...

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]: ...


class SimpleGame(AbstractGame):
    """Основная логика игры"""

    def __init__(self, tamagochi, clicker, all_food, all_medicine):
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._all_food = list(all_food)
        self._all_medicine = list(all_medicine)
        self._coins = START_COINS
        self._inventory_food: list[Food] = []
        self._inventory_medicine: list[Medicine] = []

    @property
    def tamagochi(self):
        return self._tamagochi

    def _ensure_alive(self) -> None:
        if not self._tamagochi.is_alive():
            raise GameOverError("Игра окончена.")

    def work(self) -> int:
        self._ensure_alive()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        self._tamagochi.update()
        return income

    def buy_food(self, idx: int = 0) -> None:
        self._ensure_alive()
        if not self._all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")
        if not 0 <= idx < len(self._all_food):
            raise InvalidActionError("Некорректный выбор еды.")
        food_src = self._all_food[idx]
        if self._coins < food_src.price:
            raise NotEnoughMoney("Недостаточно монет.")
        self._coins -= food_src.price
        # кладём копию объекта!
        self._inventory_food.append(Food(name=food_src.name, satiety=food_src.satiety, price=food_src.price))

    def buy_medicine(self, idx: int = 0) -> None:
        self._ensure_alive()
        if not self._all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")
        if not 0 <= idx < len(self._all_medicine):
            raise InvalidActionError("Некорректный выбор лекарства.")
        med_src = self._all_medicine[idx]
        if self._coins < med_src.price:
            raise NotEnoughMoney("Недостаточно монет.")
        self._coins -= med_src.price
        self._inventory_medicine.append(Medicine(
            name=med_src.name, price=med_src.price,
            heal_hp=med_src.heal_hp, number_of_uses=med_src.number_of_uses
        ))

    def feed_tamagochi(self, idx: int = 0) -> None:
        self._ensure_alive()
        if not self._inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")
        if not 0 <= idx < len(self._inventory_food):
            raise InvalidActionError("Некорректный выбор еды.")
        food = self._inventory_food[idx]
        self._tamagochi.feed(food)
        del self._inventory_food[idx]
        self._tamagochi.update()

    def heal_tamagochi(self, idx: int = 0) -> None:
        self._ensure_alive()
        if not self._inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")
        if not 0 <= idx < len(self._inventory_medicine):
            raise InvalidActionError("Некорректный выбор лекарства.")
        medicine = self._inventory_medicine[idx]
        if medicine.is_empty():
            raise InvalidActionError("Это лекарство закончилось.")
        self._tamagochi.heal(medicine)
        if medicine.is_empty():
            del self._inventory_medicine[idx]
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