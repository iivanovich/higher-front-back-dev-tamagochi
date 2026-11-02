from abc import ABC, abstractmethod

from .clicker import AbstractClicker
from .constants import START_COINS
from .exceptions import GameOverError, InvalidActionError, NotEnoughMoney
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    """Абстрактная логика игры Тамагочи."""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        ...

    @abstractmethod
    def work(self) -> int:
        ...

    @abstractmethod
    def buy_food(self) -> None:
        ...

    @abstractmethod
    def buy_medicine(self) -> None:
        ...

    @abstractmethod
    def feed_tamagochi(self) -> None:
        ...

    @abstractmethod
    def heal_tamagochi(self) -> None:
        ...

    @abstractmethod
    def rest_tamagochi(self) -> None:
        ...

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        ...

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        ...

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        ...

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        ...

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
        self.all_food = list(all_food)
        self.all_medicine = list(all_medicine)
        self.coins = START_COINS
        self.inventory_food: list[Food] = []
        self.inventory_medicine: list[Medicine] = []

    def _ensure_alive(self) -> None:
        if not self.tamagochi.is_alive():
            raise GameOverError("Игра окончена.")

    def work(self) -> int:
        """Имитирует работу: использует кликер для получения монет."""
        self._ensure_alive()
        self.clicker.click()
        income = self.clicker.income_per_click
        self.coins += income
        return income

    def buy_food(self) -> None:
        """Покупает одну порцию еды из списка доступных (первую)."""
        self._ensure_alive()
        if not self.all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")
        food_to_buy = self.all_food[0]
        if self.coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")
        self.coins -= food_to_buy.price
        self.inventory_food.append(food_to_buy)

    def buy_medicine(self) -> None:
        """Покупает одно лекарство из списка доступных (первое)."""
        self._ensure_alive()
        if not self.all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")
        med_to_buy = self.all_medicine[0]
        if self.coins < med_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")
        self.coins -= med_to_buy.price
        self.inventory_medicine.append(med_to_buy)

    def feed_tamagochi(self) -> None:
        """Кормит питомца из инвентаря (первой едой)."""
        self._ensure_alive()
        if not self.inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")
        food = self.inventory_food.pop(0)
        self.tamagochi.feed(food)

    def heal_tamagochi(self) -> None:
        """Лечит питомца из инвентаря."""
        self._ensure_alive()
        if not self.inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")
        medicine = self.inventory_medicine[0]
        if medicine.is_empty():
            for med in self.inventory_medicine:
                if not med.is_empty():
                    medicine = med
                    break
            else:
                raise InvalidActionError("Все лекарства закончились.")
        self.tamagochi.heal(medicine)

    def rest_tamagochi(self) -> None:
        """Позволяет питомцу отдохнуть."""
        self._ensure_alive()
        self.tamagochi.rest()

    def play_with_tamagochi(self) -> None:
        """Играет с питомцем."""
        self._ensure_alive()
        self.tamagochi.play()

    def get_status(self) -> dict[str, int]:
        """Получает статус игры: показатели питомца и монеты."""
        status = self.tamagochi.status()
        status["coins"] = self.coins
        return status

    @property
    def food(self) -> list[Food]:
        """Текущее содержимое инвентаря еды."""
        return self.inventory_food

    @property
    def medicine(self) -> list[Medicine]:
        """Текущее содержимое инвентаря лекарств."""
        return self.inventory_medicine