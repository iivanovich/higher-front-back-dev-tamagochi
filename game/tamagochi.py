import random
from abc import ABC, abstractmethod

from .constants import (
    MAX_ENERGY,
    MAX_FATIGUE,
    MAX_HP,
    MAX_HUNGER,
    MIN_ENERGY,
    MIN_FATIGUE,
    MIN_HP,
    MIN_HUNGER,
)
from .exceptions import InvalidActionError, TamagochiIsGone
from .models import Food, Medicine


class AbstractTamagochi(ABC):
    @abstractmethod
    def feed(self, food: Food) -> None:
        """
        Кормит питомца.
        """

    @abstractmethod
    def play(self) -> None:
        """
        Питомец играет.
        """

    @abstractmethod
    def rest(self) -> None:
        """
        Питомец отдыхает.
        """

    @abstractmethod
    def heal(self, medicine: Medicine) -> None:
        """
        Лечит питомца.
        """

    @abstractmethod
    def status(self) -> dict[str, int]:
        """
        Текущее состояние питомца.
        """

    @abstractmethod
    def is_alive(self) -> bool:
        """
        Жив ли питомец.
        """

    @abstractmethod
    def is_sick(self) -> bool:
        """
        Болен ли питомец.
        """

    @abstractmethod
    def update(self) -> None:
        """
        Обновляет состояние питомца.
        """

class SimpleTamagochi(AbstractTamagochi):
    """Реализация питомца для тамагочи-кликера."""

    def __init__(self, name: str = "Питомец") -> None:
        from .constants import MAX_ENERGY, MAX_HP, MIN_FATIGUE, MIN_HUNGER
        self._name = name
        self._hunger = MIN_HUNGER + 50
        self._hp = MAX_HP
        self._energy = MAX_ENERGY
        self._fatigue = MIN_FATIGUE
        self._sick = False
        self._is_alive = True

    @staticmethod
    def _clamp(value: int, min_val: int, max_val: int) -> int:
        return max(min_val, min(value, max_val))

    def feed(self, food: Food) -> None:
        """
        Кормит питомца. Если питомец болен, сытость восстанавливается наполовину.
        """
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, кормить нельзя.")
        if self._sick:
            self._hunger = self._clamp(self._hunger - food.satiety // 2, MIN_HUNGER, MAX_HUNGER)
        else:
            self._hunger = self._clamp(self._hunger - food.satiety, MIN_HUNGER, MAX_HUNGER)
        self._energy = self._clamp(self._energy - 10, MIN_ENERGY, MAX_ENERGY)

    def play(self) -> None:
        """Игра с питомцем: тратит энергию, повышает голод и усталость."""
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, играть нельзя.")
        self._energy = self._clamp(self._energy - 15, MIN_ENERGY, MAX_ENERGY)
        self._hunger = self._clamp(self._hunger + 10, MIN_HUNGER, MAX_HUNGER)
        self._fatigue = self._clamp(self._fatigue + 20, MIN_FATIGUE, MAX_FATIGUE)

    def rest(self) -> None:
        """Питомец отдыхает и восстанавливает энергию, снижает усталость."""
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, отдых невозможен.")
        recovery = 15 if self._sick else 30
        fatigue_reduction = 10 if self._sick else 25
        self._energy = self._clamp(self._energy + recovery, MIN_ENERGY, MAX_ENERGY)
        self._fatigue = self._clamp(self._fatigue - fatigue_reduction, MIN_FATIGUE, MAX_FATIGUE)

    def heal(self, medicine: Medicine) -> None:
        """Лечит питомца с помощью лекарства."""
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, лечение невозможно.")
        if medicine.is_empty():
            raise InvalidActionError("Лекарство закончилось.")
        medicine.use()
        self._hp = self._clamp(self._hp + medicine.heal_hp, MIN_HP, MAX_HP)
        self._sick = False

    def status(self) -> dict[str, int]:
        """Возвращает текущие показатели питомца."""
        return {
            "hunger": self._hunger,
            "hp": self._hp,
            "energy": self._energy,
            "fatigue": self._fatigue,
        }

    def is_alive(self) -> bool:
        """Питомец живой?"""
        return self._is_alive

    def is_sick(self) -> bool:
        """Питомец болен?"""
        return self._sick

    def set_sick(self, sick: bool) -> None:
        """Принудительно устанавливает болезнь (для тестирования)."""
        self._sick = sick

    def update(self) -> None:
        """
        Обновляет состояние питомца каждый тик.
        Вызывает TamagochiIsGone, если питомец умирает.
        """
        if not self._is_alive:
            raise TamagochiIsGone("Питомец мёртв.")

        self._hunger = self._clamp(self._hunger + 5, MIN_HUNGER, MAX_HUNGER)
        self._energy = self._clamp(self._energy - 5, MIN_ENERGY, MAX_ENERGY)
        self._fatigue = self._clamp(self._fatigue + 3, MIN_FATIGUE, MAX_FATIGUE)

        if not self._sick and (self._fatigue > 80 or self._hp < 40) and random.random() < 0.3:
            self._sick = True

        if self._sick:
            self._hp = self._clamp(self._hp - 3, MIN_HP, MAX_HP)

        if self._hp <= 0:
            self._is_alive = False
            raise TamagochiIsGone("Питомец умер.")