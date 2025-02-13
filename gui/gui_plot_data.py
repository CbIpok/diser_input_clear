#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt


def plot_file():
    # Открываем диалог выбора файла
    file_path = filedialog.askopenfilename(
        title="Выберите файл для отображения",
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )
    if file_path:
        try:
            # Загружаем данные из выбранного файла (ожидается 2D массив)
            data = np.loadtxt(file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
            return

        # Отображаем данные с использованием matplotlib
        plt.figure(figsize=(8, 6))
        im = plt.imshow(data, cmap='viridis')
        plt.title(f"Данные из файла:\n{file_path}")
        plt.colorbar(im)
        plt.show()


if __name__ == "__main__":
    # Создаем основное окно GUI
    root = tk.Tk()
    root.title("GUI для отображения данных")
    root.geometry("300x100")

    # Кнопка для выбора файла и отображения данных
    btn = tk.Button(root, text="Выбрать файл для отображения", command=plot_file)
    btn.pack(expand=True, pady=20)

    root.mainloop()
