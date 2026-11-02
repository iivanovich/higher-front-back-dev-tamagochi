"""Константы игры «Тамагочи».

Здесь собраны все «магические числа» и текстовые значения игры, чтобы
баланс правился в одном месте, а не по всему коду.
"""

# --- Границы показателей питомца -------------------------------------------
MIN_STAT = 0
MAX_STAT = 100

# --- Начальное состояние питомца -------------------------------------------
DEFAULT_NAME = 'Кот'
INITIAL_HUNGER = 30
INITIAL_FATIGUE = 10
INITIAL_HP = 100
INITIAL_ENERGY = 80

# --- Кормление --------------------------------------------------------------
FEED_ENERGY_COST = 3
FEED_FATIGUE_GAIN = 2

# --- Игра -------------------------------------------------------------------
PLAY_ENERGY_COST = 12
PLAY_FATIGUE_GAIN = 10
PLAY_HUNGER_GAIN = 8
PLAY_HP_GAIN = 2

# --- Отдых ------------------------------------------------------------------
REST_ENERGY_RECOVERY = 40
REST_ENERGY_RECOVERY_SICK = 20
REST_FATIGUE_RECOVERY = 40
REST_HUNGER_GAIN = 6

# --- Лечение ----------------------------------------------------------------
HEAL_FATIGUE_RECOVERY = 10

# --- Тик (update) -----------------------------------------------------------
HUNGER_GROWTH_MIN = 2
HUNGER_GROWTH_MAX = 5
FATIGUE_GROWTH_MIN = 1
FATIGUE_GROWTH_MAX = 3
ENERGY_DRAIN = 1
ENERGY_DRAIN_TIRED = 3
TIRED_FATIGUE_THRESHOLD = 70

SICK_HP_LOSS = 5
SICK_ENERGY_DRAIN_EXTRA = 2
SICK_FATIGUE_GAIN = 2

HUNGER_CRITICAL_THRESHOLD = 85
HUNGER_HP_LOSS = 3
ENERGY_HP_LOSS = 2

# --- Шансы заболеть ---------------------------------------------------------
SICK_CHANCE_DEFAULT = 0.10
SICK_CHANCE_VULNERABLE = 0.35
SICK_VULNERABLE_HUNGER = 70
SICK_VULNERABLE_ENERGY = 30
SICK_VULNERABLE_FATIGUE = 70

# --- Кликер -----------------------------------------------------------------
DEFAULT_MIN_INCOME = 10
DEFAULT_MAX_INCOME = 20
DEFAULT_FIXED_INCOME = 10
CLICK_BONUS_EVERY = 10
CLICK_BONUS_MULTIPLIER = 3

# --- Игра -------------------------------------------------------------------
GAME_OVER_MESSAGE = 'Игра окончена: питомец погиб'
DEAD_TAMAGOCHI_MESSAGE = 'Питомец погиб. Игра окончена.'
WELCOME_MESSAGE = 'Добро пожаловать в тамагочи-кликер!'
SICK_WARNING = (
    '=======Тамагочи болеет=======\n'
    '=======Отдых действует менее эффективно======='
)
WRONG_COMMAND_MESSAGE = 'Неверная команда'

# --- Магазин по умолчанию ---------------------------------------------------
# Кортежи (name, satiety, price) — из них собираются объекты Food.
DEFAULT_FOOD: tuple[tuple[str, int, int], ...] = (
    ('Бургер', 20, 40),
    ('Салат', 10, 20),
    ('Яблоко', 10, 15),
)

# Кортежи (name, price, heal_hp, number_of_uses) — для объектов Medicine.
DEFAULT_MEDICINE: tuple[tuple[str, int, int, int], ...] = (
    ('Ибупрофен', 30, 20, 2),
)

# Меню игры: код действия -> подпись в консоли.
MENU: dict[str, str] = {
    '1': 'Пойти на работу',
    '2': 'Купить еду',
    '3': 'Купить лекарство',
    '4': 'Покормить',
    '5': 'Вылечить',
    '6': 'Играть',
    '7': 'Отдых',
    '0': 'Выход',
}
