import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from Interface import run_genetic, run_greedy, run_both, run_experimentsGreedy, run_experimentsGenetic, run_equipment
from StartandReading import load_config_txt, load_config_xlsx
import re
import pandas as pd
import threading
from contextlib import redirect_stdout, redirect_stderr
import queue


# Клас для перенаправлення виводу print() вивід потрапляє не у консоль,
# а йде у графічний інтерфейс

class QueueIO:
    def __init__(self, log_queue):
        self.log_queue = log_queue
        self.buffer = ""

    def write(self, text):
        self.buffer += text
        # Відправляємо в чергу тільки цілі рядки
        if '\n' in self.buffer:
            lines = self.buffer.split('\n')
            for i in range(len(lines) - 1):
                self.log_queue.put(lines[i] + '\n')
            self.buffer = lines[-1]  # Залишок зберігаємо в буфері

    def flush(self):
        # Примусово скидаємо залишки буфера, якщо є
        if self.buffer:
            self.log_queue.put(self.buffer)
            self.buffer = ""
        pass

# Даний клас являє собою вікно графічного інтерфейсу
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Інтерфейс запуску алгоритмів")
        self.root.geometry("600x550")
        self.value_count = tk.IntVar(value=2)
        self.algorithm_choice = tk.StringVar()
        self.config_choice = tk.StringVar()
        self.log_queue = queue.Queue()
        self._current_file_path = None  # Для зберігання шляху до файлу конфігурації TXT/XLSX
        self._experiment_config_file_path = None # Для зберігання шляху до файлу конфігурації експериментів

        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Кількість значень цінностей одного предмета (Цінність), діапазон значень від 1 до 10.").pack(anchor=tk.W)
        ttk.Spinbox(main_frame, from_=1, to=10, textvariable=self.value_count, width=5).pack(anchor=tk.W)

        ttk.Label(main_frame, text="Оберіть алгоритм:").pack(anchor=tk.W, pady=(10, 0))
        ttk.Combobox(main_frame, textvariable=self.algorithm_choice, values=[
            "","Генетичний", "Жадібний", "Генетичний + Жадібний", "Комплектація"
        ], state="readonly").pack(anchor=tk.W)

        ttk.Label(main_frame, text="Оберіть конфігурацію:").pack(anchor=tk.W, pady=(10, 0))
        ttk.Combobox(main_frame, textvariable=self.config_choice, values=[
            "Зчитування даних у форматі .txt", "Зчитування даних у форматі .xlsx", "Експерименти з жадібним алгоритмом", "Експерименти з генетичним алгоритмом"
        ], state="readonly",width=35).pack(anchor=tk.W)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        #  "XLSX"
        ttk.Button(button_frame, text="Запустити", command=self.run_selected_wrapper).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистити", command=self.clear_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Зберегти у форматі .txt", command=self.save_as_txt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Зберегти у форматі .xlsx", command=self.save_as_xlsx).pack(side=tk.LEFT, padx=5)

        self.output_text = ScrolledText(main_frame, height=20, state='disabled', wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=10)

        self.process_log_queue()

    def display_output(self, text):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                if message is None:
                    return
                self.display_output(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)

    def clear_output(self):
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')

    def save_as_txt(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Зберегти як TXT"
        )
        if not file_path:
            return
        try:
            content = self.output_text.get("1.0", tk.END).strip()
            lines = content.split('\n')
            filtered_lines = [line for line in lines if not (
                    "Прогрес генетичного алгоритму" in line or
                    "Прогрес жадібного алгоритму" in line
            )]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(filtered_lines))
            messagebox.showinfo("Успіх", "Файл .txt збережено.")
        except Exception as e:
            self.log_queue.put(f"Помилка збереження TXT: {e}\n")
            messagebox.showerror("Помилка", f"Не вдалося зберегти файл:\n{e}")

    def save_as_xlsx(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Зберегти як XLSX"
        )
        if not file_path:
            return
        try:
            content = self.output_text.get("1.0", tk.END).strip()
            lines = content.split('\n')
            filtered_lines = [line for line in lines if not (
                    "Прогрес генетичного алгоритму" in line or
                    "Прогрес жадібного алгоритму" in line or
                    line.strip() == ""
            )]
            data_for_df = []
            for line in filtered_lines:
                parts = [p.strip() for p in re.split(r'[\t,]{1}|\s{2,}', line) if p.strip()]
                data_for_df.append(parts)
            if not data_for_df:
                messagebox.showinfo("Інформація", "Немає даних для збереження.")
                return
            max_cols = max(len(row) for row in data_for_df) if data_for_df else 0
            df_data = [row + [''] * (max_cols - len(row)) for row in data_for_df]
            df = pd.DataFrame(df_data)
            df.to_excel(file_path, index=False, header=False)
            messagebox.showinfo("Успіх", "Файл .xlsx збережено.")
        except Exception as e:
            self.log_queue.put(f"Помилка збереження XLSX: {e}\n")
            messagebox.showerror("Помилка", f"Не вдалося зберегти файл:\n{e}")

    def run_selected_wrapper(self):
        value_count = self.value_count.get()
        algo = self.algorithm_choice.get()
        config_type = self.config_choice.get()

        self._current_file_path = None
        self._experiment_config_file_path = None # Ініціалізуємо шлях до файлу експериментів

        if not config_type:
            messagebox.showwarning("Увага", "Будь ласка, виберіть конфігурацію.")
            return

        if config_type not in ["Експерименти з жадібним алгоритмом",
                               "Експерименти з генетичним алгоритмом"] and not algo:
            messagebox.showwarning("Увага", "Будь ласка, виберіть алгоритм.")
            return

        if config_type in ["Зчитування даних у форматі .txt", "Зчитування даних у форматі .xlsx"]:
            file_dialog_title = "Оберіть TXT файл конфігурації" if config_type == "Зчитування даних у форматі .txt" else "Оберіть XLSX файл конфігурації"
            file_types = [("Text files", "*.txt")] if config_type == "Зчитування даних у форматі .txt" else [("Excel files", "*.xlsx")]
            file_path = filedialog.askopenfilename(title=file_dialog_title, filetypes=file_types)
            if not file_path:
                messagebox.showinfo("Інформація", "Запуск скасовано, файл не обрано.")
                return
            self._current_file_path = file_path
        elif config_type == "Експерименти з жадібним алгоритмом":
            # Діалог для вибору файлу конфігурації експериментів
            exp_file_path = filedialog.askopenfilename(
                title="Оберіть файл конфігурації для експериментів (.txt)",
                filetypes=[("Text files", "*.txt")] # Припускаємо, що файл конфігурації експериментів - це .txt
            )
            if not exp_file_path:
                messagebox.showinfo("Інформація", "Запуск експериментів скасовано, файл конфігурації не обрано.")
                return
            self._experiment_config_file_path = exp_file_path
        elif config_type == "Експерименти з генетичним алгоритмом":
            # Діалог для вибору файлу конфігурації експериментів
            exp_file_path = filedialog.askopenfilename(
                title="Оберіть файл конфігурації для експериментів (.txt)",
                filetypes=[("Text files", "*.txt")] # Припускаємо, що файл конфігурації експериментів - це .txt
            )
            if not exp_file_path:
                messagebox.showinfo("Інформація", "Запуск експериментів скасовано, файл конфігурації не обрано.")
                return
            self._experiment_config_file_path = exp_file_path

        self.clear_output()
        self.display_output(f"Запуск: {algo} з конфігурацією {config_type} (Цінностей: {value_count})\n")
        if self._current_file_path:
            self.display_output(f"Файл конфігурації: {self._current_file_path}\n")
        if self._experiment_config_file_path: # Показуємо шлях до файлу експериментів, якщо він є
            self.display_output(f"Файл конфігурації експериментів: {self._experiment_config_file_path}\n")
        self.display_output("--------------------------------------------------\n")

        thread = threading.Thread(target=self.run_algorithm_thread_target,
                                  args=(value_count, algo, config_type, self._current_file_path, self._experiment_config_file_path), # Передаємо новий шлях
                                  daemon=True)
        thread.start()

    def run_algorithm_thread_target(self, value_count, algo, config_type, current_file_path, experiment_config_file_path): # Додано experiment_config_file_path
        queue_io = QueueIO(self.log_queue)
        with redirect_stdout(queue_io), redirect_stderr(queue_io):
            try:
                print(f"Розпочато обробку алгоритмом: {algo}...\n")

                if config_type == "Експерименти з жадібним алгоритмом":
                    if not experiment_config_file_path:
                        print("Помилка: Шлях до файлу конфігурації експериментів не було надано.\n")
                        return # Завершуємо потік, якщо шлях не надано
                    # Передаємо шлях до файлу у run_experiments
                    run_experimentsGreedy(experiment_config_file_path)
                elif config_type == "Експерименти з генетичним алгоритмом":
                    if not experiment_config_file_path:
                        print("Помилка: Шлях до файлу конфігурації експериментів не було надано.\n")
                        return # Завершуємо потік, якщо шлях не надано
                    # Передаємо шлях до файлу у run_experiments
                    run_experimentsGenetic(experiment_config_file_path)
                elif current_file_path:
                    if config_type == "Зчитування даних у форматі .txt":
                        config = load_config_txt(current_file_path, value_count)
                    elif config_type == "Зчитування даних у форматі .xlsx":
                        config = load_config_xlsx(current_file_path, value_count)
                    else:
                        print(f"Помилка: Невідомий тип конфігурації '{config_type}' для завантаження файлу.\n")
                        return

                    if algo == "Генетичний":
                        run_genetic(config, value_count)
                    elif algo == "Жадібний":
                        run_greedy(config, value_count)
                    elif algo == "Генетичний + Жадібний":
                        run_both(config, value_count)
                    elif algo == "Комплектація":
                        run_equipment(config, value_count)
                    else:
                        print(f"Помилка: Невідомий алгоритм '{algo}'.\n")
                # Випадок, коли current_file_path не потрібен (наприклад, Експерименти вже оброблені)
                # або коли він був потрібен, але не наданий (цей випадок обробляється вище).
                elif config_type not in ["Експерименти"]: # Якщо це не експерименти, і немає файлу
                     print("Помилка: Шлях до файлу конфігурації не було надано, хоча він був потрібен.\n")


                print("\nОбробку завершено.\n")
                print("--------------------------------------------------\n")

            except Exception as e:
                print(f"\n!!! ВИНИКЛА ПОМИЛКА В АЛГОРИТМІ !!!\n{type(e).__name__}: {str(e)}\n")
                import traceback
                print("Деталі помилки:")
                print(traceback.format_exc())
            finally:
                queue_io.flush()
                self.root.after(100, self.remove_progress_lines_from_output)

    def remove_progress_lines_from_output(self):
        self.output_text.config(state='normal')
        content = self.output_text.get("1.0", tk.END)
        lines = content.split('\n')
        filtered_lines = [
            line for line in lines
            if "Прогрес генетичного алгоритму" not in line
               and "Прогрес жадібного алгоритму" not in line
        ]
        new_content = '\n'.join(filtered_lines)
        # Перевіряємо, чи вміст змінився, щоб уникнути зайвих оновлень
        if content.strip() != new_content.strip():
            current_scroll_pos = self.output_text.yview() # Зберігаємо позицію скролу
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, new_content)
            self.output_text.yview_moveto(current_scroll_pos[0]) # Відновлюємо позицію скролу
        self.output_text.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

