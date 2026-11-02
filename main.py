import os

from game.clicker import SimpleRandomClicker
from game.exceptions import (
    GameOverError,
    InvalidActionError,
    NotEnoughMoney,
    TamagochiIsGone,
)
from game.game import SimpleGame
from game.models import Food, Medicine
from game.tamagochi import SimpleTamagochi

STATUS_LINE = "Статус: голод {hunger}, здоровье {hp}, энергия {energy}, усталость {fatigue}, монет {coins}\n"

def choose_from_list(objects, msg: str) -> int:
    for idx, obj in enumerate(objects):
        print(f"{idx + 1}. {obj}")
    try:
        choice = int(input(msg)) - 1
    except ValueError:
        return -1
    return choice

def main():
    all_food = [
        Food(name='Бургер', satiety=20, price=40),
        Food(name='Салат', satiety=10, price=20),
        Food(name='Яблоко', satiety=10, price=15),
        Food(name='Суп', satiety=8, price=12),
        Food(name='Пицца', satiety=15, price=25),
    ]

    all_medicine = [
        Medicine(name='Ибупрофен', price=30, heal_hp=20, number_of_uses=2),
        Medicine(name='Витамин C', price=25, heal_hp=10, number_of_uses=3),
        Medicine(name='Антибиотик', price=60, heal_hp=40, number_of_uses=1),
    ]

    tamagochi = SimpleTamagochi(name='Лапуля')
    clicker = SimpleRandomClicker(min_income=5, max_income=20)
    game = SimpleGame(
        tamagochi=tamagochi,
        clicker=clicker,
        all_food=all_food,
        all_medicine=all_medicine,
    )

    print("Добро пожаловать в тамагочи-кликер!")
    output = ""
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        if output:
            print(output)
        output = ""

        print(f"Сумка с едой: {[f.name for f in game.food]}")
        print(f"Сумка с лекарствами: {[m.name for m in game.medicine]}")
        print(STATUS_LINE.format(**game.get_status()))

        if tamagochi.is_sick():
            print("=======Тамагочи болеет======")
            print("=======Отдых действует менее эффективно=======")
        menu_lines = [
            "1. Пойти на работу (получить монетки)",
            "2. Купить Еду",
            "3. Купить Лекарство",
            "4. Покормить питомца",
            "5. Вылечить питомца",
            "6. Играть с питомцем",
            "7. Отдыхать",
            "0. Выход",
        ]
        print("\n".join(menu_lines))

        choice = input("Выберите действие: ").strip()
        try:
            match choice:
                case "1":
                    income = game.work()
                    output = f"Вы заработали {income} монет."
                case "2":
                    idx = choose_from_list(game._all_food, "Выберите еду для покупки: ")
                    game.buy_food(idx)
                    output = "Еда куплена."
                case "3":
                    idx = choose_from_list(game._all_medicine, "Выберите лекарство для покупки: ")
                    game.buy_medicine(idx)
                    output = "Лекарство куплено."
                case "4":
                    if not game.food:
                        output = "В сумке нет еды!"
                    else:
                        idx = choose_from_list(game.food, "Выберите еду для кормления: ")
                        game.feed_tamagochi(idx)
                        output = "Питомец накормлен."
                case "5":
                    if not game.medicine:
                        output = "В сумке нет лекарств!"
                    else:
                        idx = choose_from_list(game.medicine, "Выберите лекарство для лечения: ")
                        game.heal_tamagochi(idx)
                        output = "Питомец вылечен."
                case "6":
                    game.play_with_tamagochi()
                    output = "Вы поиграли с питомцем."
                case "7":
                    game.rest_tamagochi()
                    output = "Питомец отдохнул."
                case "0":
                    print("Пока!")
                    break
                case _:
                    output = "Неверная команда"
        except (InvalidActionError, NotEnoughMoney) as e:
            output = str(e)
        except (GameOverError, TamagochiIsGone):
            print("\nКонец игры: питомец погиб.\n")
            break