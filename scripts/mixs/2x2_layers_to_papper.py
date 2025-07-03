import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.colors import ListedColormap, BoundaryNorm

# Увеличиваем размер шрифта в 2 раза
plt.rcParams['font.size'] *= 2

# Параметр вертикального сдвига (можно менять)
vertical_shift = 0.05

# Выбираем только необходимые папки
basises = [
    "basis_10",
    "basis_12",
    "basis_30",
    "basis_36"
]

# Путь к базовой директории
base_dir = r"/data/final/parabola_sine_200_2000"

# Пороговые значения для классификации:
region_thresholds = [0.2, 0.4]

# Определяем дискретную цветовую карту:
colors = ["green", "yellow", "red"]
cmap = ListedColormap(colors)
norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap.N)

# Создаем фигуру с 2 рядами и 2 столбцами подграфиков
fig, axes = plt.subplots(2, 2, figsize=(10, 10))
# Отступ снизу увеличиваем на vertical_shift для сдвига всего содержимого вверх
plt.subplots_adjust(bottom=0.15 + vertical_shift, wspace=0.3, hspace=0.3)

im = None

for i, folder in enumerate(basises):
    file_path = os.path.join(base_dir, folder, "rms_accuracy.txt")
    try:
        data = np.loadtxt(file_path)
    except Exception as e:
        print(f"Ошибка загрузки {file_path}: {e}")
        continue

    # Если нужно можно добавить сглаживание, например, с помощью uniform_filter
    smoothed_data = data

    # Формируем дискретную карту: np.digitize возвращает 0 для значений < 0.3,
    # 1 для [0.3, 0.5) и 2 для ≥ 0.5
    region_map = np.digitize(smoothed_data, region_thresholds)

    row = i // 2
    col = i % 2
    ax = axes[row, col]

    im = ax.imshow(region_map, cmap=cmap, norm=norm, origin="upper")
    try:
        N = folder.split('_')[1]
    except IndexError:
        N = folder
    ax.set_title(f"{N} of UnSs")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

# Создаем отдельную ось для горизонтального колорбара под графиками и сдвигаем ее вверх на vertical_shift
cbar_ax = fig.add_axes([0.15, 0.05 + vertical_shift, 0.7, 0.03])
cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', ticks=[0, 1, 2])
cbar.ax.set_xticklabels(["<20%", "20–40%", ">40%"])
cbar.set_label("RMS Accuracy Regions")

plt.show()
