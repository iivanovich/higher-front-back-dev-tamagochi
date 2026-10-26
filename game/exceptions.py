# game/exceptions.py

class GameOverError(Exception):
    """Исключение, сигнализирующее о завершении игры (питомец умер)."""


class NotEnoughMoneyError(Exception):
    """Исключение для случаев, когда у игрока недостаточно монет."""


class InvalidActionError(Exception):
    """Исключение для недопустимых действий (например, попытка использовать пустой предмет)."""


class TamagochiIsGone(Exception):
    """Исключение, когда питомец умер и дальнейшие действия с ним невозможны."""
