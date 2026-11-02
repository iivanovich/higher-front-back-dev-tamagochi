from abc import ABC, abstractmethod

from .clicker import AbstractClicker
from .constants import START_COINS
from .exceptions import GameOverError, InvalidActionError, NotEnoughMoney
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
        pass

    @abstractmethod
    def work(self) -> int:
        pass

    @abstractmethod
    def buy_food(self, idx: int = 0) -> None:
        pass

    @abstractmethod
    def buy_medicine(self, idx: int = 0) -> None:
        pass

    @abstractmethod
    def feed_tamagochi(self, idx: int = 0) -> None:
        pass

    @abstractmethod
    def heal_tamagochi(self, idx: int = 0) -> None:
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
    def food(self) -> list[Food]:
        pass

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        pass


class SimpleGame(AbstractGame):
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
        self._coins = START_COINS
        self._inventory_food: list[Food] = []
        self._inventory_medicine: list[Medicine] = []

    @property
    def tamagochi(self):
        return self._tamagochi

    def _ensure_alive(self) -> None:
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена.")

    def work(self) -> int:
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
        food_src = self._all_food[idx]
        if self._coins < food_src.price:
            raise NotEnoughMoney("Недостаточно монет.")
        self._coins -= food_src.price
        # Создание нового объекта Food - важно!
        self._inventory_food.append(
            Food(name=food_src.name, satiety=food_src.satiety, price=food_src.price)
        )

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
        # Создаём новый объект Medicine, не ссылку!
        self._inventory_medicine.append(Medicine(
            name=med_src.name, price=med_src.price,
            heal_hp=med_src.heal_hp, number_of_uses=med_src.number_of_uses
        ))

    def feed_tamagochi(self, idx: int = 0) -> None:
        self._ensure_alive()
        if not self._inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")
        if not 0 <= idx < len(self._inventory_food):
            raise InvalidActionError("Некорректный выбор еды для кормления.")
        food = self._inventory_food[idx]
        self.tamagochi.feed(food)
        # Удаляем только выбранный элемент!
        del self._inventory_food[idx]
        self.tamagochi.update()

    def heal_tamagochi(self, idx: int = 0) -> None:
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
        self._ensure_alive()
        self.tamagochi.rest()
        self.tamagochi.update()

    def play_with_tamagochi(self) -> None:
        self._ensure_alive()
        self.tamagochi.play()
        self.tamagochi.update()

    def get_status(self) -> dict[str, int]:
        status = self.tamagochi.status()
        status['coins'] = self._coins
        return status

    @property
    def food(self) -> list[Food]:
        return list(self._inventory_food)

    @property
    def medicine(self) -> list[Medicine]:
        return list(self._inventory_medicine)