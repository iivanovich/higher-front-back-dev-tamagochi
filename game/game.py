import copy
from abc import ABC, abstractmethod

from .clicker import AbstractClicker
from .exceptions import InvalidActionError, NotEnoughMoney, TamagochiIsGone
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
        self._all_food = all_food
        self._all_medicine = all_medicine
        self._coins = 100
        # Пустые списки инвентаря — никаких «стартовых» списков
        self._inventory_food: list[Food] = []
        self._inventory_medicine: list[Medicine] = []

    @property
    def all_food(self) -> list[Food]:
        return self._all_food

    @property
    def all_medicine(self) -> list[Medicine]:
        return self._all_medicine

    @property
    def food(self) -> list[Food]:
        # Возвращаем копию, чтобы тест не мог сломать состояние изнутри
        return copy.deepcopy(self._inventory_food)

    @property
    def medicine(self) -> list[Medicine]:
        return copy.deepcopy(self._inventory_medicine)

    @property
    def coins(self) -> int:
        return self._coins

    @coins.setter
    def coins(self, value: int) -> None:
        self._coins = value

    def _ensure_alive(self) -> None:
        if not self._tamagochi.is_alive():
            raise TamagochiIsGone("Питомец умер, игра окончена.")

    def work(self) -> int:
        self._ensure_alive()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        return income

    def buy_food(self, index: int = 0) -> None:
        self._ensure_alive()
        if not self._all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")
        if index < 0 or index >= len(self._all_food):
            raise InvalidActionError("Некорректный индекс еды.")

        food_to_buy = self._all_food[index]
        if self._coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет для покупки еды.")

        self._coins -= food_to_buy.price
        # Добавляем один объект (копию), а не список
        self._inventory_food.append(copy.deepcopy(food_to_buy))

    def buy_medicine(self, index: int = 0) -> None:
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

    def feed_tamagochi(self, index: int = 0) -> None:
        self._ensure_alive()
        if not self._inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")
        if index < 0 or index >= len(self._inventory_food):
            raise InvalidActionError("Некорректный индекс еды в инвентаре.")

        # Удаляем и получаем предмет за один шаг
        food = self._inventory_food.pop(index)
        self._tamagochi.feed(food)

    def heal_tamagochi(self, index: int = 0) -> None:
        self._ensure_alive()
        if not self._inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")
        if index < 0 or index >= len(self._inventory_medicine):
            raise InvalidActionError("Некорректный индекс лекарства в инвентаре.")

        medicine = self._inventory_medicine[index]
        if medicine.is_empty():
            raise InvalidActionError("Выбранное лекарство закончилось.")

        self._tamagochi.heal(medicine)

        # Если после использования лекарство стало пустым — удаляем его из инвентаря
        if medicine.is_empty():
            # Безопасное удаление: если индекс всё ещё валиден — по индексу, иначе по значению
            if 0 <= index < len(self._inventory_medicine):
                # Проверяем, что тот же самый объект всё ещё на этом месте
                if self._inventory_medicine[index] is medicine:
                    self._inventory_medicine.pop(index)
                else:
                    # Объект сдвинулся (редкий случай), удаляем по значению
                    if medicine in self._inventory_medicine:
                        self._inventory_medicine.remove(medicine)
            else:
                if medicine in self._inventory_medicine:
                    self._inventory_medicine.remove(medicine)

    def rest_tamagochi(self) -> None:
        self._ensure_alive()
        self._tamagochi.rest()

    def play_with_tamagochi(self) -> None:
        self._ensure_alive()
        self._tamagochi.play()

    def get_status(self) -> dict[str, int]:
        status = self._tamagochi.status()
        status["coins"] = self._coins
        return status
