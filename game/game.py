"""Сущность игры: связывает питомца, кликер и ресурсы.

Класс игры знает только контракты компонентов. Что именно происходит
внутри ``click`` или ``feed`` — его не касается: он отдаёт команды и
следит за состоянием партии.
"""

from abc import ABC, abstractmethod

from game import constants
from game.clicker import AbstractClicker
from game.exceptions import (
    EmptyInventoryError,
    GameError,
    InvalidChoiceError,
)
from game.models import Food, Medicine
from game.tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    """Интерфейс игры."""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Инициализировать игру.

        :param tamagochi: питомец.
        :param clicker: кликер, выдающий монеты.
        :param all_food: доступный в магазине ассортимент еды.
        :param all_medicine: доступный в магазине ассортимент лекарств.
        """

    @abstractmethod
    def work(self) -> int:
        """Пойти на работу: заработать монеты кликом."""

    @abstractmethod
    def buy_food(self) -> None:
        """Купить еду."""

    @abstractmethod
    def buy_medicine(self) -> None:
        """Купить лекарство."""

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Покормить питомца едой из сумки."""

    @abstractmethod
    def heal_tamagochi(self) -> None:
        """Вылечить питомца лекарством из сумки."""

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Дать питомцу отдохнуть."""

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Поиграть с питомцем."""

    @abstractmethod
    def get_status(self) -> dict[str, int]:
        """Получить статус игры."""

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """Вернуть сумку с едой."""

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """Вернуть сумку с лекарствами."""


class SimpleGame(AbstractGame):
    """Конкретная реализация игры.

    Действия не выбрасывают исключения наружу: игровые ошибки (нехватка
    монет, пустая сумка и т. п.) перехватываются и печатаются как сообщения,
    чтобы игровой цикл продолжался.
    """

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food] | None = None,
        all_medicine: list[Medicine] | None = None,
    ) -> None:
        """Создать игру.

        :param tamagochi: питомец.
        :param clicker: кликер, выдающий монеты.
        :param all_food: ассортимент магазина еды.
        :param all_medicine: ассортимент магазина лекарств.
        """
        self._tamagochi = tamagochi
        self._clicker = clicker
        self._store_food = list(all_food or [])
        self._store_medicine = list(all_medicine or [])
        self._bag_food: list[Food] = []
        self._bag_medicine: list[Medicine] = []
        self._is_over = False

    @property
    def tamagochi(self) -> AbstractTamagochi:
        """Вернуть питомца."""
        return self._tamagochi

    @property
    def clicker(self) -> AbstractClicker:
        """Вернуть кликер."""
        return self._clicker

    def work(self) -> int:
        """Пойти на работу и заработать монеты.

        Обновление состояния питомца выполняет вызывающий код (игровой
        цикл), чтобы за один ход происходил ровно один тик.

        :return: сколько монет заработано за клик.
        """
        if self._check_game_over():
            return 0
        self._clicker.click()
        return self._clicker.income_per_click()

    def buy_food(self, index: int | None = None) -> None:
        """Купить еду и положить её в сумку.

        :param index: номер еды в магазине; если не указан, игрок выбирает
            её в консоли.
        """
        if self._check_game_over():
            return
        try:
            position = self._resolve_choice(self._store_food, index, 'еды')
            item = self._store_food[position]
            self._clicker.spend(item.price)
            self._bag_food.append(Food(item.name, item.satiety, item.price))
            print(f'Куплено: {item.name}')
        except GameError as error:
            print(f'Не удалось купить: {error}')

    def buy_medicine(self, index: int | None = None) -> None:
        """Купить лекарство и положить его в сумку.

        :param index: номер лекарства в магазине; если не указан, игрок
            выбирает его в консоли.
        """
        if self._check_game_over():
            return
        try:
            position = self._resolve_choice(self._store_medicine, index, 'лекарств')
            item = self._store_medicine[position]
            self._clicker.spend(item.price)
            self._bag_medicine.append(
                Medicine(
                    name=item.name,
                    price=item.price,
                    heal_hp=item.heal_hp,
                    number_of_uses=item.number_of_uses,
                )
            )
            print(f'Куплено: {item.name}')
        except GameError as error:
            print(f'Не удалось купить: {error}')

    def feed_tamagochi(self, index: int | None = None) -> None:
        """Покормить питомца едой из сумки.

        :param index: номер еды в сумке; если не указан, игрок выбирает
            её в консоли.
        """
        if self._check_game_over():
            return
        try:
            position = self._resolve_choice(self._bag_food, index, 'еды в сумке')
            food = self._bag_food[position]
            self._tamagochi.feed(food)
            self._bag_food.pop(position)
            print(f'Питомец съел: {food.name}')
        except GameError as error:
            print(f'Не удалось покормить: {error}')

    def heal_tamagochi(self, index: int | None = None) -> None:
        """Вылечить питомца лекарством из сумки.

        :param index: номер лекарства в сумке; если не указан, игрок
            выбирает его в консоли.
        """
        if self._check_game_over():
            return
        try:
            position = self._resolve_choice(
                self._bag_medicine, index, 'лекарств в сумке'
            )
            medicine = self._bag_medicine[position]
            self._tamagochi.heal(medicine)
            if medicine.is_empty():
                self._bag_medicine.pop(position)
            print(f'Питомец вылечен: {medicine.name}')
        except GameError as error:
            print(f'Не удалось вылечить: {error}')

    def rest_tamagochi(self) -> None:
        """Дать питомцу отдохнуть."""
        if self._check_game_over():
            return
        try:
            self._tamagochi.rest()
        except GameError as error:
            print(error)

    def play_with_tamagochi(self) -> None:
        """Поиграть с питомцем."""
        if self._check_game_over():
            return
        try:
            self._tamagochi.play()
        except GameError as error:
            print(error)

    def get_status(self) -> dict[str, int]:
        """Собрать полный статус партии.

        :return: показатели питомца, количество монет и признак окончания
            игры (``game_over``: 0 или 1).
        """
        status = dict(self._tamagochi.status())
        status['coins'] = self._clicker.coins
        status['game_over'] = int(self.is_over())
        return status

    @property
    def food(self) -> list[Food]:
        """Вернуть сумку с едой."""
        return list(self._bag_food)

    @property
    def medicine(self) -> list[Medicine]:
        """Вернуть сумку с лекарствами."""
        return list(self._bag_medicine)

    def is_over(self) -> bool:
        """Проверить, закончилась ли игра.

        :return: ``True``, если питомец погиб.
        """
        if not self._tamagochi.is_alive():
            self._is_over = True
        return self._is_over

    def __repr__(self) -> str:
        """Вернуть читаемое представление игры."""
        return (
            f'SimpleGame(tamagochi={self._tamagochi!r}, '
            f'food={len(self._bag_food)}, medicine={len(self._bag_medicine)})'
        )

    def _check_game_over(self) -> bool:
        """Проверить окончание игры и сообщить о нём игроку.

        :return: ``True``, если игра уже закончена.
        """
        if self.is_over():
            print(constants.GAME_OVER_MESSAGE)
            return True
        return False

    @staticmethod
    def _describe(item: Food | Medicine) -> str:
        """Вернуть краткое описание предмета для меню выбора.

        :param item: еда или лекарство.
        :return: строка вида «Бургер — 40 монет (насыщение 20)».
        """
        if isinstance(item, Food):
            return f'{item.name} — {item.price} монет (насыщение {item.satiety})'
        return (
            f'{item.name} — {item.price} монет '
            f'(лечит {item.heal_hp}, осталось {item.number_of_uses - item.uses})'
        )

    @staticmethod
    def _resolve_choice(
        items: list[Food] | list[Medicine],
        index: int | None,
        what: str,
    ) -> int:
        """Определить индекс выбранного предмета.

        :param items: список доступных предметов.
        :param index: индекс, переданный программно, или ``None``.
        :param what: название категории для сообщений («еды», «лекарств»).
        :return: индекс предмета в списке.
        :raises EmptyInventoryError: если список пуст.
        :raises InvalidChoiceError: если выбран несуществующий номер.
        """
        if not items:
            raise EmptyInventoryError(f'Нет доступной {what}')
        if index is None:
            for number, item in enumerate(items):
                print(f'{number}. {SimpleGame._describe(item)}')
            try:
                index = int(input(f'Введите номер ({what}): ').strip())
            except ValueError as error:
                raise InvalidChoiceError('Номер должен быть числом') from error
        if not 0 <= index < len(items):
            raise InvalidChoiceError(f'Нет предмета с номером {index}')
        return index
