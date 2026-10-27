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
    def buy_food(self, index: int) -> None:
        """Покупает еду по индексу из каталога магазина."""

    @abstractmethod
    def buy_medicine(self, index: int) -> None:
        """Покупает лекарство по индексу из каталога магазина."""

    @abstractmethod
    def feed_tamagochi(self, index: int) -> None:
        """Кормит питомца едой по индексу из инвентаря игрока."""

    @abstractmethod
    def heal_tamagochi(self, index: int) -> None:
        """Лечит питомца лекарством по индексу из инвентаря игрока."""

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Позволяет питомцу отдохнуть и восстанавливает энергию."""

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Играет с питомцем: тратит энергию, повышает голод и усталость."""

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        """Возвращает словарь со статусом игры: показатели питомца и количество монет."""

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """Возвращает список еды в инвентаре игрока (копию для защиты от мутации)."""

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """Возвращает список лекарств в инвентаре игрока (копию для защиты от мутации)."""


class SimpleGame(AbstractGame):
    """Конкретная реализация игры: управление ресурсами и действиями питомца."""

    START_COINS = 100

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Создаёт игру с заданными компонентами и стартовыми монетами."""
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._all_food = list(all_food)
        self._all_medicine = list(all_medicine)
        self._coins = self.START_COINS
        self._inventory_food: list[Food] = []
        self._inventory_medicine: list[Medicine] = []

    def _ensure_alive(self) -> None:
        """Проверяет, жив ли питомец. Если нет — выбрасывает GameOverError."""
        if not self._tamagochi.is_alive():
            raise GameOverError("Игра окончена: питомец умер.")

    def work(self) -> int:
        """Работа: кликает, получает доход и обновляет состояние питомца (тик)."""
        self._ensure_alive()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        self._tamagochi.update()  # тик внутри метода — как просил ревьюер
        return income

    def buy_food(self, index: int) -> None:
        """Покупка еды по индексу: проверяет деньги, добавляет в инвентарь, обновляет питомца."""
        self._ensure_alive()

        if not self._all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")

        if index < 0 or index >= len(self._all_food):
            raise InvalidActionError("Некорректный индекс товара.")

        food_to_buy = self._all_food[index]

        if self._coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self._coins -= food_to_buy.price
        self._inventory_food.append(deepcopy(food_to_buy))
        self._tamagochi.update()

    def buy_medicine(self, index: int) -> None:
        """Покупка лекарства по индексу: проверяет деньги, добавляет в инвентарь, обновляет питомца."""
        self._ensure_alive()

        if not self._all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")

        if index < 0 or index >= len(self._all_medicine):
            raise InvalidActionError("Некорректный индекс товара.")

        med_to_buy = self._all_medicine[index]

        if self._coins < med_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self._coins -= med_to_buy.price
        self._inventory_medicine.append(deepcopy(med_to_buy))
        self._tamagochi.update()

    def feed_tamagochi(self, index: int) -> None:
        """Кормление питомца по индексу еды в инвентаре: удаляет предмет, обновляет питомца."""
        self._ensure_alive()

        if not self._inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")

        if index < 0 or index >= len(self._inventory_food):
            raise InvalidActionError("Некорректный индекс еды в инвентаре.")

        food = self._inventory_food.pop(index)
        self._tamagochi.feed(food)
        self._tamagochi.update()

    def heal_tamagochi(self, index: int) -> None:
        """Лечение питомца по индексу лекарства в инвентаре: проверяет остаток, обновляет питомца."""
        self._ensure_alive()

        if not self._inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")

        if index < 0 or index >= len(self._inventory_medicine):
            raise InvalidActionError("Некорректный индекс лекарства в инвентаре.")

        medicine = self._inventory_medicine[index]

        if medicine.is_empty():
            raise InvalidActionError("Выбранное лекарство закончилось.")

        self._tamagochi.heal(medicine)
        self._tamagochi.update()

    def rest_tamagochi(self) -> None:
        """Отдых питомца: восстанавливает энергию, обновляет состояние (тик)."""
        self._ensure_alive()
        self._tamagochi.rest()
        self._tamagochi.update()

    def play_with_tamagochi(self) -> None:
        """Игра с питомцем: повышает усталость, обновляет состояние (тик)."""
        self._ensure_alive()
        self._tamagochi.play()
        self._tamagochi.update()

    def get_status(self) -> dict[str, int]:
        """Получает статус: показатели питомца плюс количество монет."""
        status = self._tamagochi.status()
        status["coins"] = self._coins
        return status

    @property
    def food(self) -> list[Food]:
        """Безопасное получение инвентаря еды: возвращает копию списка."""
        return list(self._inventory_food)

    @property
    def medicine(self) -> list[Medicine]:
        """Безопасное получение инвентаря лекарств: возвращает копию списка."""
        return list(self._inventory_medicine)
