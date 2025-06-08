import pandas as pd
import GeneticAlgorithm as Genetic10andMorePart2WithLogicSorting
import GreedyAlgorithm as Greedy
import ExperimentsGreedy
import ExperimentsGenetic

def set_defaults_if_missing(config):
    if 'population_size' not in config or config['population_size'] in [None, '', ' ']:
        print("Параметр 'population_size' не задано або порожній. Встановлено значення за замовчуванням: 1000")
        config['population_size'] = 1000
    if 'generations' not in config or config['generations'] in [None, '', ' ']:
        print("Параметр 'generations' не задано або порожній. Встановлено значення за замовчуванням: 100")
        config['generations'] = 100
    if 'mutation_rate' not in config or config['mutation_rate'] in [None, '', ' ']:
        print("Параметр 'mutation_rate' не задано або порожній. Встановлено значення за замовчуванням: 0.01")
        config['mutation_rate'] = 0.01

def load_config_txt(filename, value_count):
    config = {}
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        items = []
        for line in lines:
            if line.startswith("items:"):
                continue
            elif line.startswith("V:"):
                config['V'] = int(line.split(":")[1].strip())
            elif line.startswith("W:"):
                config['W'] = int(line.split(":")[1].strip())
            elif line.startswith("population_size:"):
                value = line.split(":")[1].strip()
                if value != '':
                    config['population_size'] = int(value)
            elif line.startswith("generations:"):
                value = line.split(":")[1].strip()
                if value != '':
                    config['generations'] = int(value)
            elif line.startswith("mutation_rate:"):
                value = line.split(":")[1].strip()
                if value != '':
                    config['mutation_rate'] = float(value)
            else:
                item = line.strip().split(',')
                name = item[0]
                volume = int(item[1])
                values = [int(v) for v in item[2:2 + value_count]]
                weight = int(item[2 + value_count])
                items.append([name, volume] + values + [weight])
        config['items'] = items
    set_defaults_if_missing(config)


    print("\nКонфігурація зчитана з файлу:")
    print(f"Об'єм вантажного відділення: {config['V']}")
    print(f"Допустима вага: {config['W']}")
    print(f"Розмір популяції: {config['population_size']}")
    print(f"Кількість поколінь: {config['generations']}")
    print(f"Шанс мутації: {config['mutation_rate']}\n")
    print("Список товарів:")
    print(f"{'Назва':<15}{'Обʼєм':<8}{'Вага':<6}{'Значення цінності кожної копії предмету (Цінність)':<55}")
    print("-" * 100)
    for item in config['items']:
        name = item[0]
        volume = item[1]
        values = item[2:-1]
        weight = item[-1]
        values_str = ', '.join(map(str, values))
        print(f"{name:<15}{volume:<8}{weight:<6}{values_str:<55}")
    print()

    return config

def load_config_xlsx(filename, value_count):
    excel_data = pd.ExcelFile(filename)
    items_df = excel_data.parse(excel_data.sheet_names[0])
    items = []

    for _, row in items_df.iterrows():
        name = row['Назва']
        volume = int(row['Обʼєм'])
        weight = int(row['Вага'])
        values = [int(row[f'Цінність{i}']) for i in range(1, value_count + 1)]

        items.append([name, volume] + values + [weight])

    params_df = excel_data.parse(excel_data.sheet_names[1])
    config = {}
    for _, row in params_df.iterrows():
        param = row['Параметр']
        value = row['Значення']
        if pd.isna(value) or str(value).strip() == '':
            continue
        if param == "допустимий об'єм предметів":
            config['V'] = int(value)
        elif param == 'допустима вага':
            config['W'] = int(value)
        elif param == 'population_size':
            config['population_size'] = int(value)
        elif param == 'generations':
            config['generations'] = int(value)
        elif param == 'mutation_rate':
            config['mutation_rate'] = float(value)

    config['items'] = items
    set_defaults_if_missing(config)

    print("\nКонфігурація зчитана з файлу:")
    print(f"Об'єм вантажного відділення: {config['V']}")
    print(f"Допустима вага: {config['W']}")
    print(f"Розмір популяції: {config['population_size']}")
    print(f"Кількість поколінь: {config['generations']}")
    print(f"Шанс мутації: {config['mutation_rate']}\n")


    print("Список товарів:")
    print(f"{'Назва':<15}{'Обʼєм':<8}{'Вага':<6}{'Значення цінності кожної копії предмету (Цінність)':<55}")
    print("-" * 100)
    for item in config['items']:
        name = item[0]
        volume = item[1]
        values = item[2:-1]
        weight = item[-1]
        values_str = ', '.join(map(str, values))
        print(f"{name:<15}{volume:<8}{weight:<6}{values_str:<55}")

    return config

def main():
    try:
        value_count = int(input("\nСкільки цінностей бажаєте враховувати для кожного предмета?"
        "\n(Для запобігання перевантаженню системи, значення обмежені від 1 до 10)"
        "\nВведить значення: ").strip())
        if value_count < 1 or value_count > 10 :
            raise ValueError
    except ValueError:
        print("Неправильне значення. Використано значення за замовчуванням: 2.")
        value_count = 2

    print("Яку функцію бажаєте використати?")
    choice = input("(1. Генетік / 2. Жадібний / 3. Генетичний + Жадібний): ").strip().lower()
    if choice == '1':
        choiceGenetic = input("(1. Проаналізувати TXT / 2. XLSX / 3. Провести експерименти): ").strip().lower()
        if choiceGenetic == '1':
            config = load_config_txt('test/config.txt', value_count)
        elif choiceGenetic == '2':
            config = load_config_xlsx('test/configX100S100.xlsx', value_count)
        elif choiceGenetic == '3':
            ExperimentsGenetic.main()
            return
        else:
            print("Невірний вибір.")
            return
        items = config["items"]
        V = config["V"]
        W = config["W"]
        population_size = config["population_size"]
        generations = config["generations"]
        mutation_rate = config["mutation_rate"]

        with open("genetic_algorithm_results.txt", "w") as file:
            file.write("------------------------------------------------------------------------------------------\n")
            file.write(f"Задані значення:\n")
            file.write(f"Об'єм трюму: {V}\n")
            file.write(f"Список товарів: {items}\n")
            file.write(f"Розмір популяції: {population_size}\n")
            file.write(f"Кількість поколінь: {generations}\n")
            file.write(f"Шанс мутації: {mutation_rate}\n\n")

        Genetic10andMorePart2WithLogicSorting.run_genetic_algorithm1(items, V, W, population_size, generations, mutation_rate, value_count)
    elif choice == '2':
        choiceGreedy = input("(1. Проаналізувати TXT / 2. XLSX / 3. Провести експерименти): ").strip().lower()
        if choiceGreedy == '1':
            config = load_config_txt('config.txt', value_count)
        elif choiceGreedy == '2':
            config = load_config_xlsx('test/configX100S100.xlsx', value_count)
        elif choiceGreedy == '3':
            ExperimentsGreedy.main()
            return
        else:
            print("Невірний вибір.")
            return
        items = config["items"]
        V = config["V"]
        W = config["W"]
        population_size = config["population_size"]
        generations = config["generations"]
        mutation_rate = config["mutation_rate"]

        with open("greedy_algorithm_results.txt", "w") as file:
            file.write("------------------------------------------------------------------------------------------\n")
            file.write(f"Задані значення:\n")
            file.write(f"Об'єм трюму: {V}\n")
            file.write(f"Список товарів: {items}\n")
            file.write(f"Розмір популяції: {population_size}\n")
            file.write(f"Кількість поколінь: {generations}\n")
            file.write(f"Шанс мутації: {mutation_rate}\n\n")
        Greedy.run_greedy_algorithm(items, V, W, population_size)
    elif choice == '3':
        choiceGeneticGreedy = input("(1. Проаналізувати TXT / 2. XLSX / 3. Провести експерименти): ").strip().lower()
        if choiceGeneticGreedy == '1':
            config = load_config_txt('test/config.txt', value_count)
        elif choiceGeneticGreedy == '2':
            config = load_config_xlsx('test/configX100TooGreedy.xlsx', value_count)
        elif choiceGeneticGreedy == '3':
            ExperimentsGenetic.main()
            ExperimentsGreedy.main()
            return
        else:
            print("Невірний вибір.")
            return
        items = config["items"]
        V = config["V"]
        W = config["W"]
        population_size = config["population_size"]
        generations = config["generations"]
        mutation_rate = config["mutation_rate"]
        Genetic10andMorePart2WithLogicSorting.run_genetic_algorithm1(items, V, W, population_size, generations,mutation_rate, value_count)
        Greedy.run_greedy_algorithm(items, V, W, value_count)

if __name__ == "__main__":
    main()
