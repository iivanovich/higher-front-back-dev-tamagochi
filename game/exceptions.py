class GameError(Exception):
    """Базовый класс для всех игровых исключений."""
    pass


class TamagochiIsGone(GameError):
    """Исключение, которое выбрасывается."""
    pass


class NotEnoughMoney(GameError):
    """Исключение при нехватке денег для действия."""
    pass


class InvalidActionError(GameError):
    """Исключение для недопустимых действий в игровой логике."""
    pass
