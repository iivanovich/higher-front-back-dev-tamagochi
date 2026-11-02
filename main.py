import os

from game import constants
from game.clicker import SimpleRandomClicker
from game.exceptions import GameError
from game.game import SimpleGame
from game.models import Food, Medicine
from game.tamagochi import SimpleTamagochi


def build_game() -> SimpleGame:
    """Собрать игру с ассортиментом магазина по умолчанию.

    :return: готовый к запуску объект игры.
    """
    all_food = [
        Food(name=name, satiety=satiety, price=price)
        for name, satiety, price in constants.DEFAULT_FOOD
    ]

    all_medicine = [
        Medicine(
            name=name,
            price=price,
            heal_hp=heal_hp,
            number_of_uses=number_of_uses,
        )
        for name, price, heal_hp, number_of_uses in constants.DEFAULT_MEDICINE
    ]

    return SimpleGame(
        SimpleTamagochi(constants.DEFAULT_NAME),
        SimpleRandomClicker(
            constants.DEFAULT_MIN_INCOME,
            constants.DEFAULT_MAX_INCOME,
        ),
        all_food=all_food,
        all_medicine=all_medicine,
    )


def print_menu() -> None:
    """Вывести меню доступных действий."""
    for code, title in constants.MENU.items():
        print(f'{code}. {title}')


def main() -> None:
    """Запустить консольную игру «Тамагочи-кликер»."""
    game = build_game()

    print(constants.WELCOME_MESSAGE)
    output = ''

    while True:
        print(output)

        print(f'Сумка с едой: {game.food}')
        print(f'Сумка с лекарствами: {game.medicine}')

        status = game.get_status()
        print(
            f"\nСтатус: голод {status['hunger']}, здоровье {status['hp']}, "
            f"энергия {status['energy']}, монет {status['coins']}\n"
        )
        if game.tamagochi.is_sick():
            print(constants.SICK_WARNING)
        if status['game_over']:
            print(constants.DEAD_TAMAGOCHI_MESSAGE)
            break

        print_menu()

        try:
            choice = input('Выберите действие: ')
        except (EOFError, KeyboardInterrupt):
            break

        match choice:
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
                output = constants.WRONG_COMMAND_MESSAGE

        os.system('clear')


if __name__ == '__main__':
    try:
        main()
    except GameError as error:
        print(f'Игра прервана: {error}')
