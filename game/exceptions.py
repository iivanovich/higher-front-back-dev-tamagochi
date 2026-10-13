# game/exceptions.py
class GameOverError(Exception):
    """Игра окончена: питомец умер."""


class NotEnoughMoneyError(Exception):
    """Недостаточно монет для покупки."""


class InvalidActionError(Exception):
    """Недопустимое действие (например, попытка использовать пустое лекарство)."""
