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


def main():
    all_food = [
        Food(name="Яблоко", satiety=20, price=40),
        Food(name="Банан", satiety=10, price=20),
        Food(name="Суши", satiety=10, price=15),
        Food(name="Булочка", satiety=8, price=12),
        Food(name="Пирожок", satiety=15, price=25),
    ]
    all_medicine = [
        Medicine(name="Антибиотик", price=30, heal_hp=20, number_of_uses=2),
        Medicine(name="Витамин C", price=25, heal_hp=10, number_of_uses=3),
        Medicine(name="Болитголовой", price=60, heal_hp=40, number_of_uses=1),
    ]

    tamagochi = SimpleTamagochi(name="Котик")
    clicker = SimpleRandomClicker(min_income=5, max_income=20)
    game = SimpleGame(
        tamagochi=tamagochi,
        clicker=clicker,
        all_food=all_food,
        all_medicine=all_medicine,
    )

    print("Добро пожаловать в игру Тамагочи-кликер!")
    output = ""
    STATUS_TEMPLATE = (
        "\nГолод: {hunger}, Здоровье: {hp}, Энергия: {energy}, Монеты: {coins}\n"
    )

    while True:
        os.system("clear" if os.name != "nt" else "cls")
        print(output)
        output = ""

        print(f"Еда в инвентаре: {[f.name for f in game.food]}")
        print(f"Лекарства в инвентаре: {[m.name for m in game.medicine]}")

        status = game.get_status()
        print(STATUS_TEMPLATE.format(**status))

        if tamagochi.is_sick():
            print("======= Питомец болен! =======")
            print("======= Срочно дайте лекарство! =======")

        menu_lines = [
            "1. Поработать (заработать монеты)",
            "2. Купить еду",
            "3. Купить лекарство",
            "4. Покормить питомца",
            "5. Полечить питомца",
            "6. Поиграть с питомцем",
            "7. Дать питомцу отдохнуть",
            "0. Выйти из игры",
        ]
        print("\n".join(menu_lines))

        choice = input("Ваш выбор: ").strip()

        try:
            match choice:
                case "1":
                    income = game.work()
                    output = f"Вы заработали {income} монет."
                case "2":
                    idx = int(input("Выберите номер еды из списка (начиная с 0): ") or 0)
                    game.buy_food(idx)
                    output = "Еда куплена."
                case "3":
                    idx = int(input("Выберите номер лекарства из списка (начиная с 0): ") or 0)
                    game.buy_medicine(idx)
                    output = "Лекарство куплено."
                case "4":
                    idx = int(input("Выберите индекс еды из инвентаря (начиная с 0): ") or 0)
                    game.feed_tamagochi(idx)
                    output = "Питомец накормлен."
                case "5":
                    idx = int(input("Выберите индекс лекарства из инвентаря (начиная с 0): ") or 0)
                    game.heal_tamagochi(idx)
                    output = "Питомец вылечен."
                case "6":
                    game.play_with_tamagochi()
                    output = "Вы поиграли с питомцем."
                case "7":
                    game.rest_tamagochi()
                    output = "Питомец отдохнул."
                case "0":
                    print("Выход из игры!")
                    return
                case _:
                    output = "Некорректный выбор меню."
        except (InvalidActionError, NotEnoughMoney) as e:
            output = str(e)
        except (GameOverError, TamagochiIsGone):
            print("\nИгра окончена: ваш питомец погиб.")
            break

if __name__ == "__main__":
    main()