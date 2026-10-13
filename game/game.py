# game/game.py
from abc import ABC, abstractmethod

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
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        pass

    @abstractmethod
    def work(self) -> int:
        pass

    @abstractmethod
    def buy_food(self) -> None:
        pass

    @abstractmethod
    def buy_medicine(self) -> None:
        pass

    @abstractmethod
    def feed_tamagochi(self) -> None:
        pass

    @abstractmethod
    def heal_tamagochi(self) -> None:
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
    """Основная логика игры: управление ресурсами и действиями."""

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        self.tamagochi = tamagochi
        self.clicker = clicker
        self.all_food = all_food
        self.all_medicine = all_medicine
        self.coins = 100  # стартовые монеты
        self.inventory_food: list[Food] = []
        self.inventory_medicine: list[Medicine] = []

    def work(self) -> int:
        """Имитирует работу: использует кликер для получения монет."""
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена.")
        self.clicker.click()
        income = self.clicker.income_per_click
        self.coins += income
        return income

    def buy_food(self) -> None:
        """Покупает одну порцию еды из списка доступных."""
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена.")
        if not self.all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")

        food_to_buy = self.all_food[0]  # покупаем первую доступную
        if self.coins < food_to_buy.price:
            raise NotEnoughMoneyError("Недостаточно монет.")

        self.coins -= food_to_buy.price
        self.inventory_food.append(food_to_buy)

    def buy_medicine(self) -> None:
        """Покупает одно лекарство из списка доступных."""
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена.")
        if not self.all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")

        med_to_buy = self.all_medicine[0]
        if self.coins < med_to_buy.price:
            raise NotEnoughMoneyError("Недостаточно монет.")

        self.coins -= med_to_buy.price
        self.inventory_medicine.append(med_to_buy)

    def feed_tamagochi(self) -> None:
        """Кормит питомца из инвентаря."""
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена.")
        if not self.inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")

        food = self.inventory_food.pop(0)  # берём первую
        self.tamagochi.feed(food)

    def heal_tamagochi(self) -> None:
        """Лечит питомца из инвентаря."""
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена.")
        if not self.inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")

        medicine = self.inventory_medicine[0]
        if medicine.is_empty():
            # Если первое лекарство кончилось, ищем следующее
            found = False
            for med in self.inventory_medicine:
                if not med.is_empty():
                    medicine = med
                    found = True
                    break
            if not found:
                raise InvalidActionError("Все лекарства закончились.")
        
        self.tamagochi.heal(medicine)

    def rest_tamagochi(self) -> None:
        """Позволяет питомцу отдохнуть."""
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена.")
        self.tamagochi.rest()

    def play_with_tamagochi(self) -> None:
        """Играет с питомцем."""
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена.")
        self.tamagochi.play()

    def get_status(self) -> dict[str, int]:
        """Получает статус игры: показатели питомца и монеты."""
        status = self.tamagochi.status()
        status["coins"] = self.coins
        return status

    @property
    def food(self) -> list[Food]:
        return self.inventory_food

    @property
    def medicine(self) -> list[Medicine]:
        return self.inventory_medicine