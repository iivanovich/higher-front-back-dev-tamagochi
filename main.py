# main.py
import os

from game.clicker import SimpleRandomClicker
from game.exceptions import GameOverError, InvalidActionError, NotEnoughMoney
from game.game import SimpleGame
from game.models import Food, Medicine
from game.tamagochi import SimpleTamagochi


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

    print("Добро пожаловать в тамагочи-кликер!")
    output = ""

    while True:
        os.system("clear" if os.name != "nt" else "cls")
        print(output)
        output = ""

        print(f"Сумка с едой: {[f.name for f in game.food]}")
        print(f"Сумка с лекарствами: {[m.name for m in game.medicine]}")

        try:
            status = game.get_status()
        except GameOverError:
            print("\n😿 Игра окончена: ваш питомец умер.")
            break

        print(
            f"\nСтатус: голод {status['hunger']}, здоровье {status['hp']}, "
            f"энергия {status['energy']}, монеты {status['coins']}\n"
        )

        if tamagochi.is_sick():
            print("======= Тамагочи болеет! =======")
            print("======= Отдых действует менее эффективно. =======")

        menu_lines = [
            "1. Пойти на работу (кликер)",
            "2. Купить еду",
            "3. Купить лекарство",
            "4. Покормить питомца",
            "5. Вылечить питомца",
            "6. Поиграть с питомцем",
            "7. Отдохнуть",
            "0. Выход",
        ]
        print("\n".join(menu_lines))

        choice = input("Выберите действие: ").strip()

        try:
            match choice:
                case "1":
                    income = game.work()
                    output = f"Вы заработали {income} монет."
                    tamagochi.update()
                case "2":
                    game.buy_food()
                    output = "Еда куплена."
                case "3":
                    game.buy_medicine()
                    output = "Лекарство куплено."
                case "4":
                    game.feed_tamagochi()
                    output = "Питомец покормлен."
                case "5":
                    game.heal_tamagochi()
                    output = "Питомец вылечен."
                case "6":
                    game.play_with_tamagochi()
                    output = "Вы поиграли с питомцем."
                case "7":
                    game.rest_tamagochi()
                    output = "Питомец отдохнул."
                case "0":
                    print("До свидания!")
                    return
                case _:
                    output = "Неверный выбор, попробуйте снова."
        except ValueError:
            output = "Пожалуйста, введите корректный номер."
        except (InvalidActionError, NotEnoughMoney) as e:
            output = str(e)
        except GameOverError:
            print("\n😿 Игра окончена: ваш питомец умер.")
            break


if __name__ == "__main__":
    main()
