# Імпорт бібліотек
import random
import GeneticAlgorithm
# Зчитуємо параметри з .txt файлу
def read_config(filename):
    # Створили порожній словник для конфігурацій параметрів
    config = {}
    # Зчитали всі рядки з файлу
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
    # Визначили параметри у файлі та відповідні внутрішні змінні для коду пайтон
    expected_keys = {
        "Кількість експериментів": "experiments_count",
        "Кількість речей": "items_count",
        "Кількість цінностей для кожної речі": "max_same_items",
        "Діапазон генерації цінності": "value_range",
        "Діапазон генерації об'єму для кожної речі": "volume_range",
        "Діапазон генерації ваги для кожної речі": "weight_range",
        "Допустимий загальний об'єм речей": "volume_limit",
        "Допустимий загальна вага речей": "weight_limit",
        "Розмір популяції": "population_size",
        "Кількість поколінь": "generations",
        "Ймовірність мутації": "mutation_rate"
    }
    # Створили словник, у якому поділали рядки на ключі та їх значення,
    # за допомогою використання :
    parsed_data = {}
    # Пройшлись циклом по рядках
    for line in lines:
        # Спроба обробити рядок
        try:
            # Розбили рядок на дві частини №1Ключи,
            # №2 Значення по першому символу двокрапки (:)
            key, value = line.split(":", 1)
            # key.strip() - прибрали пробіли з обох кінців
            key = key.strip()
            # Тут з такого значення "Кількість елементів:10" вже отримали таке "10"
            value = value.strip()
            # Через словник expected_keys перевірили чи є ключ
            # Якщо ключ є то отримали його ім'я в системі
            if key in expected_keys:
                internal_key = expected_keys[key]
                # Якщо у нас параметр - це діапазон значень
                # від 10 до 50 наприклад, то розбиваємо на два значення
                # перше значення це мінімум, друге максимум.
                if internal_key.endswith("_range"):
                    parts = list(map(int, value.split()))
                    # Якщо обидва значення наявні, то зберігаємо
                    # у parsed_data з значеннями мінімуму та максимуму
                    if len(parts) == 2:
                        parsed_data[internal_key + "_min"] = parts[0]
                        parsed_data[internal_key + "_max"] = parts[1]
                    else:
                        raise ValueError(f"Діапазон для '{key}' повинен містити два числа.")
                # Отримали тим даних флоат для шансу мутації
                elif internal_key == "mutation_rate":
                    parsed_data[internal_key] = float(value)
                # всі інші значення - це цілі числа що будуть збережені в словник parsed_data
                else:
                    parsed_data[internal_key] = int(value)
            else:
                print(f"Попередження: Невідомий ключ конфігурації '{key}' у файлі.")
        except ValueError as e:
            raise ValueError(f"Помилка розбору рядка: '{line}'. Деталі: {e}")
    # Створює список, з назвами параметрів, які будуть в
    # словнику parsed_data після зчитування файлу
    required_keys = [
        "experiments_count", "items_count", "max_same_items",
        "value_range_min", "value_range_max",
        "volume_range_min", "volume_range_max",
        "weight_range_min", "weight_range_max",
        "volume_limit", "weight_limit",
        "population_size", "generations", "mutation_rate"
    ]
    # Перевіряє кожен параметр у parsed_data, якщо хоча б 1 відсутній
    # Видається помилка і зупиняється програма
    for key in required_keys:
        if key not in parsed_data:
            raise KeyError(f"Відсутній параметр: {key}")
    # Повератє значення у формі кортежу з конкретним порядком
    # Дані значення потім передаються у змінні
    # у фунцію main(config_file)
    return (
        parsed_data["experiments_count"],
        parsed_data["items_count"],
        parsed_data["max_same_items"],
        parsed_data["value_range_min"],
        parsed_data["value_range_max"],
        parsed_data["volume_range_min"],
        parsed_data["volume_range_max"],
        parsed_data["weight_range_min"],
        parsed_data["weight_range_max"],
        parsed_data["volume_limit"],
        parsed_data["weight_limit"],
        parsed_data["population_size"],
        parsed_data["generations"],
        parsed_data["mutation_rate"]
    )
# Генерує список випадкових товарів,
# які мають в собі наступні параметри
def generate_items(items_count, max_same_items, value_min, value_max, volume_min, volume_max, weight_min, weight_max):
    # Створили порожній список
    items = []
    # генеруємо items_count товарів
    for i in range(items_count):
        # Задали назву товару
        name = f"Item{i+1}"
        # генерація об'єму та ваги на заданих проміжках
        volume = random.randint(volume_min, volume_max)
        weight = random.randint(weight_min, weight_max)
        # Випадковий список цінностей
        values = [random.randint(value_min, value_max) for _ in range(max_same_items)]
        # Формуємо списко, що представлятиме собою один товар
        item = [name, volume, *values, weight]
        # Додаємо товари у список
        items.append(item)
    return items
# Вимодимо товари у табличному вигляді
def print_items(items):
    print("Список згенерованих товарів:")
    print(f"{'Назва':<15}{'Обʼєм':<8}{'Вага':<8}{'Цінності':<40}")
    print("-" * 70)
    for item in items:
        name = item[0]
        volume = item[1]
        values = item[2:-1] # Цінності знаходяться між об'ємом та вагою
        weight = item[-1]
        print(f"{name:<15}{volume:<8}{weight:<8}{', '.join(map(str, values)):<40}")

def main(config_file):
    # Викликаємо read_config та отримуємо зчитані з файлу параметри
    try:
        (
            exp_count,
            items_gen_count,
            max_same,
            val_min,
            val_max,
            vol_min,
            vol_max,
            w_min,
            w_max,
            vol_limit,
            w_limit,
            pop_size,
            gens,
            mut_rate
        ) = read_config(config_file)
        # Якщо не вийшло, видали помилку
    except Exception as e:
        print(f"Помилка конфігурації: {e}")
        return
    # Виводимо результати в консоль
    print(f"Конфігурація завантажена з '{config_file}':")
    print(f"  Кількість експериментів: {exp_count}")
    print(f"  Кількість речей для генерації: {items_gen_count}")
    print(f"  Кількість цінностей для кожної речі: {max_same}")
    print(f"  Діапазон цінності: [{val_min}, {val_max}]")
    print(f"  Діапазон об'єму: [{vol_min}, {vol_max}]")
    print(f"  Діапазон ваги: [{w_min}, {w_max}]")
    print(f"  Ліміт об'єму: {vol_limit}")
    print(f"  Ліміт ваги: {w_limit}")
    print(f"  Розмір популяції: {pop_size}")
    print(f"  Кількість поколінь: {gens}")
    print(f"  Ймовірність мутації: {mut_rate}")
    # Задали цикл для повторювання експериментів
    # Виконує задану кількість експериментів
    for i in range(exp_count):
        print(f"\n--- Експеримент {i + 1} з {exp_count} ---")
        # Генеруємо товари
        current_items = generate_items(
            items_gen_count, max_same,
            val_min, val_max,
            vol_min, vol_max,
            w_min, w_max
        )
        # Вимодимо згенеровані товари
        # для кожного експрименту
        print_items(current_items)
        # Передаймо товари й параметри
        # у функцію генетичного алгоритму
        # Пвоертаємо результати у result
        # result приймає той тип значення, яке в нього повертають
        result = GeneticAlgorithm.run_genetic_algorithm1(
            current_items,
            vol_limit,
            w_limit,
            pop_size,
            gens,
            mut_rate,
            max_same
        )
        print(f"\nРезультат генетичного алгоритму:\n{result}")

if __name__ == "__main__":
    default_config = "config_genetic.txt"
    print(f"Використовується конфігураційний файл: {default_config}")
    main(default_config)
