"""Кастомные исключения игры «Тамагочи».

Все ошибки наследуются от общего базового класса :class:`GameError`,
поэтому клиентский код может ловить их как по отдельности, так и пачкой.
"""


class GameError(Exception):
    """Базовое исключение для всех ошибок игры."""


class NotEnoughCoinsError(GameError):
    """Не хватает монет для покупки."""


class TamagochiIsDeadError(GameError):
    """Действие невозможно: питомец уже погиб."""


class TamagochiIsNotSickError(GameError):
    """Питомца нельзя лечить: он здоров."""


class EmptyMedicineError(GameError):
    """Лекарство закончилось: использований не осталось."""


class EmptyInventoryError(GameError):
    """В сумке нет подходящего предмета (еды или лекарства)."""


class InvalidChoiceError(GameError):
    """Выбран несуществующий индекс при выборе еды или лекарства."""
