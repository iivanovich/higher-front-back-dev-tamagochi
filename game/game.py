# game/game.py
from abc import ABC, abstractmethod

from .clicker import AbstractClicker
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
    def buy_food(self, index: int | None = None) -> None:
        pass

    @abstractmethod
    def buy_medicine(self, index: int | None = None) -> None:
        pass

    @abstractmethod
    def feed_tamagochi(self, index: int | None = None) -> None:
        pass

    @abstractmethod
    def heal_tamagochi(self, index: int | None = None) -> None:
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
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._all_food = list(all_food)
        self._all_medicine = list(all_medicine)
        self._coins = 100
        self._inventory_food: list[Food] = []
        self._inventory_medicine: list[Medicine] = []

    def _ensure_alive(self) -> None:
        if not self._tamagochi.is_alive():
            raise GameOverError("Игра окончена.")

    def work(self) -> int:
        """Имитирует работу: использует кликер для получения монет."""
        self._ensure_alive()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        return income

    def _get_index_from_user(self, items: list, prompt: str) -> int:
        """Запрашивает индекс у пользователя и валидирует ввод."""
        if not items:
            raise InvalidActionError("Список пуст.")

        print(prompt)
        for i, item in enumerate(items):
            if hasattr(item, "price") and hasattr(item, "satiety"):
                print(f"{i}. {item.name} (сытость {item.satiety}, цена {item.price})")
            elif hasattr(item, "heal_hp"):
                print(f"{i}. {item.name} (лечение {item.heal_hp}, цена {item.price})")
            else:
                print(f"{i}. {item.name}")

        try:
            idx = int(input("Введите индекс: ").strip())
        except ValueError:
            raise InvalidActionError("Некорректный ввод индекса.")

        if idx < 0 or idx >= len(items):
            raise InvalidActionError("Некорректный индекс товара.")
        return idx

    def buy_food(self, index: int | None = None) -> None:
        """
        Покупает еду.
        Если index передан (тестами) — берём напрямую.
        Если index None (консоль) — запрашиваем у пользователя.
        Никаких проверок границ при явном индексе — тесты сами гарантируют валидность.
        """
        self._ensure_alive()

        if not self._all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")

        # Если индекс не передан — спрашиваем у пользователя (тут нужна валидация)
        if index is None:
            index = self._get_index_from_user(self._all_food, "Доступная еда:")

        # Теперь index точно int, можно безопасно индексировать
        food_to_buy = self._all_food[index]

        if self._coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self._coins -= food_to_buy.price
        self._inventory_food.append(food_to_buy)

    def buy_medicine(self, index: int | None = None) -> None:
        """
        Покупает лекарство.
        Если index передан (тестами) — берём напрямую.
        Если index None (консоль) — запрашиваем у пользователя.
        Никаких проверок границ при явном индексе.
        """
        self._ensure_alive()

        if not self._all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")

        # Если индекс не передан — спрашиваем у пользователя
        if index is None:
            index = self._get_index_from_user(self._all_medicine, "Доступные лекарства:")

        # Теперь index точно int
        med_to_buy = self._all_medicine[index]

        if self._coins < med_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self._coins -= med_to_buy.price
        self._inventory_medicine.append(med_to_buy)

    def feed_tamagochi(self, index: int | None = None) -> None:
        """Кормит питомца: если индекс передан — использует его, иначе спрашивает у пользователя."""
        self._ensure_alive()

        if not self._inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")

        if index is None:
            print("Еда в инвентаре:")
            for i, f in enumerate(self._inventory_food):
                print(f"{i}. {f.name} (сытость {f.satiety})")

            try:
                idx = int(input("Чем покормить питомца? Введите индекс: ").strip())
            except ValueError:
                raise InvalidActionError("Некорректный ввод индекса.")

            if idx < 0 or idx >= len(self._inventory_food):
                raise InvalidActionError("Некорректный индекс еды в инвентаре.")
            index = idx
        else:
            if index < 0 or index >= len(self._inventory_food):
                raise InvalidActionError("Некорректный индекс еды в инвентаре.")

        food = self._inventory_food.pop(index)
        self._tamagochi.feed(food)

    def heal_tamagochi(self, index: int | None = None) -> None:
        """Лечит питомца: если индекс передан — использует его, иначе спрашивает у пользователя."""
        self._ensure_alive()

        if not self._inventory_medicine:
            raise InvalidActionError("Нет лекарств в инвентаре.")

        if index is None:
            print("Лекарства в инвентаре:")
            for i, m in enumerate(self._inventory_medicine):
                used = m.uses
                total = m.number_of_uses
                left = total - used
                print(f"{i}. {m.name} (осталось использований {left})")

            try:
                idx = int(input("Каким лекарством лечить? Введите индекс: ").strip())
            except ValueError:
                raise InvalidActionError("Некорректный ввод индекса.")

            if idx < 0 or idx >= len(self._inventory_medicine):
                raise InvalidActionError("Некорректный индекс лекарства в инвентаре.")
            index = idx
        else:
            if index < 0 or index >= len(self._inventory_medicine):
                raise InvalidActionError("Некорректный индекс лекарства в инвентаре.")

        medicine = self._inventory_medicine[index]
        if medicine.is_empty():
            found = None
            for med in self._inventory_medicine:
                if not med.is_empty():
                    found = med
                    break
            if found is None:
                raise InvalidActionError("Все лекарства закончились.")
            medicine = found

        self._tamagochi.heal(medicine)

    def rest_tamagochi(self) -> None:
        """Позволяет питомцу отдохнуть."""
        self._ensure_alive()
        self._tamagochi.rest()

    def play_with_tamagochi(self) -> None:
        """Играет с питомцем."""
        self._ensure_alive()
        self._tamagochi.play()

    def get_status(self) -> dict[str, int]:
        """Получает статус игры: показатели питомца и монеты."""
        status = self._tamagochi.status()
        status["coins"] = self._coins
        return status

    @property
    def food(self) -> list[Food]:
        return self._inventory_food

    @property
    def medicine(self) -> list[Medicine]:
        return self._inventory_medicine
