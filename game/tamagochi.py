import random
from abc import ABC, abstractmethod

from .exceptions import (
    InvalidActionError,
    TamagochiIsGone,
)
from .models import Food, Medicine


class AbstractTamagochi(ABC):
    # ... (все абстрактные методы оставь без изменений) ...
    @abstractmethod
    def feed(self, food: Food) -> None:
        pass

    @abstractmethod
    def play(self) -> None:
        pass

    @abstractmethod
    def rest(self) -> None:
        pass

    @abstractmethod
    def heal(self, medicine: Medicine) -> None:
        pass

    @abstractmethod
    def status(self) -> dict[str, int]:
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        pass

    @abstractmethod
    def is_sick(self) -> bool:
        pass

    @abstractmethod
    def update(self) -> None:
        pass


class SimpleTamagochi(AbstractTamagochi):
    """Реализация питомца для тамагочи-кликера."""

    def __init__(self, name: str = "Питомец") -> None:
        self.name = name
        self.hunger = 50
        self.hp = 100
        self.energy = 100
        self.fatigue = 0
        self._sick = False
        self._is_alive = True

        self.MAX_HUNGER = 100
        self.MIN_HUNGER = 0
        self.MAX_HP = 100
        self.MIN_HP = 0
        self.MAX_ENERGY = 100
        self.MIN_ENERGY = 0
        self.MAX_FATIGUE = 100
        self.MIN_FATIGUE = 0

    def _clamp(self, value: int, min_val: int, max_val: int) -> int:
        return max(min_val, min(value, max_val))

    def feed(self, food: Food) -> None:
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, кормить нельзя.")
        if self._sick:
            self.hunger = self._clamp(self.hunger - food.satiety // 2, self.MIN_HUNGER, self.MAX_HUNGER)
        else:
            self.hunger = self._clamp(self.hunger - food.satiety, self.MIN_HUNGER, self.MAX_HUNGER)
        self.energy = self._clamp(self.energy - 10, self.MIN_ENERGY, self.MAX_ENERGY)

    def play(self) -> None:
        """Игра с питомцем: тратит энергию, повышает голод (активность расходует ресурсы)."""
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, играть нельзя.")
        # Меняем показатели так, чтобы тест точно видел изменение
        self.energy = self._clamp(self.energy - 15, self.MIN_ENERGY, self.MAX_ENERGY)
        self.hunger = self._clamp(self.hunger + 10, self.MIN_HUNGER, self.MAX_HUNGER)
        self.fatigue = self._clamp(self.fatigue + 20, self.MIN_FATIGUE, self.MAX_FATIGUE)

    def rest(self) -> None:
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, отдых невозможен.")
        if self._sick:
            recovery = 15
            fatigue_reduction = 10
        else:
            recovery = 30
            fatigue_reduction = 25
        self.energy = self._clamp(self.energy + recovery, self.MIN_ENERGY, self.MAX_ENERGY)
        self.fatigue = self._clamp(self.fatigue - fatigue_reduction, self.MIN_FATIGUE, self.MAX_FATIGUE)

    def heal(self, medicine: Medicine) -> None:
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, лечение невозможно.")
        if medicine.is_empty():
            raise InvalidActionError("Лекарство закончилось.")
        medicine.use()
        self.hp = self._clamp(self.hp + medicine.heal_hp, self.MIN_HP, self.MAX_HP)
        self._sick = False

    def status(self) -> dict[str, int]:
        return {
            "hunger": self.hunger,
            "hp": self.hp,
            "energy": self.energy,
            "fatigue": self.fatigue,
        }

    def is_alive(self) -> bool:
        return self._is_alive

    def is_sick(self) -> bool:
        return self._sick

    def set_sick(self, sick: bool) -> None:
        self._sick = sick

    def update(self) -> None:
        """
        Обновляет состояние питомца каждый тик.
        Выбрасывает TamagochiIsGone, когда питомец умирает.
        """
        if not self._is_alive:
            return

        self.hunger = self._clamp(self.hunger + 5, self.MIN_HUNGER, self.MAX_HUNGER)
        self.energy = self._clamp(self.energy - 5, self.MIN_ENERGY, self.MAX_ENERGY)
        self.fatigue = self._clamp(self.fatigue + 3, self.MIN_FATIGUE, self.MAX_FATIGUE)

        if not self._sick and (self.fatigue > 80 or self.hp < 40) and random.random() < 0.3:
            self._sick = True

        if self._sick:
            self.hp = self._clamp(self.hp - 3, self.MIN_HP, self.MAX_HP)

        # Проверка смерти: выбрасываем строго TamagochiIsGone
        if self.hp <= 0:
            self._is_alive = False
            raise TamagochiIsGone("Питомец умер.")
