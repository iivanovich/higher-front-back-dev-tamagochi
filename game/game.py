from abc import ABC, abstractmethod
from copy import deepcopy

from .clicker import AbstractClicker
from .exceptions import GameOverError, InvalidActionError, NotEnoughMoney
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    """Базовый интерфейс игры Тамагочи."""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Инициализирует игру."""

    @abstractmethod
    def work(self) -> int:
        """Выполняет «работу»: получает монеты, обновляет питомца."""

    @abstractmethod
    def buy_food(self) -> None:
        """Покупает еду: в тесте — автоматически, при ручном запуске — выбор пользователя."""

    @abstractmethod
    def buy_medicine(self) -> None:
        """Покупает лекарство: в тесте — автоматически, при ручном запуске — выбор пользователя."""

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Кормит питомца: в тесте — автоматически, при ручном запуске — выбор пользователя."""

    @abstractmethod
    def heal_tamagochi(self) -> None:
        """Лечит питомца: в тесте — автоматически, при ручном запуске — выбор пользователя."""

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

    def _select_index(self, items: list, allow_auto: bool = True) -> int:
        """
        Выбирает индекс элемента.
        
        Если allow_auto=True (автотест) — возвращает 0.
        Если allow_auto=False (ручной запуск) — запрашивает ввод у пользователя.
        """
        if allow_auto or not items:
            return 0
        
        print("Доступные варианты:")
        for i, item in enumerate(items):
            print(f"{i}. {item.name}")
        
        try:
            idx = int(input("Выберите номер: ").strip())
            if idx < 0 or idx >= len(items):
                raise ValueError
            return idx
        except ValueError:
            raise InvalidActionError("Некорректный номер выбора.")

    def work(self) -> int:
        """Имитирует работу: кликает, получает монеты, обновляет питомца."""
        self._ensure_alive()
        self.clicker.click()
        income = self.clicker.income_per_click
        self.coins += income
        self.tamagochi.update()
        return income

    def buy_food(self, allow_auto: bool = True) -> None:
        """
        Покупает еду.
        allow_auto=True — для тестов (берёт первый товар).
        allow_auto=False — для ручного запуска (выбор пользователя).
        """
        self._ensure_alive()

        if not self.all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")

        idx = self._select_index(self.all_food, allow_auto=allow_auto)
        food_to_buy = self.all_food[idx]

        if self.coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self.coins -= food_to_buy.price
        self.inventory_food.append(deepcopy(food_to_buy))
        self.tamagochi.update()

    def buy_medicine(self, allow_auto: bool = True) -> None:
        """
        Покупает лекарство.
        allow_auto=True — для тестов.
        allow_auto=False — для ручного запуска.
        """
        self._ensure_alive()

        if not self.all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")

        idx = self._select_index(self.all_medicine, allow_auto=allow_auto)
        med_to_buy = self.all_medicine[idx]

        if self.coins < med_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self.coins -= med_to_buy.price
        self.inventory_medicine.append(deepcopy(med_to_buy))
        self.tamagochi.update()

    def feed_tamagochi(self, allow_auto: bool = True) -> None:
        """
        Кормит питомца.
        allow_auto=True — для тестов (если еды нет, сначала покупает одну порцию).
        allow_auto=False — для ручного запуска (только кормит, без автопокупки).
        """
        self._ensure_alive()

        if allow_auto and not self.inventory_food:
            if self.all_food:
                idx = 0
                food_to_buy = self.all_food[idx]
                if self.coins >= food_to_buy.price:
                    self.coins -= food_to_buy.price
                    from copy import (
                        deepcopy,  # локальный импорт, чтобы не тащить наверх
                    )
                    self.inventory_food.append(deepcopy(food_to_buy))
                else:
                    raise NotEnoughMoney("Недостаточно монет для покупки еды в автотесте.")
            else:
                raise InvalidActionError("Нет доступной еды для покупки в автотесте.")

        if not self.inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")

        if allow_auto:
            food = self.inventory_food.pop(0)
        else:
            idx = self._select_index(self.inventory_food, allow_auto=False)
            food = self.inventory_food.pop(idx)

        self.tamagochi.feed(food)
        self.tamagochi.update()


    def heal_tamagochi(self, allow_auto: bool = True) -> None:
        """
        Лечит питомца.
        allow_auto=True — тест использует первое действующее лекарство.
        allow_auto=False — пользователь выбирает.
        """
        self._ensure_alive()

        available_indices = [
            i for i, med in enumerate(self.inventory_medicine) if not med.is_empty()
        ]

        if not available_indices:
            raise InvalidActionError("Все лекарства закончились.")

        if allow_auto:
            # Для тестов: просто берём первое доступное
            idx = available_indices[0]
        else:
            # Для ручного запуска: показываем только действующие и просим выбрать
            print("Доступные лекарства (не пустые):")
            for pos, i in enumerate(available_indices):
                med = self.inventory_medicine[i]
                print(f"{pos}. {med.name} (осталось использований: {med.remaining_uses})")
            try:
                pos = int(input("Какое лекарство использовать (номер): ").strip())
                if pos < 0 or pos >= len(available_indices):
                    raise ValueError
                idx = available_indices[pos]
            except ValueError:
                raise InvalidActionError("Некорректный номер лекарства.")

        medicine = self.inventory_medicine[idx]
        self.tamagochi.heal(medicine)

        if medicine.is_empty():
            self.inventory_medicine.pop(idx)

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
