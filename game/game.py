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
        """Покупает еду: пользователь выбирает товар из каталога."""

    @abstractmethod
    def buy_medicine(self) -> None:
        """Покупает лекарство: пользователь выбирает товар из каталога."""

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Кормит питомца: пользователь выбирает еду из инвентаря."""

    @abstractmethod
    def heal_tamagochi(self) -> None:
        """Лечит питомца: пользователь выбирает лекарство из инвентаря."""

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
        # Копируем списки, чтобы не мутировать исходные коллекции
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
        """
        Покупает еду.
        Пользователь должен выбрать товар из каталога all_food по индексу.
        В инвентарь кладётся копия объекта.
        """
        self._ensure_alive()

        if not self.all_food:
            raise InvalidActionError("Нет доступной еды для покупки.")

        print("Доступные товары:")
        for i, f in enumerate(self.all_food):
            print(f"{i}. {f.name} (сытость: {f.satiety}, цена: {f.price})")

        try:
            idx = int(input("Выберите номер товара: ").strip())
        except ValueError:
            raise InvalidActionError("Некорректный номер товара.")

        if idx < 0 or idx >= len(self.all_food):
            raise InvalidActionError("Товар с таким номером отсутствует.")

        food_to_buy = self.all_food[idx]

        if self.coins < food_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self.coins -= food_to_buy.price
        self.inventory_food.append(deepcopy(food_to_buy))
        self.tamagochi.update()

    def buy_medicine(self) -> None:
        """
        Покупает лекарство.
        Пользователь выбирает товар из all_medicine по индексу.
        В инвентарь кладётся копия объекта.
        """
        self._ensure_alive()

        if not self.all_medicine:
            raise InvalidActionError("Нет доступных лекарств для покупки.")

        print("Доступные лекарства:")
        for i, m in enumerate(self.all_medicine):
            print(
                f"{i}. {m.name} "
                f"(лечение: {m.heal_hp}, использований: {m.number_of_uses}, цена: {m.price})"
            )

        try:
            idx = int(input("Выберите номер лекарства: ").strip())
        except ValueError:
            raise InvalidActionError("Некорректный номер лекарства.")

        if idx < 0 or idx >= len(self.all_medicine):
            raise InvalidActionError("Лекарство с таким номером отсутствует.")

        med_to_buy = self.all_medicine[idx]

        if self.coins < med_to_buy.price:
            raise NotEnoughMoney("Недостаточно монет.")

        self.coins -= med_to_buy.price
        self.inventory_medicine.append(deepcopy(med_to_buy))
        self.tamagochi.update()

    def feed_tamagochi(self) -> None:
        """
        Кормит питомца.
        Пользователь выбирает еду из инвентаря по индексу, затем она удаляется.
        """
        self._ensure_alive()

        if not self.inventory_food:
            raise InvalidActionError("Нет еды в инвентаре.")

        print("Еда в инвентаре:")
        for i, f in enumerate(self.inventory_food):
            print(f"{i}. {f.name} (сытость: {f.satiety})")

        try:
            idx = int(input("Чем покормить питомца (номер): ").strip())
        except ValueError:
            raise InvalidActionError("Некорректный номер еды.")

        if idx < 0 or idx >= len(self.inventory_food):
            raise InvalidActionError("Еды с таким номером нет в инвентаре.")

        food = self.inventory_food.pop(idx)
        self.tamagochi.feed(food)
        self.tamagochi.update()

    def heal_tamagochi(self) -> None:
        """
        Лечит питомца.
        Пользователь выбирает действующее лекарство из инвентаря по индексу.
        Если лекарство закончилось (is_empty), оно пропускается.
        """
        self._ensure_alive()

        # Ищем доступные лекарства
        available_indices = [
            i for i, med in enumerate(self.inventory_medicine) if not med.is_empty()
        ]

        if not available_indices:
            raise InvalidActionError("Все лекарства закончились.")

        print("Доступные лекарства (не пустые):")
        for pos, i in enumerate(available_indices):
            med = self.inventory_medicine[i]
            print(f"{pos}. {med.name} (осталось использований: {med.remaining_uses})")

        try:
            pos = int(input("Какое лекарство использовать (номер): ").strip())
        except ValueError:
            raise InvalidActionError("Некорректный номер лекарства.")

        if pos < 0 or pos >= len(available_indices):
            raise InvalidActionError("Выбрано недопустимое лекарство.")

        idx = available_indices[pos]
        medicine = self.inventory_medicine[idx]

        self.tamagochi.heal(medicine)

        if medicine.is_empty():
            # Удаляем, если после использования стало пустым
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
