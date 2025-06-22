import tkinter as tk

def process_equipment(genet, greedy):
    # Функція сортування предметів
    def distribute_items_by_weight(items):
        # Відсортувати предмети за вагою (індекс 2) Сортуємо
        # від більшого до меньшого reverse=True
        sorted_items = sorted(items, key=lambda x: x[2], reverse=True)
        # Визначили порядок секторів
        sectors_order = [
            "left_top", "bottom_right", "top_right", "bottom_left",
            "top", "bottom", "left", "right", "center"
        ]
        # Зворотній порядок секторів
        backward_order = list(reversed(sectors_order))
        # Зробили словник ЗБЕРІГАННЯ ПРЕДМЕТІВ ПО СЕКТОРАМ
        sectors = {pos: [] for pos in sectors_order}
        # Розбили предмети на групи по 9 елементів (layer-буде групою)
        # Оскільки список вже відсортований, то можна вантажити
        # З 20 елементів буде 2 списки по 9 елементів і 1 по 2
        parts = [sorted_items[i:i + 9] for i in range(0, len(sorted_items), 9)]
        # Проводимо цикл Для кожного шару i та містом layer
        # Якщо індекс групи парний то order_forward, якщо не парний то...
        # через enumerate задали кожному елементу parts індекс
        for i, layer in enumerate(parts):
            order = sectors_order if i % 2 == 0 else backward_order
            # Для кожного предмета у групі item в залежності від позиції j
            # визначаємо назву сектора sector_name
            # Додали предмет до словника предметів сектора
            for j, item in enumerate(layer):
                sector_name = order[j]
                sectors[sector_name].append(item)
            # Повернуи словник з секторами
        return sectors

    # Графічний інтерфейс
    def gui(sectors):
        #  Графічний інтерфейс
        scroll_window = tk.Toplevel()
        scroll_window.title("Графічне розміщення предметів")
        scroll_window.geometry("600x700")
        canvas = tk.Canvas(scroll_window)
        scrollbar = tk.Scrollbar(scroll_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        sector_names = {
            "left_top": "Лівий верхній кут",
            "bottom_right": "Правий нижній кут",
            "top_right": "Правий верхній кут",
            "bottom_left": "Нижній лівий кут",
            "top": "Верх центр",
            "bottom": "Низ центр",
            "left": "Ліво центр",
            "right": "Право центр",
            "center": "Центр"
        }

        # Центруючий контейнер
        center_wrapper = tk.Frame(scrollable_frame)
        center_wrapper.pack(pady=10, anchor="center")

        grid_frame = tk.Frame(center_wrapper)
        grid_frame.pack(anchor="center")

        position_to_grid = {
            "left_top": (0, 0), "top": (0, 1), "top_right": (0, 2),
            "left": (1, 0), "center": (1, 1), "right": (1, 2),
            "bottom_left": (2, 0), "bottom": (2, 1), "bottom_right": (2, 2)
        }

        for pos, (row, col) in position_to_grid.items():
            sector_items = sectors.get(pos, [])
            if sector_items:
                sector_text = f"{sector_names[pos]}\n" + "\n".join(
                    f"{item[0]} (вага {item[2]})" for item in sector_items)
                bg_color = "#9a9a9a"
            else:
                sector_text = f"{sector_names[pos]}\n\nВільне місце"
                bg_color = "#f0f0f0"

            frame = tk.Frame(grid_frame, bd=1, relief="solid", padx=5, pady=5,
                             width=180, height=100, bg=bg_color)
            frame.grid(row=row, column=col, padx=5, pady=5)
            frame.grid_propagate(False)

            tk.Label(frame, text=sector_text, justify="center", wraplength=160,
                     anchor="center", height=6, width=22).pack(fill="both", expand=True)

        # Вивід консоль
        print("\nРозподіл предметів по секторах:")
        for sector, items_in_sector in sectors.items():
            print(f"\nСектор '{sector_names[sector]}':")
            if not items_in_sector:
                print("  (порожній)")
            for item in items_in_sector:
                print(f"  {item}")


    # Вибір списку Жадібний/Генетичний
    print("\nОтримані предмети з генетичного алгоритму")
    for item in genet:
        print("Обробляємо:", item)
        # Визначили цінність всіх предметів списку
    total_value_genet = sum(item[3] for item in genet)

    print("\nОтримані предмети з жадібного алгоритму")
    for item in greedy:
        print("Обробляємо:", item)
        # Визначили цінність всіх предметів списку
    total_value_greedy = sum(item[3] for item in greedy)

    print(f"\nСума цінностей (Генетичний алгоритм): {total_value_genet}")
    print(f"Сума цінностей (Жадібний алгоритм): {total_value_greedy}")
    # Які список більше, ті предмети і беруться
    if total_value_genet > total_value_greedy:
        print("\nОбрано результати генетичного алгоритму")
        sectors = distribute_items_by_weight(genet)
        gui(sectors)

    else:
        print("\nОбрано результати жадібного алгоритму")
        sectors = distribute_items_by_weight(greedy)
        gui(sectors)

