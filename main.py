import os

from game.clicker import SimpleRandomClicker
from game.exceptions import GameOverError, InvalidActionError, NotEnoughMoneyError
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
        # Очищаем консоль перед каждым кадром
        os.system("clear" if os.name != "nt" else "cls")

        print(output)
        output = ""  # сбрасываем сообщение после вывода

        print(f"Сумка с едой: {[f.name for f in game.food]}")
        print(f"Сумка с лекарствами: {[m.name for m in game.medicine]}")

        try:
            status = game.get_status()
        except GameOverError:
            print("\n💀 Игра окончена: ваш питомец умер.")
            break

        print(
            f"\nСтатус: голод {status['hunger']}, здоровье {status['hp']}, "
            f"энергия {status['energy']}, монет {status['coins']}\n"
        )

        if game.tamagochi.is_sick():
            print("======= Тамагочи болеет! =======")
            print("======= Отдых действует менее эффективно. =======")

        print("1. Пойти на работу (кликер)")
        print("2. Купить еду")
        print("3. Купить лекарство")
        print("4. Покормить питомца")
        print("5. Вылечить питомца")
        print("6. Поиграть с питомцем")
        print("7. Отдых")
        print("0. Выход")

        choice = input("Выберите действие: ").strip()

        try:
            match choice:
                case "1":
                    income = game.work()
                    output = f"Вы заработали {income} монет."
                    game.tamagochi.update()
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
        except NotEnoughMoneyError:
            output = "❌ Недостаточно монет для покупки."
        except InvalidActionError as e:
            output = f"❌ Невозможно выполнить действие: {e}"
        except GameOverError:
            print("\n💀 Игра окончена: ваш питомец умер.")
            break


if __name__ == "__main__":
    main()
