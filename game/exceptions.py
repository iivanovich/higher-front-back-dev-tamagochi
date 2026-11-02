class GameOverError(Exception):
    """Питомец погиб, дальнейшие действия невозможны."""


class InvalidActionError(Exception):
    """Недопустимое действие."""


class NotEnoughMoney(Exception):
    """Недостаточно монет для совершения действия."""


class TamagochiIsGone(Exception):
    """Питомец погиб."""