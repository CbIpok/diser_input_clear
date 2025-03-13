#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt

# Импорт tkinterdnd2 для поддержки drag and drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    raise ImportError("Необходимо установить tkinterdnd2: pip install tkinterdnd2")


def plot_file(file_path):
    """
    Загружает данные из файла file_path (ожидается 2D массив)
    и отображает их с помощью matplotlib в неблокирующем режиме.
    """
    if file_path:
        try:
            data = np.loadtxt(file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
            return

        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(data, cmap='viridis')
        ax.set_title(f"Данные из файла:\n{file_path}")
        plt.colorbar(im, ax=ax)
        # Открываем окно графика в неблокирующем режиме
        plt.show(block=False)


def drop(event):
    """
    Обработчик события drag and drop.
    Извлекает путь к файлу из event.data, вызывает plot_file,
    и возвращает фокус в окно.
    """
    file_path = event.data
    # Если путь содержит фигурные скобки (при наличии пробелов), удаляем их
    if file_path.startswith("{") and file_path.endswith("}"):
        file_path = file_path[1:-1]
    # Если перетащили несколько файлов, берём первый
    file_path = file_path.split()[0]
    plot_file(file_path)
    # Фокусировка окна (можно оставить, если требуется)
    root.after(100, lambda: root.focus_force())


def open_file_dialog():
    """
    Открывает диалог выбора файла и вызывает plot_file.
    """
    file_path = filedialog.askopenfilename(
        title="Выберите файл для отображения",
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )
    plot_file(file_path)


if __name__ == "__main__":
    # Используем TkinterDnD.Tk() для поддержки drag and drop
    root = TkinterDnD.Tk()
    root.title("GUI для отображения данных")
    root.geometry("350x150")

    # Виджет для перетаскивания файла (метка)
    drop_label = tk.Label(root, text="Перетащите файл сюда", relief="raised", borderwidth=2, width=40, height=4)
    drop_label.pack(expand=True, pady=10)

    # Регистрируем область для drag and drop
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind("<<Drop>>", drop)

    # Кнопка для стандартного диалога выбора файла
    btn = tk.Button(root, text="Выбрать файл для отображения", command=open_file_dialog)
    btn.pack(expand=True, pady=10)

    root.mainloop()
