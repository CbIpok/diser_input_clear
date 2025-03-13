import os
import matplotlib.pyplot as plt
import numpy as np

def save_array(data, path):
    """Сохраняет 2D массив в текстовый файл (значения разделены пробелами, строки – переносами).
    Создает необходимые директории, если их нет."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    np.savetxt(path, data, fmt='%.6f')


def plot_arrays(arrays):
    """
    Отображает два графика:
      - Верхний: сумма всех переданных 2D массивов.
      - Нижний: отдельный 2D массив, который можно листать с помощью клавиш "←" и "→".

    Параметры:
      arrays - список (или numpy-массив) 2D массивов, которые будут визуализированы.
    """


    if len(arrays) == 0:
        raise ValueError("Список массивов пуст.")

    # Создаём фигуру с двумя осями: верхняя для суммы, нижняя для индивидуального массива
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(8, 10))

    # Вычисляем сумму массивов и отображаем в верхней части
    sum_array = np.sum(arrays, axis=0)
    im_top = ax_top.imshow(sum_array, cmap='viridis')
    ax_top.set_title("Сумма массивов")
    plt.colorbar(im_top, ax=ax_top)

    # Отображаем первый массив из списка в нижней части
    current_index = 0
    im_bottom = ax_bottom.imshow(arrays[current_index], cmap='viridis')
    ax_bottom.set_title(f"Индивидуальный массив: индекс {current_index}")
    plt.colorbar(im_bottom, ax=ax_bottom)

    # Функция-обработчик для переключения массивов с помощью клавиатуры
    def on_key(event):
        nonlocal current_index
        if event.key == 'right':
            current_index = (current_index + 1) % len(arrays)
        elif event.key == 'left':
            current_index = (current_index - 1) % len(arrays)
        else:
            return
        im_bottom.set_data(arrays[current_index])
        ax_bottom.set_title(f"Индивидуальный массив: индекс {current_index}")
        fig.canvas.draw_idle()

    # Подключаем обработчик событий клавиатуры
    fig.canvas.mpl_connect('key_press_event', on_key)

    plt.tight_layout()
    plt.show()


def plot_multiple(loaded,ncols, nrows):
    x, y, n = loaded.shape

    # Определяем сетку subplot'ов
    # ncols = int(np.ceil(np.sqrt(n)))
    # nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows))
    # Гарантируем, что axes имеет двумерную структуру
    axes = np.atleast_2d(axes)

    for i in range(n):
        row = i // ncols
        col = i % ncols
        ax = axes[row, col]
        im = ax.imshow(loaded[:, :, i], cmap='viridis', origin='lower')
        ax.set_title(f'Плоскость {i + 1}')
        fig.colorbar(im, ax=ax)

    plt.tight_layout()
    plt.show()