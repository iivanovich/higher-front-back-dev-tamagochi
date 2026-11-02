import os

from game import constants
from game.clicker import SimpleRandomClicker
from game.exceptions import GameError
from game.game import SimpleGame
from game.models import Food, Medicine
from game.tamagochi import SimpleTamagochi

# Подписи и данные читаются из модуля констант с запасными значениями,
# чтобы игра запускалась даже с устаревшей версией constants.py.
WELCOME_MESSAGE = getattr(
    constants, 'WELCOME_MESSAGE', 'Добро пожаловать в тамагочи-кликер!'
)
DEAD_TAMAGOCHI_MESSAGE = getattr(
    constants, 'DEAD_TAMAGOCHI_MESSAGE', 'Питомец погиб. Игра окончена.'
)
SICK_WARNING = getattr(
    constants,
    'SICK_WARNING',
    '=======Тамагочи болеет=======\n'
    '=======Отдых действует менее эффективно=======',
)
WRONG_COMMAND_MESSAGE = getattr(constants, 'WRONG_COMMAND_MESSAGE', 'Неверная команда')
DEFAULT_NAME = getattr(constants, 'DEFAULT_NAME', 'Кот')
MENU = getattr(
    constants,
    'MENU',
    {
        '1': 'Пойти на работу',
        '2': 'Купить еду',
        '3': 'Купить лекарство',
        '4': 'Покормить',
        '5': 'Вылечить',
        '6': 'Играть',
        '7': 'Отдых',
        '0': 'Выход',
    },
)
DEFAULT_FOOD = getattr(
    constants,
    'DEFAULT_FOOD',
    (('Бургер', 20, 40), ('Салат', 10, 20), ('Яблоко', 10, 15)),
)
DEFAULT_MEDICINE = getattr(
    constants, 'DEFAULT_MEDICINE', (('Ибупрофен', 30, 20, 2),)
)


def build_game() -> SimpleGame:
    """Собрать игру с ассортиментом магазина по умолчанию.

    :return: готовый к запуску объект игры.
    """
    all_food = [
        Food(name=name, satiety=satiety, price=price)
        for name, satiety, price in DEFAULT_FOOD
    ]

    all_medicine = [
        Medicine(
            name=name,
            price=price,
            heal_hp=heal_hp,
            number_of_uses=number_of_uses,
        )
        for name, price, heal_hp, number_of_uses in DEFAULT_MEDICINE
    ]

    return SimpleGame(
        SimpleTamagochi(DEFAULT_NAME),
        SimpleRandomClicker(),
        all_food=all_food,
        all_medicine=all_medicine,
    )


def print_menu() -> None:
    """Вывести меню доступных действий."""
    for code, title in MENU.items():
        print(f'{code}. {title}')


def main() -> None:
    """Запустить консольную игру «Тамагочи-кликер»."""
    game = build_game()

    print(WELCOME_MESSAGE)
    output = ''

    while True:
        print(output)

        print(f'Сумка с едой: {game.food()}')
        print(f'Сумка с лекарствами: {game.medicine()}')

        status = game.get_status()
        print(
            f"\nСтатус: голод {status['hunger']}, здоровье {status['hp']}, "
            f"энергия {status['energy']}, монет {status['coins']}\n"
        )
        if game.tamagochi.is_sick():
            print(SICK_WARNING)
        if not game.tamagochi.is_alive():
            print(DEAD_TAMAGOCHI_MESSAGE)
            break

        print_menu()

        try:
            choice = input('Выберите действие: ')
        except (EOFError, KeyboardInterrupt):
            break

        match choice.strip():
            case '1':
                income = game.work()
                output = f'Вы заработали {income} монет'
                game.tamagochi.update()
            case '2':
                game.buy_food()
            case '3':
                game.buy_medicine()
            case '4':
                game.feed_tamagochi()
            case '5':
                game.heal_tamagochi()
            case '6':
                game.play_with_tamagochi()
                output = 'Вы поиграли с питомцем'
                game.tamagochi.update()
            case '7':
                game.rest_tamagochi()
                output = 'Питомец отдохнул'
                game.tamagochi.update()
            case '0':
                break
            case _:
                output = WRONG_COMMAND_MESSAGE

        os.system('clear')


if __name__ == '__main__':
    try:
        main()
    except GameError as error:
        print(f'Игра прервана: {error}')
