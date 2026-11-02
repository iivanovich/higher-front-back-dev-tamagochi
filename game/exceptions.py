class GameOverError(Exception):
    """
    Исключение сигнала окончания игры: например, питомец погиб.
    """


class InvalidActionError(Exception):
    """
    Неверное действие или неправильный выбор игрока.
    """


class NotEnoughMoney(Exception):
    """
    Недостаточно средств для покупки предмета.
    """


class TamagochiIsGone(Exception):
    """
    Исключение для случая, когда питомец мёртв и действия невозможны.
    """

    
class MedicineIsGone(Exception):
    """Лекарство закончилось."""
