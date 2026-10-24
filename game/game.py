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
        
        # Инициализируем пустые списки инвентаря
        self._inventory_food: list[Food] = 
        self._inventory_medicine: list[Medicine] = 
        
        # ИСПРАВЛЕНИЕ: Не добавляем весь список как один элемент.
        # Если нужно стартовое количество еды, добавляем отдельные копии предметов.
        # В большинстве учебных задач стартовый инвентарь пуст, но если требуется стартовая еда:
        # for item in self._all_food:
        #     self._inventory_food.append(copy.deepcopy(item))
        # Сейчас оставляем пустым, чтобы тест на "покупку" и "кормление" работал корректно с нуля.

    @property
    def all_food(self) -> list[Food]:
        return self._all_food

    @property
    def all_medicine(self) -> list[Medicine]:
        return self._all_medicine

    @property
    def food(self) -> list[Food]:
        # Возвращаем копию, чтобы внешний код не мог изменить инвентарь напрямую
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
        # Добавляем копию предмета, а не ссылку на оригинал из магазина
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

        # Берем предмет и сразу удаляем из инвентаря
        food = self._inventory_food.pop(index)
        # Теперь food — это объект Food, у которого есть атрибут satiety
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

        # ИСПРАВЛЕНИЕ ДЛЯ ТЕСТА: Если лекарство стало пустым после использования, удаляем его из инвентаря
        if medicine.is_empty():
            # Удаляем по индексу. Так как мы взяли объект по индексу выше, индекс актуален,
            # но нужно быть осторожным, если логика is_empty() меняет состояние внутри heal.
            # В вашем коде heal вызывает medicine.use(), который меняет счетчик.
            # Проверяем снова и удаляем, если пусто.
            if medicine.is_empty():
                # Находим актуальный индекс, так как список мог измениться (хотя здесь мы только читаем)
                # Проще удалить по значению, если объекты сравнимы, или по индексу, если уверены.
                # Самый безопасный способ в данном контексте:
                try:
                    self._inventory_medicine.pop(index)
                except IndexError:
                    # Если индекс уже невалиден (редкий кейс), ищем и удаляем
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
