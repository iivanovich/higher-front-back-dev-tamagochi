# main.py
import os

from game.clicker import SimpleRandomClicker
from game.exceptions import (
    GameOverError,
    InvalidActionError,
    NotEnoughMoneyError,
)
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
                    if not all_food:
                        print("Нет доступной еды для покупки.")
                        continue
                    print("Доступная еда:")
                    for i, f in enumerate(all_food):
                        print(f"{i}. {f.name} (сытость {f.satiety}, цена {f.price})")
                    idx = int(input("Какую еду купить? Введите индекс: ").strip())
                    game.buy_food(idx)
                    output = "Еда куплена."
                case "3":
                    if not all_medicine:
                        print("Нет доступных лекарств для покупки.")
                        continue
                    print("Доступные лекарства:")
                    for i, m in enumerate(all_medicine):
                        print(f"{i}. {m.name} (лечение {m.heal_hp}, цена {m.price})")
                    idx = int(input("Какое лекарство купить? Введите индекс: ").strip())
                    game.buy_medicine(idx)
                    output = "Лекарство куплено."
                case "4":
                    if not game.food:
                        print("Нет еды в инвентаре.")
                        continue
                    print("Еда в инвентаре:")
                    for i, f in enumerate(game.food):
                        print(f"{i}. {f.name} (сытость {f.satiety})")
                    idx = int(input("Чем покормить питомца? Введите индекс: ").strip())
                    game.feed_tamagochi(idx)
                    output = "Питомец покормлен."
                case "5":
                    if not game.medicine:
                        print("Нет лекарств в инвентаре.")
                        continue
                    print("Лекарства в инвентаре:")
                    for i, m in enumerate(game.medicine):
                        print(f"{i}. {m.name} (осталось использований {m.number_of_uses - m.uses})")
                    idx = int(input("Каким лекарством лечить? Введите индекс: ").strip())
                    game.heal_tamagochi(idx)
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
        except (InvalidActionError, NotEnoughMoneyError) as e:
            output = str(e)
        except GameOverError:
            print("\n😿 Игра окончена: ваш питомец умер.")
            break


if __name__ == "__main__":
    main()
