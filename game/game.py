from abc import ABC, abstractmethod

from .clicker import AbstractClicker
from .constants import START_COINS
from .exceptions import GameOverError, InvalidActionError, NotEnoughMoney
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    """Абстрактный интерфейс для игры тамагочи-кликера."""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Инициализация игры с питомцем, кликером, ассортиментом еды и лекарств."""

    @abstractmethod
    def work(self) -> int:
        """Работа: получение монет через кликер."""

    @abstractmethod
    def buy_food(self) -> None:
        """Купить порцию еды."""

    @abstractmethod
    def buy_medicine(self) -> None:
        """Купить лекарство."""

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Накормить питомца (выдать еду из инвентаря)."""

    @abstractmethod
    def heal_tamagochi(self) -> None:
        """Вылечить питомца (применить лекарство из инвентаря)."""

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Дать питомцу отдохнуть."""

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Поиграть с питомцем."""

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        """Получить статус: показатели питомца и количество монет."""

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """Возвращает текущий инвентарь еды."""

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """Возвращает текущий инвентарь лекарств."""

class SimpleGame(AbstractGame):
    """Основная логика игры: управление ресурсами и действиями."""

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """
        Инициализация игры с питомцем, кликером, ассортиментом еды и лекарств.
        """
        self.tamagochi = tamagochi
        self.clicker = clicker
        # Важно: делаем копии списков, чтобы не менять исходные коллекции
        self.all_food = list(all_food)
        self.all_medicine = list(all_medicine)
        self.coins = START_COINS  # используем константу
        self.inventory_food: list[Food] = []
        self.inventory_medicine: list[Medicine] = []

    def _ensure_alive(self) -> None:
        """Проверяет, что питомец еще жив."""
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

        food_to_buy = self.all_food[0]  # берём первую доступную

        if self.coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self.coins -= food_to_buy.price
        self.inventory_food.append(food_to_buy)

    def buy_medicine(self) -> None:
        """Покупает одно лекарство из списка доступных (первое)."""
        self._ensure_alive()

        if not self.all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")

        med_to_buy = self.all_medicine[0]  # берём первое доступное

        if self.coins < med_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self.coins -= med_to_buy.price
        self.inventory_medicine.append(med_to_buy)

    def feed_tamagochi(self) -> None:
        """Кормит питомца из инвентаря (первой едой)."""
        self._ensure_alive()

        if not self.inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")

        food = self.inventory_food.pop(0)  # берём первую
        self.tamagochi.feed(food)

    def heal_tamagochi(self) -> None:
        """Лечит питомца из инвентаря."""
        self._ensure_alive()

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