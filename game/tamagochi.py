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
    """Абстрактный базовый класс для питомца в игре тамагочи."""

    @abstractmethod
    def feed(self, food: Food) -> None:
        """Кормит питомца указанной едой."""

    @abstractmethod
    def play(self) -> None:
        """Играет с питомцем, изменяя его показатели."""

    @abstractmethod
    def rest(self) -> None:
        """Позволяет питомцу отдохнуть и восстановить силы."""

    @abstractmethod
    def heal(self, medicine: Medicine) -> None:
        """Лечит питомца с помощью указанного лекарства."""

    @abstractmethod
    def status(self) -> dict[str, int]:
        """Возвращает текущий статус питомца в виде словаря показателей."""

    @abstractmethod
    def is_alive(self) -> bool:
        """Проверяет, жив ли питомец."""

    @abstractmethod
    def is_sick(self) -> bool:
        """Проверяет, болен ли питомец."""

    @abstractmethod
    def update(self) -> None:
        """Обновляет состояние питомца в соответствии с игровым тиком."""


class SimpleTamagochi(AbstractTamagochi):
    """Реализация питомца для тамагочи-кликера с базовой логикой показателей."""

    def __init__(self, name: str = "Питомец") -> None:
        self.name = name
        self._hunger = 50
        self._hp = 100
        self._energy = 100
        self._fatigue = 0
        self._sick = False
        self._is_alive = True

    @staticmethod
    def _clamp(value: int, min_val: int, max_val: int) -> int:
        return max(min_val, min(value, max_val))

    def feed(self, food: Food) -> None:
        """Кормит питомца указанной едой, изменяя показатели голода и энергии."""
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, кормить нельзя.")

        if self._sick:
            satiety_effect = food.satiety // 2
            self._hunger = self._clamp(
                self._hunger - satiety_effect,
                MIN_HUNGER,
                MAX_HUNGER,
            )
        else:
            self._hunger = self._clamp(
                self._hunger - food.satiety,
                MIN_HUNGER,
                MAX_HUNGER,
            )

        self._energy = self._clamp(
            self._energy - 10,
            MIN_ENERGY,
            MAX_ENERGY,
        )

    def play(self) -> None:
        """Игра с питомцем: тратит энергию, повышает голод и усталость."""
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, играть нельзя.")

        self._energy = self._clamp(
            self._energy - 15,
            MIN_ENERGY,
            MAX_ENERGY,
        )
        self._hunger = self._clamp(
            self._hunger + 10,
            MIN_HUNGER,
            MAX_HUNGER,
        )
        self._fatigue = self._clamp(
            self._fatigue + 20,
            MIN_FATIGUE,
            MAX_FATIGUE,
        )

    def rest(self) -> None:
        """Позволяет питомцу отдохнуть, восстанавливая энергию и снижая усталость."""
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, отдых невозможен.")

        if self._sick:
            recovery = 15
            fatigue_reduction = 10
        else:
            recovery = 30
            fatigue_reduction = 25

        self._energy = self._clamp(
            self._energy + recovery,
            MIN_ENERGY,
            MAX_ENERGY,
        )
        self._fatigue = self._clamp(
            self._fatigue - fatigue_reduction,
            MIN_FATIGUE,
            MAX_FATIGUE,
        )

    def heal(self, medicine: Medicine) -> None:
        """Лечит питомца с помощью указанного лекарства."""
        if not self.is_alive():
            raise TamagochiIsGone("Питомец умер, лечение невозможно.")

        if medicine.is_empty():
            raise InvalidActionError("Лекарство закончилось.")

        medicine.use()
        self._hp = self._clamp(
            self._hp + medicine.heal_hp,
            MIN_HP,
            MAX_HP,
        )
        self._sick = False

    def status(self) -> dict[str, int]:
        """Возвращает текущий статус питомца в виде словаря показателей."""
        return {
            "hunger": self._hunger,
            "hp": self._hp,
            "energy": self._energy,
            "fatigue": self._fatigue,
        }

    def is_alive(self) -> bool:
        """Проверяет, жив ли питомец."""
        return self._is_alive

    def is_sick(self) -> bool:
        """Проверяет, болен ли питомец."""
        return self._sick

    def set_sick(self, sick: bool) -> None:
        """Устанавливает состояние болезни питомца."""
        self._sick = sick

    def update(self) -> None:
        """
        Обновляет состояние питомца каждый игровой тик.

        Изменяет показатели голода, энергии, усталости, проверяет возможность
        заболевания и состояние здоровья. При достижении критического уровня
        здоровья питомец умирает, и выбрасывается исключение TamagochiIsGone.
        """
        if not self._is_alive:
            return

        self._hunger = self._clamp(
            self._hunger + 5,
            MIN_HUNGER,
            MAX_HUNGER,
        )
        self._energy = self._clamp(
            self._energy - 5,
            MIN_ENERGY,
            MAX_ENERGY,
        )
        self._fatigue = self._clamp(
            self._fatigue + 3,
            MIN_FATIGUE,
            MAX_FATIGUE,
        )

        if (
            not self._sick
            and (self._fatigue > 80 or self._hp < 40)
            and random.random() < 0.3
        ):
            self._sick = True

        if self._sick:
            self._hp = self._clamp(
                self._hp - 3,
                MIN_HP,
                MAX_HP,
            )

        if self._hp <= 0:
            self._is_alive = False
            raise TamagochiIsGone("Питомец умер.")
