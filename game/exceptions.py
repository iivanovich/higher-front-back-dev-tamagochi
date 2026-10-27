class GameOverError(Exception):
    """Игра окончена: питомец умер или достигнуто условие проигрыша."""


class InvalidActionError(Exception):
    """Недопустимое действие (например, покупка из пустого списка)."""


class NotEnoughMoney(Exception):
    """Недостаточно монет для покупки."""


class TamagochiIsGone(Exception):
    """Питомец недоступен (удалён или окончательно исчез)."""

