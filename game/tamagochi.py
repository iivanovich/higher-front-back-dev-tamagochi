"""Логика питомца-тамагочи.

Класс :class:`SimpleTamagochi` ничего не знает о деньгах, магазинах и меню
игры: он лишь меняет собственные показатели в ответ на действия.

Значения по умолчанию берутся из :mod:`game.constants`; если какого-то
ключа там нет, используется запасное значение, поэтому игра продолжает
работать даже с неполным файлом констант.
"""

import random
from abc import ABC, abstractmethod
from typing import Any

from game.exceptions import EmptyMedicine, TamagochiIsGone
from game.models import Food, Medicine

try:
    from game import constants
except ImportError:  # pragma: no cover - страховка на случай отсутствия файла
    constants = None  # type: ignore[assignment]


def _const(name: str, default: Any) -> Any:
    """Прочитать константу игры, подставив значение по умолчанию.

    :param name: имя константы в модуле ``game.constants``.
    :param default: значение, если константа не определена.
    :return: значение константы или ``default``.
    """
    return getattr(constants, name, default)


MIN_STAT = _const('MIN_STAT', 0)
MAX_STAT = _const('MAX_STAT', 100)
DEFAULT_NAME = _const('DEFAULT_NAME', 'Кот')
INITIAL_HUNGER = _const('INITIAL_HUNGER', 30)
INITIAL_FATIGUE = _const('INITIAL_FATIGUE', 10)
INITIAL_HP = _const('INITIAL_HP', 100)
INITIAL_ENERGY = _const('INITIAL_ENERGY', 80)

FEED_ENERGY_COST = _const('FEED_ENERGY_COST', 3)
FEED_FATIGUE_GAIN = _const('FEED_FATIGUE_GAIN', 2)

PLAY_ENERGY_COST = _const('PLAY_ENERGY_COST', 12)
PLAY_FATIGUE_GAIN = _const('PLAY_FATIGUE_GAIN', 10)
PLAY_HUNGER_GAIN = _const('PLAY_HUNGER_GAIN', 8)
PLAY_HP_GAIN = _const('PLAY_HP_GAIN', 2)

REST_ENERGY_RECOVERY = _const('REST_ENERGY_RECOVERY', 40)
REST_ENERGY_RECOVERY_SICK = _const('REST_ENERGY_RECOVERY_SICK', 20)
REST_FATIGUE_RECOVERY = _const('REST_FATIGUE_RECOVERY', 40)
REST_HUNGER_GAIN = _const('REST_HUNGER_GAIN', 6)

HEAL_FATIGUE_RECOVERY = _const('HEAL_FATIGUE_RECOVERY', 10)

HUNGER_GROWTH_MIN = _const('HUNGER_GROWTH_MIN', 2)
HUNGER_GROWTH_MAX = _const('HUNGER_GROWTH_MAX', 5)
FATIGUE_GROWTH_MIN = _const('FATIGUE_GROWTH_MIN', 1)
FATIGUE_GROWTH_MAX = _const('FATIGUE_GROWTH_MAX', 3)
ENERGY_DRAIN = _const('ENERGY_DRAIN', 1)
ENERGY_DRAIN_TIRED = _const('ENERGY_DRAIN_TIRED', 3)
TIRED_FATIGUE_THRESHOLD = _const('TIRED_FATIGUE_THRESHOLD', 70)

SICK_HP_LOSS = _const('SICK_HP_LOSS', 5)
SICK_ENERGY_DRAIN_EXTRA = _const('SICK_ENERGY_DRAIN_EXTRA', 2)
SICK_FATIGUE_GAIN = _const('SICK_FATIGUE_GAIN', 2)

HUNGER_CRITICAL_THRESHOLD = _const('HUNGER_CRITICAL_THRESHOLD', 85)
HUNGER_HP_LOSS = _const('HUNGER_HP_LOSS', 3)
ENERGY_HP_LOSS = _const('ENERGY_HP_LOSS', 2)

SICK_CHANCE_DEFAULT = _const('SICK_CHANCE_DEFAULT', 0.10)
SICK_CHANCE_VULNERABLE = _const('SICK_CHANCE_VULNERABLE', 0.35)
SICK_VULNERABLE_HUNGER = _const('SICK_VULNERABLE_HUNGER', 70)
SICK_VULNERABLE_ENERGY = _const('SICK_VULNERABLE_ENERGY', 30)
SICK_VULNERABLE_FATIGUE = _const('SICK_VULNERABLE_FATIGUE', 70)


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

    Голод, усталость и энергия лежат в диапазоне ``MIN_STAT..MAX_STAT``.
    Здоровье может уйти в минус — это гибель питомца.
    """

    def __init__(self, name: str = DEFAULT_NAME) -> None:
        """Создать питомца.

        :param name: имя питомца.
        """
        self._name = name
        self._hunger = INITIAL_HUNGER
        self._fatigue = INITIAL_FATIGUE
        self._hp = INITIAL_HP
        self._energy = INITIAL_ENERGY
        self._sick = False

    @property
    def name(self) -> str:
        """Вернуть имя питомца."""
        return self._name

    @property
    def hunger(self) -> int:
        """Вернуть текущий голод."""
        return self._hunger

    @hunger.setter
    def hunger(self, value: int) -> None:
        """Задать голод питомца.

        :param value: новое значение голода.
        """
        self._hunger = self._clamp(value)

    @property
    def fatigue(self) -> int:
        """Вернуть текущую усталость."""
        return self._fatigue

    @fatigue.setter
    def fatigue(self, value: int) -> None:
        """Задать усталость питомца.

        :param value: новое значение усталости.
        """
        self._fatigue = self._clamp(value)

    @property
    def hp(self) -> int:
        """Вернуть текущее здоровье."""
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        """Задать здоровье питомца.

        :param value: новое значение здоровья; может быть отрицательным.
        """
        self._hp = value

    @property
    def energy(self) -> int:
        """Вернуть текущую энергию."""
        return self._energy

    @energy.setter
    def energy(self, value: int) -> None:
        """Задать энергию питомца.

        :param value: новое значение энергии.
        """
        self._energy = self._clamp(value)

    def feed(self, food: Food) -> None:
        """Накормить питомца: снять голод ценой небольшой энергии.

        :param food: еда, которой кормят.
        :raises TamagochiIsGone: если питомец погиб.
        """
        self._ensure_alive()
        self._hunger = self._clamp(self._hunger - food.satiety)
        self._energy = self._clamp(self._energy - FEED_ENERGY_COST)
        self._fatigue = self._clamp(self._fatigue + FEED_FATIGUE_GAIN)

    def play(self) -> None:
        """Поиграть: поднять здоровье, потратив энергию и нагуляв аппетит.

        :raises TamagochiIsGone: если питомец погиб.
        """
        self._ensure_alive()
        self._energy = self._clamp(self._energy - PLAY_ENERGY_COST)
        self._fatigue = self._clamp(self._fatigue + PLAY_FATIGUE_GAIN)
        self._hunger = self._clamp(self._hunger + PLAY_HUNGER_GAIN)
        self._hp += PLAY_HP_GAIN

    def rest(self) -> None:
        """Отдохнуть: восстановить энергию. Больной питомец отдыхает хуже.

        :raises TamagochiIsGone: если питомец погиб.
        """
        self._ensure_alive()
        recovery = (
            REST_ENERGY_RECOVERY_SICK if self._sick else REST_ENERGY_RECOVERY
        )
        self._energy = self._clamp(self._energy + recovery)
        self._fatigue = self._clamp(self._fatigue - REST_FATIGUE_RECOVERY)
        self._hunger = self._clamp(self._hunger + REST_HUNGER_GAIN)

    def heal(self, medicine: Medicine) -> None:
        """Вылечить питомца лекарством.

        Лечение применяется всегда, когда есть чем лечить: у здорового
        питомца оно просто восстанавливает здоровье и снимает усталость,
        а болезнь снимает полностью.

        :param medicine: применяемое лекарство.
        :raises TamagochiIsGone: если питомец погиб.
        :raises EmptyMedicine: если лекарство закончилось.
        """
        self._ensure_alive()
        if medicine.is_empty():
            raise EmptyMedicine(f'Лекарство {medicine.name} закончилось')

        medicine.uses += 1
        self._hp += medicine.heal_hp
        self._fatigue = self._clamp(self._fatigue - HEAL_FATIGUE_RECOVERY)
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
        return self._hp >= MIN_STAT

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
            self._hunger + random.randint(HUNGER_GROWTH_MIN, HUNGER_GROWTH_MAX)
        )
        self._fatigue = self._clamp(
            self._fatigue + random.randint(FATIGUE_GROWTH_MIN, FATIGUE_GROWTH_MAX)
        )

        energy_drain = ENERGY_DRAIN
        if self._fatigue > TIRED_FATIGUE_THRESHOLD:
            energy_drain = ENERGY_DRAIN_TIRED

        if self._sick:
            energy_drain += SICK_ENERGY_DRAIN_EXTRA
            self._fatigue = self._clamp(self._fatigue + SICK_FATIGUE_GAIN)
            self._hp -= SICK_HP_LOSS

        self._energy = self._clamp(self._energy - energy_drain)

        if self._hunger > HUNGER_CRITICAL_THRESHOLD:
            self._hp -= HUNGER_HP_LOSS
        if self._energy == MIN_STAT:
            self._hp -= ENERGY_HP_LOSS

        if not self._sick and self._hp > MIN_STAT:
            self._try_to_get_sick()

    def __repr__(self) -> str:
        """Вернуть читаемое представление питомца."""
        return f'SimpleTamagochi(name={self._name!r}, status={self.status()})'

    def _try_to_get_sick(self) -> None:
        """С некоторой вероятностью заразить питомца болезнью."""
        vulnerable = (
            self._hunger > SICK_VULNERABLE_HUNGER
            or self._energy < SICK_VULNERABLE_ENERGY
            or self._fatigue > SICK_VULNERABLE_FATIGUE
        )
        chance = (
            SICK_CHANCE_VULNERABLE if vulnerable else SICK_CHANCE_DEFAULT
        )
        if random.random() < chance:
            self._sick = True

    def _ensure_alive(self) -> None:
        """Проверить, что питомец жив.

        :raises TamagochiIsGone: если питомец погиб.
        """
        if not self.is_alive():
            raise TamagochiIsGone(f'{self._name} погиб, игра окончена')

    @staticmethod
    def _clamp(value: int) -> int:
        """Ограничить значение диапазоном допустимых показателей.

        :param value: исходное значение.
        :return: значение внутри ``MIN_STAT..MAX_STAT``.
        """
        return max(MIN_STAT, min(MAX_STAT, value))
