# Імпорт бібліотек
import GeneticAlgorithm
import GreedyAlgorithm as Greedy
import ExperimentsGreedy
import ExperimentsGenetic
import Equipment
import Equipment
# Функція запуску генетичного алгоритму
# config приймає в себе словник, який містить інформацію про предмети
# value_count приймає в себе кількість цінностей для 1-го предмету
def run_genetic(config, value_count):
    items = config["items"]
    V = config["V"]
    W = config["W"]
    population_size = config["population_size"]
    generations = config["generations"]
    mutation_rate = config["mutation_rate"]

    result = GeneticAlgorithm.run_genetic_algorithm1(
        items, V, W, population_size, generations, mutation_rate, value_count
    )
    return result
# Запускає жадібний алгоритм
# config приймає в себе словник, який містить інформацію про предмети
# value_count приймає в себе кількість цінностей для 1-го предмету
def run_greedy(config, value_count):
    items = config["items"]
    V = config["V"]
    W = config["W"]
    population_size = config["population_size"]

    Greedy.run_greedy_algorithm(items, V, W, population_size)
# Викликаємо два алгоритми
def run_both(config, value_count):
    run_genetic(config, value_count)
    Greedy.run_greedy_algorithm(config["items"], config["V"], config["W"], value_count)
# Запускаємо run_experimentsGreedy
def run_experimentsGreedy(experiment_config_file_path):
    ExperimentsGreedy.main(experiment_config_file_path)
# Запускаємо run_experimentsGenetic
def run_experimentsGenetic(experiment_config_file_path):
    ExperimentsGenetic.main(experiment_config_file_path)
def run_equipment(config, value_count):
    genet = run_genetic(config, value_count)
    greedy = Greedy.run_greedy_algorithm(config["items"], config["V"], config["W"], value_count)
    Equipment.process_equipment(genet,greedy)



