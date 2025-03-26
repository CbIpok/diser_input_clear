import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.ndimage import uniform_filter
from matplotlib.colors import ListedColormap, BoundaryNorm

# Список папок
basises = [
    "basis_6",
    "basis_8",
    "basis_9",
    "basis_10",
    "basis_12",
    "basis_15",
    "basis_16",
    "basis_18",
    "basis_20",
    "basis_24",
    "basis_25",
    "basis_30",
    "basis_36",
    "basis_40",
    "basis_48",
]

# Путь к базовой директории
base_dir = r"D:\dmitrienkomy\python\diser_framework\diser_input_clear\data\res_real\x_200_2000\async_gaus_single_2"

# Пороговые значения для классификации:
# Значения < 0.3 → регион 0, 0.3 ≤ val < 0.5 → регион 1, ≥ 0.5 → регион 2.
region_thresholds = [0.3, 0.5]

# Определяем дискретную цветовую карту:
# регион 0 – зеленый, регион 1 – желтый, регион 2 – красный.
colors = ["green", "yellow", "red"]
cmap = ListedColormap(colors)
# Нормировка, чтобы значения 0, 1, 2 попадали в нужные интервалы
norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap.N)

# Создаем фигуру с 9 подграфиками (3 строки x 3 столбца)
fig, axes = plt.subplots(4, 4, figsize=(12, 12))

# Настраиваем промежутки: уменьшаем горизонтальное расстояние (wspace)
# и оставляем место справа (right) для отдельной оси колорбара
plt.subplots_adjust(wspace=0.3, hspace=0.3, right=0.8)

# Проходим по списку папок
for i, folder in enumerate(basises):
    file_path = os.path.join(base_dir, folder, "rms_accuracy.txt")
    try:
        data = np.loadtxt(file_path)
    except Exception as e:
        print(f"Ошибка загрузки {file_path}: {e}")
        continue

    # Сглаживаем данные (окно 15x15)
    smoothed_data = data

    # Формируем дискретную карту: np.digitize возвращает 0 для значений < 0.3,
    # 1 для [0.3, 0.5) и 2 для >= 0.5
    region_map = np.digitize(smoothed_data, region_thresholds)

    # Определяем текущий subplot
    row = i // 4
    col = i % 4
    ax = axes[row, col]

    # Отображаем heatmap
    im = ax.imshow(region_map, cmap=cmap, norm=norm, origin="upper")
    ax.set_title(folder)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

# Создаем отдельную ось для колорбара справа от подграфиков
cbar_ax = fig.add_axes([0.85, 0.15, 0.03, 0.7])
cbar = fig.colorbar(im, cax=cbar_ax, ticks=[0, 1, 2])
cbar.ax.set_yticklabels(["<0.3", "0.3–0.5", ">0.5"])
cbar.set_label("RMS Accuracy Regions")

plt.show()
