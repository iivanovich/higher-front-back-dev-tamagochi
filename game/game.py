from abc import ABC, abstractmethod
from copy import deepcopy

from .clicker import AbstractClicker
from .exceptions import GameOverError, InvalidActionError, NotEnoughMoney
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    """Базовый интерфейс игры Тамагочи: обязательные методы и свойства."""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Инициализирует игру: питомец, кликер, каталоги товаров."""

    @abstractmethod
    def work(self) -> int:
        """Выполняет «работу»: получает монеты, обновляет питомца."""

    @abstractmethod
    def buy_food(self) -> None:
        """Покупает еду: берёт первый товар из каталога."""

    @abstractmethod
    def buy_medicine(self) -> None:
        """Покупает лекарство: берёт первый товар из каталога."""

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Кормит питомца едой из инвентаря."""

    @abstractmethod
    def heal_tamagochi(self) -> None:
        """Лечит питомца лекарством из инвентаря."""

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Позволяет питомцу отдохнуть."""

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Играет с питомцем."""

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        """Возвращает статус: параметры питомца и монеты."""

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """Список еды в инвентаре игрока."""

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """Список лекарств в инвентаре игрока."""


class SimpleGame(AbstractGame):
    """Реализация игры: управление ресурсами и действиями питомца."""

    START_COINS = 100

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Инициализирует состояние игры, копирует списки товаров."""
        self.tamagochi = tamagochi
        self.clicker = clicker
        self.all_food = list(all_food)
        self.all_medicine = list(all_medicine)
        self.coins = self.START_COINS
        self.inventory_food: list[Food] = []
        self.inventory_medicine: list[Medicine] = []

    def _ensure_alive(self) -> None:
        """Проверяет, жив ли питомец; иначе выбрасывает GameOverError."""
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена: питомец умер.")

    def work(self) -> int:
        """Имитирует работу: кликает, получает монеты, обновляет питомца."""
        self._ensure_alive()
        self.clicker.click()
        income = self.clicker.income_per_click
        self.coins += income
        self.tamagochi.update()
        return income

    def buy_food(self) -> None:
        """Покупает первую доступную порцию еды, добавляет копию в инвентарь."""
        self._ensure_alive()

        if not self.all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")

        food_to_buy = self.all_food[0]

        if self.coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self.coins -= food_to_buy.price
        # Ключевое исправление: кладём в инвентарь КОПИЮ объекта, а не ссылку
        self.inventory_food.append(deepcopy(food_to_buy))
        self.tamagochi.update()

    def buy_medicine(self) -> None:
        """Покупает первое доступное лекарство, добавляет копию в инвентарь."""
        self._ensure_alive()

        if not self.all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")

        med_to_buy = self.all_medicine[0]

        if self.coins < med_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self.coins -= med_to_buy.price
        # То же самое для лекарств
        self.inventory_medicine.append(deepcopy(med_to_buy))
        self.tamagochi.update()

    def feed_tamagochi(self) -> None:
        """Кормит питомца первой едой из инвентаря, удаляет её оттуда."""
        self._ensure_alive()

        if not self.inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")

        food = self.inventory_food.pop(0)
        self.tamagochi.feed(food)
        self.tamagochi.update()

    def heal_tamagochi(self) -> None:
        """Лечит питомца первым непустым лекарством из инвентаря."""
        self._ensure_alive()

        if not self.inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")

        medicine = None
        found_index = -1

        for i, med in enumerate(self.inventory_medicine):
            if not med.is_empty():
                medicine = med
                found_index = i
                break

        if medicine is None:
            raise InvalidActionError("Все лекарства закончились.")

        self.tamagochi.heal(medicine)
        self.inventory_medicine.pop(found_index)
        self.tamagochi.update()

    def rest_tamagochi(self) -> None:
        """Позволяет питомцу отдохнуть, обновляет его состояние."""
        self._ensure_alive()
        self.tamagochi.rest()
        self.tamagochi.update()

    def play_with_tamagochi(self) -> None:
        """Играет с питомцем, обновляет его состояние."""
        self._ensure_alive()
        self.tamagochi.play()
        self.tamagochi.update()

    def get_status(self) -> dict[str, int]:
        """Получает статус игры: параметры питомца и баланс монет."""
        status = self.tamagochi.status()
        status["coins"] = self.coins
        return status

    @property
    def food(self) -> list[Food]:
        """Возвращает список еды в инвентаре."""
        return list(self.inventory_food)

    @property
    def medicine(self) -> list[Medicine]:
        """Возвращает список лекарств в инвентаре."""
        return list(self.inventory_medicine)
