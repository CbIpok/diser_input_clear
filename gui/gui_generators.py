#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

# Определение параметров для каждого генератора
generator_params = {
    "generate_data": {
        "script": "generate_data.py",
        "params": [
            {"flag": "--form", "type": "choice", "choices": ["gradient_x", "gradient_y", "parabola", "parabola_sine"],
             "default": "gradient_x", "label": "Форма"},
            {"flag": "--output", "type": "str", "default": "data/output.txt", "label": "Путь вывода"},
            {"flag": "--min_value", "type": "float", "default": 0.0, "label": "Мин. значение"},
            {"flag": "--max_value", "type": "float", "default": 1.0, "label": "Макс. значение"},
            {"flag": "--sin_amp", "type": "float", "default": 0.5, "label": "Амплитуда синуса",
             "depends_on": {"flag": "--form", "value": "parabola_sine"}},
            {"flag": "--sin_period_x", "type": "int", "default": 50, "label": "Период X",
             "depends_on": {"flag": "--form", "value": "parabola_sine"}},
            {"flag": "--sin_period_y", "type": "int", "default": 50, "label": "Период Y",
             "depends_on": {"flag": "--form", "value": "parabola_sine"}},
        ]
    },
    "generate_subduction": {
        "script": "generate_subduction.py",
        "params": [
            {"flag": "--form", "type": "choice", "choices": ["gaussian", "double_gaussian"],
             "default": "gaussian", "label": "Форма"},
            {"flag": "--output", "type": "str", "default": "subduction/output.txt", "label": "Путь вывода"},
            {"flag": "--sigma", "type": "float", "default": 50.0, "label": "Sigma"},
            {"flag": "--amplitude", "type": "float", "default": 1.0, "label": "Амплитуда",
             "depends_on": {"flag": "--form", "value": "gaussian"}},
            {"flag": "--amplitude1", "type": "float", "default": 1.0, "label": "Амплитуда верхней",
             "depends_on": {"flag": "--form", "value": "double_gaussian"}},
            {"flag": "--amplitude2", "type": "float", "default": 1.0, "label": "Амплитуда нижней",
             "depends_on": {"flag": "--form", "value": "double_gaussian"}},
        ]
    },
    "generate_basis": {
        "script": "generate_basis.py",
        "params": [
            {"flag": "--tile-height", "type": "int", "default": 50, "label": "Высота плитки"},
            {"flag": "--tile-width", "type": "int", "default": 100, "label": "Ширина плитки"},
            {"flag": "--output-dir", "type": "str", "default": "basis_functions", "label": "Директория вывода"},
            {"flag": "--value", "type": "float", "default": 1.0, "label": "Значение"},
            {"flag": "--visualize", "type": "bool", "default": False, "label": "Визуализировать"},
        ]
    }
}


class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор BAT-файла для запуска генераторов")
        self.param_vars = {}  # Хранит переменные для всех параметров текущего генератора

        # Основное окно разделено на 2 части: слева – настройки, справа – итоговый текст
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Левая панель: выбор генератора
        ttk.Label(self.left_frame, text="Выберите генератор:").pack(anchor=tk.W)
        self.generator_choice = ttk.Combobox(self.left_frame, values=list(generator_params.keys()), state="readonly")
        self.generator_choice.pack(fill=tk.X, pady=5)
        self.generator_choice.bind("<<ComboboxSelected>>", self.on_generator_change)
        self.generator_choice.current(0)

        # Рамка для параметров выбранного генератора (разделена на две части)
        self.params_frame = ttk.LabelFrame(self.left_frame, text="Параметры")
        self.params_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.control_frame = ttk.Frame(self.params_frame)
        self.control_frame.pack(fill=tk.X, pady=2)
        self.dependent_frame = ttk.Frame(self.params_frame)
        self.dependent_frame.pack(fill=tk.X, pady=2)

        # Кнопка для добавления команды в итоговый BAT-файл
        self.add_button = ttk.Button(self.left_frame, text="Добавить текст запуска", command=self.add_command)
        self.add_button.pack(pady=5, fill=tk.X)

        # Правая панель: текстовое поле для итогового BAT-файла
        ttk.Label(self.right_frame, text="Суммарный BAT-файл:").pack(anchor=tk.W)
        self.text_area = tk.Text(self.right_frame, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.scroll_y = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.save_button = ttk.Button(self.right_frame, text="Сохранить в файл", command=self.save_to_file)
        self.save_button.pack(pady=5)

        # Инициализация полей параметров для выбранного генератора
        self.current_generator = None
        self.update_params_frame(initial=True)

    def on_generator_change(self, event=None):
        # При смене генератора полностью пересоздаем все параметры
        self.update_params_frame(initial=True)

    def update_params_frame(self, initial=False):
        gen_type = self.generator_choice.get()
        params_list = generator_params[gen_type]["params"]

        if self.current_generator != gen_type or initial:
            # Если генератор изменился, очищаем обе области и пересоздаем контролирующие параметры
            for widget in self.control_frame.winfo_children():
                widget.destroy()
            for widget in self.dependent_frame.winfo_children():
                widget.destroy()
            self.param_vars = {}
            for param in params_list:
                if "depends_on" not in param:
                    self.create_param_widget(param, parent=self.control_frame)
            self.current_generator = gen_type
        else:
            # Если генератор не изменился, просто обновляем зависимые параметры
            for widget in self.dependent_frame.winfo_children():
                widget.destroy()

        # Создаем зависимые параметры, если условие выполнено
        for param in params_list:
            if "depends_on" in param:
                dep = param["depends_on"]
                ctrl_flag = dep["flag"]
                required_value = str(dep["value"])
                if ctrl_flag in self.param_vars and str(self.param_vars[ctrl_flag].get()) == required_value:
                    self.create_param_widget(param, parent=self.dependent_frame)

    def create_param_widget(self, param, parent):
        """Создает виджет для параметра и сохраняет переменную в self.param_vars."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        label = ttk.Label(frame, text=param["label"] + ":")
        label.pack(side=tk.LEFT)

        flag = param["flag"]
        p_type = param["type"]
        default = param.get("default", "")

        if p_type == "choice":
            var = tk.StringVar(value=str(default))
            combo = ttk.Combobox(frame, textvariable=var, values=param["choices"], state="readonly", width=15)
            combo.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            # При изменении значения обновляем только зависимые параметры
            var.trace_add("write", lambda *args: self.update_params_frame())
        elif p_type in ["int", "float", "str"]:
            var = tk.StringVar(value=str(default))
            entry = ttk.Entry(frame, textvariable=var)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        elif p_type == "bool":
            var = tk.BooleanVar(value=default)
            chk = ttk.Checkbutton(frame, variable=var)
            chk.pack(side=tk.RIGHT)
        else:
            var = tk.StringVar(value=str(default))
            entry = ttk.Entry(frame, textvariable=var)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.param_vars[flag] = var

    def add_command(self):
        """Генерирует командную строку на основе выбранного генератора и введённых параметров,
        затем добавляет её в итоговое текстовое поле."""
        gen_type = self.generator_choice.get()
        script = generator_params[gen_type]["script"]
        # Префикс для установки PYTHONPATH (чтобы корень проекта был в sys.path)
        cmd_parts = [f"set PYTHONPATH=%CD% && python scripts/{script}"]

        for param in generator_params[gen_type]["params"]:
            flag = param["flag"]
            # Для зависимых параметров проверяем условие
            if "depends_on" in param:
                dep = param["depends_on"]
                ctrl_flag = dep["flag"]
                required_value = str(dep["value"])
                if ctrl_flag in self.param_vars and str(self.param_vars[ctrl_flag].get()) != required_value:
                    continue
                elif ctrl_flag not in self.param_vars:
                    continue

            if flag in self.param_vars:
                value = self.param_vars[flag].get()
            else:
                value = str(param.get("default", ""))
            if param["type"] == "bool":
                if self.param_vars[flag].get():
                    cmd_parts.append(flag)
            else:
                if value != "":
                    cmd_parts.append(f"{flag} {value}")
        cmd_line = " ".join(cmd_parts)
        self.text_area.insert(tk.END, cmd_line + "\n")
        self.text_area.see(tk.END)

    def save_to_file(self):
        """Сохраняет содержимое итогового текстового поля в выбранный файл."""
        file_path = filedialog.asksaveasfilename(defaultextension=".bat",
                                                 filetypes=[("BAT файлы", "*.bat"), ("Все файлы", "*.*")],
                                                 title="Сохранить BAT файл")
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.text_area.get("1.0", tk.END))
                messagebox.showinfo("Сохранено", f"Файл успешно сохранён:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()
