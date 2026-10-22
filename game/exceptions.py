class GameOverError(Exception):
    pass

class NotEnoughMoneyError(Exception):
    pass

class InvalidActionError(Exception):
    pass

class TamagochiIsGone(Exception):
    """Исключение, когда питомец умер."""

class NotEnoughMoney(Exception):
    """Исключение для случаев нехватки денег."""
