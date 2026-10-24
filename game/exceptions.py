class GameError(Exception):
    """Базовый класс для всех игровых исключений."""


class TamagochiIsGone(GameError):
    """Исключение, которое выбрасывается."""


class NotEnoughMoney(GameError):
    """Исключение при нехватке денег для действия."""


class InvalidActionError(GameError):
    """Исключение для недопустимых действий в игровой логике."""
