class GameOverError(Exception):
    """Вызывается, когда игра завершена из-за смерти питомца."""

class InvalidActionError(Exception):
    """Вызывается при недопустимом действии в игре."""

class NotEnoughMoney(Exception):
    """Вызывается, если пользователю не хватает монет."""

class TamagochiIsGone(Exception):
    """Вызывается, если питомец умер и любое действие невозможно."""
