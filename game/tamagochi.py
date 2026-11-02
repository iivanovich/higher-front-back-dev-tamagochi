"""Логика питомца-тамагочи.

Класс :class:`SimpleTamagochi` ничего не знает о деньгах, еде за монеты и
меню игры: он лишь меняет собственные показатели в ответ на действия.
Все числовые параметры берутся из модуля :mod:`game.constants`.
"""

import random
from abc import ABC, abstractmethod

from game import constants
from game.exceptions import (
    EmptyMedicineError,
    TamagochiIsDeadError,
    TamagochiIsNotSickError,
)
from game.models import Food, Medicine


class AbstractTamagochi(ABC):
    """Интерфейс питомца."""

    @abstractmethod
    def feed(self, food: Food) -> None:
        """Накормить питомца.

        :param food: еда, которой кормят.
        """

    @abstractmethod
    def play(self) -> None:
        """Поиграть с питомцем."""

    @abstractmethod
    def rest(self) -> None:
        """Дать питомцу отдохнуть."""

    @abstractmethod
    def heal(self, medicine: Medicine) -> None:
        """Вылечить питомца.

        :param medicine: применяемое лекарство.
        """

    @abstractmethod
    def status(self) -> dict[str, int]:
        """Вернуть все показатели питомца."""

    @abstractmethod
    def is_alive(self) -> bool:
        """Проверить, жив ли питомец."""

    @abstractmethod
    def is_sick(self) -> bool:
        """Проверить, болен ли питомец."""

    @abstractmethod
    def update(self) -> None:
        """Обновить состояние питомца (вызывается каждый тик)."""


class SimpleTamagochi(AbstractTamagochi):
    """Конкретный питомец с голодом, усталостью, здоровьем и энергией.

    Показатели кроме здоровья лежат в диапазоне
    ``MIN_STAT..MAX_STAT``. Здоровье может уйти в минус — это гибель.
    """

    def __init__(self, name: str = constants.DEFAULT_NAME) -> None:
        """Создать питомца.

        :param name: имя питомца.
        """
        self._name = name
        self._hunger = constants.INITIAL_HUNGER
        self._fatigue = constants.INITIAL_FATIGUE
        self._hp = constants.INITIAL_HP
        self._energy = constants.INITIAL_ENERGY
        self._sick = False

    @property
    def name(self) -> str:
        """Вернуть имя питомца."""
        return self._name

    def feed(self, food: Food) -> None:
        """Накормить питомца: снять голод ценой небольшой энергии.

        :param food: еда, которой кормят.
        :raises TamagochiIsDeadError: если питомец погиб.
        """
        self._ensure_alive()
        self._hunger = self._clamp(self._hunger - food.satiety)
        self._energy = self._clamp(self._energy - constants.FEED_ENERGY_COST)
        self._fatigue = self._clamp(self._fatigue + constants.FEED_FATIGUE_GAIN)

    def play(self) -> None:
        """Поиграть: поднять здоровье, потратив энергию и нагуляв аппетит.

        :raises TamagochiIsDeadError: если питомец погиб.
        """
        self._ensure_alive()
        self._energy = self._clamp(self._energy - constants.PLAY_ENERGY_COST)
        self._fatigue = self._clamp(self._fatigue + constants.PLAY_FATIGUE_GAIN)
        self._hunger = self._clamp(self._hunger + constants.PLAY_HUNGER_GAIN)
        self._hp = self._clamp(self._hp + constants.PLAY_HP_GAIN)

    def rest(self) -> None:
        """Отдохнуть: восстановить энергию. Больной питомец отдыхает хуже.

        :raises TamagochiIsDeadError: если питомец погиб.
        """
        self._ensure_alive()
        recovery = (
            constants.REST_ENERGY_RECOVERY_SICK
            if self._sick
            else constants.REST_ENERGY_RECOVERY
        )
        self._energy = self._clamp(self._energy + recovery)
        self._fatigue = self._clamp(
            self._fatigue - constants.REST_FATIGUE_RECOVERY
        )
        self._hunger = self._clamp(self._hunger + constants.REST_HUNGER_GAIN)

    def heal(self, medicine: Medicine) -> None:
        """Вылечить питомца лекарством.

        :param medicine: применяемое лекарство.
        :raises TamagochiIsDeadError: если питомец погиб.
        :raises TamagochiIsNotSickError: если питомец здоров.
        :raises EmptyMedicineError: если лекарство закончилось.
        """
        self._ensure_alive()
        if not self._sick:
            raise TamagochiIsNotSickError(f'{self._name} не болен, лечение не нужно')
        if medicine.is_empty():
            raise EmptyMedicineError(f'Лекарство {medicine.name} закончилось')

        medicine.uses += 1
        self._hp = self._clamp(self._hp + medicine.heal_hp)
        self._fatigue = self._clamp(
            self._fatigue - constants.HEAL_FATIGUE_RECOVERY
        )
        self._sick = False

    def status(self) -> dict[str, int]:
        """Вернуть словарь со всеми показателями питомца.

        :return: ключи ``hunger``, ``fatigue``, ``hp``, ``energy``.
        """
        return {
            'hunger': self._hunger,
            'fatigue': self._fatigue,
            'hp': self._hp,
            'energy': self._energy,
        }

    def is_alive(self) -> bool:
        """Проверить, жив ли питомец.

        :return: ``False``, если здоровье упало ниже нуля.
        """
        return self._hp >= constants.MIN_STAT

    def is_sick(self) -> bool:
        """Проверить, болен ли питомец.

        :return: ``True``, если питомец болеет.
        """
        return self._sick

    def update(self) -> None:
        """Обновить состояние питомца: один игровой тик.

        Голод и усталость растут, энергия падает. Голодный, уставший или
        больной питомец теряет здоровье и может заболеть.
        """
        if not self.is_alive():
            return

        self._hunger = self._clamp(
            self._hunger
            + random.randint(
                constants.HUNGER_GROWTH_MIN, constants.HUNGER_GROWTH_MAX
            )
        )
        self._fatigue = self._clamp(
            self._fatigue
            + random.randint(
                constants.FATIGUE_GROWTH_MIN, constants.FATIGUE_GROWTH_MAX
            )
        )

        energy_drain = constants.ENERGY_DRAIN
        if self._fatigue > constants.TIRED_FATIGUE_THRESHOLD:
            energy_drain = constants.ENERGY_DRAIN_TIRED

        if self._sick:
            energy_drain += constants.SICK_ENERGY_DRAIN_EXTRA
            self._fatigue = self._clamp(
                self._fatigue + constants.SICK_FATIGUE_GAIN
            )
            self._hp -= constants.SICK_HP_LOSS

        self._energy = self._clamp(self._energy - energy_drain)

        if self._hunger > constants.HUNGER_CRITICAL_THRESHOLD:
            self._hp -= constants.HUNGER_HP_LOSS
        if self._energy == constants.MIN_STAT:
            self._hp -= constants.ENERGY_HP_LOSS

        if not self._sick and self._hp > constants.MIN_STAT:
            self._try_to_get_sick()

    def __repr__(self) -> str:
        """Вернуть читаемое представление питомца."""
        return f'SimpleTamagochi(name={self._name!r}, status={self.status()})'

    def _try_to_get_sick(self) -> None:
        """С некоторой вероятностью заразить питомца болезнью."""
        vulnerable = (
            self._hunger > constants.SICK_VULNERABLE_HUNGER
            or self._energy < constants.SICK_VULNERABLE_ENERGY
            or self._fatigue > constants.SICK_VULNERABLE_FATIGUE
        )
        chance = (
            constants.SICK_CHANCE_VULNERABLE
            if vulnerable
            else constants.SICK_CHANCE_DEFAULT
        )
        if random.random() < chance:
            self._sick = True

    def _ensure_alive(self) -> None:
        """Проверить, что питомец жив.

        :raises TamagochiIsDeadError: если питомец погиб.
        """
        if not self.is_alive():
            raise TamagochiIsDeadError(f'{self._name} погиб, игра окончена')

    @staticmethod
    def _clamp(value: int) -> int:
        """Ограничить значение диапазоном допустимых показателей.

        :param value: исходное значение.
        :return: значение внутри ``MIN_STAT..MAX_STAT``.
        """
        return max(constants.MIN_STAT, min(constants.MAX_STAT, value))
