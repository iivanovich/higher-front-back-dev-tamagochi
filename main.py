import os

from game.clicker import SimpleRandomClicker
from game.constants import MAX_HP
from game.exceptions import GameError, TamagochiIsGone, NotEnoughMoney, InvalidActionError
from game.game import SimpleGame
from game.models import Food, Medicine
from game.tamagochi import SimpleTamagochi


MENU_ITEMS = [
    "1. Пойти на работу (кликер)",
    "2. Купить еду",
    "3. Купить лекарство",
    "4. Покормить питомца",
    "5. Вылечить питомца",
    "6. Поиграть с питомцем",
    "7. Отдых",
    "0. Выход",
]
MENU = "\n".join(MENU_ITEMS)

STATUS_TEMPLATE = (
    "\nСтатус: голод {hunger}, здоровье {hp}, энергия {energy}, монеты {coins}\n"
)

WELCOME_MESSAGE = "Добро пожаловать в тамагочи-кликер!"
GAME_OVER_MESSAGE = "\n💀 Игра окончена: ваш питомец умер."
ERROR_NOT_ENOUGH_MONEY = "💸 Недостаточно монет для покупки."
ERROR_INVALID_ACTION = "⚠️ Невозможно выполнить действие: {message}"


def _clear_console():
    os.system("clear" if os.name != "nt" else "cls")


def main():
    all_food = [
        Food(name="Бургер", satiety=20, price=40),
        Food(name="Салат", satiety=10, price=20),
        Food(name="Яблоко", satiety=10, price=15),
        Food(name="Йогурт", satiety=8, price=12),
        Food(name="Печенье", satiety=15, price=25),
    ]

    all_medicine = [
        Medicine(name="Ибупрофен", price=30, heal_hp=20, number_of_uses=2),
        Medicine(name="Витамин C", price=25, heal_hp=10, number_of_uses=3),
        Medicine(name="Эликсир здоровья", price=60, heal_hp=40, number_of_uses=1),
    ]

    tamagochi = SimpleTamagochi(name="Пушистик")
    clicker = SimpleRandomClicker(min_income=5, max_income=20)
    game = SimpleGame(
        tamagochi=tamagochi,
        clicker=clicker,
        all_food=all_food,
        all_medicine=all_medicine,
    )

    print(WELCOME_MESSAGE)
    output = ""

    while True:
        _clear_console()
        print(output)
        output = ""  

        print(f"Сумка с едой: {[f.name for f in game.food]}")
        print(f"Сумка с лекарствами: {[m.name for m in game.medicine]}")

        status = game.get_status()
        print(STATUS_TEMPLATE.format(**status))

        if game._tamagochi.is_sick():
            print("======= Питомец болеет! =======")
            print("======= Отдых действует менее эффективно. =======")

        print(MENU)

        choice = input("Выберите действие: ").strip()

        try:
            match choice:
                case "1":
                    income = game.work()
                    output = f"Вы заработали {income} монет."

                case "2":
                    if not game._all_food:
                        raise InvalidActionError("Нет доступной еды для покупки.")
                    print("Доступные товары:")
                    for i, f in enumerate(game.all_food):
                        print(f"{i}. {f.name} (сытость {f.satiety}, цена {f.price})")
                    idx = int(input("Введите индекс товара: ").strip())
                    game.buy_food(idx)
                    output = "Еда куплена."

                case "3":
                    if not game.all_medicine:
                        raise InvalidActionError("Нет доступных лекарств для покупки.")
                    print("Доступные лекарства:")
                    for i, m in enumerate(game.all_medicine):
                        print(
                            f"{i}. {m.name} (лечение {m.heal_hp} HP, "
                            f"использований {m.number_of_uses}, цена {m.price})"
                        )
                    idx = int(input("Введите индекс лекарства: ").strip())
                    game.buy_medicine(idx)
                    output = "Лекарство куплено."

                case "4":
                    if not game.food:
                        raise InvalidActionError("Нет еды в инвентаре.")
                    print("Еда в инвентаре:")
                    for i, f in enumerate(game.food):
                        print(f"{i}. {f.name} (сытость {f.satiety})")
                    idx = int(input("Чем покормить питомца? Введите индекс: ").strip())
                    game.feed_tamagochi(idx)
                    output = "Питомец покормлен."

                case "5":
                    if not game.medicine:
                        raise InvalidActionError("Нет лекарств в инвентаре.")
                    print("Лекарства в инвентаре:")
                    for i, m in enumerate(game.medicine):
                        remaining = m.number_of_uses - m.uses
                        print(f"{i}. {m.name} (осталось использований: {remaining})")
                    idx = int(input("Какое лекарство дать питомцу? Введите индекс: ").strip())
                    game.heal_tamagochi(idx)
                    output = "Питомцу дали лекарство."

                case "6":
                    game.play_with_tamagochi()
                    output = "Вы поиграли с питомцем."

                case "7":
                    game.rest_tamagochi()
                    output = "Питомец отдохнул."

                case "0":
                    print("До свидания!")
                    break

                case _:
                    output = "Неверная команда. Выберите число от 0 до 7."

        except (NotEnoughMoney, InvalidActionError) as e:
            if isinstance(e, NotEnoughMoney):
                output = ERROR_NOT_ENOUGH_MONEY
            else:
                output = ERROR_INVALID_ACTION.format(message=str(e))

        except TamagochiIsGone:
            _clear_console()
            print(GAME_OVER_MESSAGE)
            break

        except ValueError:
            output = "Ошибка ввода: введите корректный индекс (число)."


if __name__ == "__main__":
    main()
