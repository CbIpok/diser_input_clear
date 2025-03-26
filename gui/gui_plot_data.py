#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
import json
from tkinterdnd2 import DND_FILES, TkinterDnD
from matplotlib.colors import ListedColormap
import plotly.graph_objects as go

# Глобальная переменная для хранения загруженных данных
loaded_data = None

def plot_2d(file_path, data):
    """
    Отображает данные в 2D с помощью imshow.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(data, cmap='viridis')
    ax.set_title(f"2D: Данные из файла:\n{file_path}")
    plt.colorbar(im, ax=ax)
    plt.show(block=False)

def plot_by_threshold(file_path, data):
    """
    Отображает данные, разделяя области по пороговому значению,
    введённому пользователем. Значения больше порога – красным,
    меньше или равные – зелёным.
    """
    threshold_str = threshold_entry.get()
    try:
        threshold = float(threshold_str)
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректное числовое значение порога.")
        return

    # Создаем маску: 1 для значений > threshold, 0 для значений <= threshold
    mask = (data > threshold).astype(int)
    cmap = ListedColormap(['green', 'red'])

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(mask, cmap=cmap, vmin=0, vmax=1)
    ax.set_title(f"Зоны: красные > {threshold}, зелёные <= {threshold}")
    plt.colorbar(im, ax=ax, ticks=[0, 1], label='0: <= порог, 1: > порог')
    plt.show(block=False)

def plot_3d(file_path, data):
    """
    Отображает данные в 3D в виде поверхности с использованием Plotly.
    """
    fig = go.Figure(data=[go.Surface(z=data)])
    fig.update_layout(
        title=f"3D: Данные из файла:\n{file_path}",
        autosize=True,
        width=800,
        height=600,
        margin=dict(l=65, r=50, b=65, t=90)
    )
    fig.show()

def handle_file(file_path):
    """
    Загружает данные из выбранного файла, сохраняет их в loaded_data и
    отображает согласно выбранному режиму из выпадающего списка.
    При активированной галочке обрезает данные по выбранной зоне из ../config/zones.json.
    Структура zones.json:
    {
        "size": [2048, 2048], # x_size, y_size
        "subduction_zone": [128, 248, 904, 1144], #[y_min, y_max, x_min, x_max]
        "mariogramm_zone": [448, 1848, 24, 2024] #[y_min, y_max, x_min, x_max]
    }
    """
    global loaded_data
    if file_path:
        try:
            data = np.loadtxt(file_path)
            loaded_data = data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
            return

        # Если активирована галочка, обрезаем данные по выбранной зоне
        if zone_var.get():
            try:
                with open("../config/zones.json", "r") as f:
                    zones_config = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить zones.json:\n{e}")
                return
            zone_key = zone_option.get()
            if zone_key in zones_config:
                coords = zones_config[zone_key]  # [y_min, y_max, x_min, x_max]
                try:
                    data = data[coords[0]:coords[1], coords[2]:coords[3]]
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при обрезке данных:\n{e}")
                    return
            else:
                messagebox.showerror("Ошибка", "Выбранная зона не найдена в конфигурации.")
                return

        mode = display_mode.get()
        if mode == "отобразить 2д":
            plot_2d(file_path, data)
        elif mode == "отрисовать по областям":
            plot_by_threshold(file_path, data)
        elif mode == "отрисовать 3д":
            plot_3d(file_path, data)

def drop(event):
    """
    Обработчик события drag and drop.
    Извлекает путь к файлу из event.data и вызывает handle_file.
    """
    file_path = event.data
    if file_path.startswith("{") and file_path.endswith("}"):
        file_path = file_path[1:-1]
    file_path = file_path.split()[0]
    handle_file(file_path)
    root.after(100, lambda: root.focus_force())

def open_file_dialog():
    """
    Открывает диалог выбора файла и передаёт путь в handle_file.
    """
    file_path = filedialog.askopenfilename(
        title="Выберите файл для отображения",
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )
    handle_file(file_path)

def update_threshold_visibility(*args):
    """
    Отображает или скрывает поле ввода порога в зависимости от выбранного режима.
    """
    if display_mode.get() == "отрисовать по областям":
        threshold_frame.pack(expand=True, pady=5)
    else:
        threshold_frame.forget()

def update_zone_dropdown_state():
    """
    Обновляет состояние выпадающего списка зон в зависимости от состояния галочки.
    """
    if zone_var.get():
        zone_option_menu.config(state="normal")
    else:
        zone_option_menu.config(state="disabled")

if __name__ == "__main__":
    # Используем TkinterDnD.Tk() для поддержки drag and drop
    root = TkinterDnD.Tk()
    root.title("GUI для отображения данных")
    root.geometry("400x350")

    # Виджет для перетаскивания файла (метка)
    drop_label = tk.Label(root, text="Перетащите файл сюда", relief="raised", borderwidth=2, width=40, height=4)
    drop_label.pack(expand=True, pady=10)
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind("<<Drop>>", drop)

    # Кнопка для стандартного диалога выбора файла
    btn = tk.Button(root, text="Выбрать файл для отображения", command=open_file_dialog)
    btn.pack(expand=True, pady=5)

    # Выпадающий список для выбора режима отображения
    display_mode = tk.StringVar(value="отобразить 2д")
    mode_options = ["отобразить 2д", "отрисовать по областям", "отрисовать 3д"]
    mode_menu = tk.OptionMenu(root, display_mode, *mode_options)
    mode_menu.pack(expand=True, pady=5)
    display_mode.trace("w", update_threshold_visibility)

    # Фрейм для ввода порогового значения (отображается только в режиме "отрисовать по областям")
    threshold_frame = tk.Frame(root)
    threshold_label = tk.Label(threshold_frame, text="Порог:")
    threshold_label.pack(side=tk.LEFT, padx=(0, 5))
    threshold_entry = tk.Entry(threshold_frame, width=10)
    threshold_entry.pack(side=tk.LEFT, padx=(0, 5))

    # Фрейм для выбора зоны
    zone_frame = tk.Frame(root)
    zone_var = tk.BooleanVar(value=False)
    zone_checkbox = tk.Checkbutton(zone_frame, text="Отобразить выбранную зону", variable=zone_var,
                                   command=update_zone_dropdown_state)
    zone_checkbox.pack(side=tk.LEFT, padx=(0, 5))
    zone_option = tk.StringVar(value="subduction_zone")
    zone_options = ["subduction_zone", "mariogramm_zone"]
    zone_option_menu = tk.OptionMenu(zone_frame, zone_option, *zone_options)
    zone_option_menu.config(state="disabled")  # по умолчанию отключено
    zone_option_menu.pack(side=tk.LEFT, padx=(0, 5))
    zone_frame.pack(expand=True, pady=5)

    root.mainloop()
