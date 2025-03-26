import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.ndimage import uniform_filter
from matplotlib.colors import ListedColormap, BoundaryNorm

# Список папок
basises = [
    "basis_6",
    "basis_8",
    "basis_10",
    "basis_15",
    "basis_20",
    "basis_24",
    "basis_30",
    "basis_36",
    "basis_40",
]

# Путь к базовой директории
base_dir = r"D:\dmitrienkomy\python\diser_framework\diser_input_clear\data\res\parabola_sine_200_2000\gaus_single_2"

# Пороговые значения для классификации:
# Значения < 0.3 → регион 0, 0.3 ≤ val < 0.5 → регион 1, ≥ 0.5 → регион 2.
region_thresholds = [0.3, 0.5]

# Определяем дискретную цветовую карту:
# регион 0 – зеленый, регион 1 – желтый, регион 2 – красный.
colors = ["green", "yellow", "red"]
cmap = ListedColormap(colors)
# Нормировка для корректного отображения значений 0, 1, 2
norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap.N)

# Создаем фигуру с 9 подграфиками (3x3) с автоматическим распределением элементов
fig, axes = plt.subplots(3, 3, figsize=(12, 12), constrained_layout=True)

# Проходим по списку папок
for i, folder in enumerate(basises):
    file_path = os.path.join(base_dir, folder, "rms_accuracy.txt")
    try:
        data = np.loadtxt(file_path)
    except Exception as e:
        print(f"Ошибка загрузки {file_path}: {e}")
        continue

    # Сглаживаем данные (окно 15x15)
    smoothed_data = uniform_filter(data, size=15)

    # Формируем дискретную карту: np.digitize возвращает 0 для значений < 0.3,
    # 1 для [0.3, 0.5) и 2 для значений ≥ 0.5.
    region_map = np.digitize(smoothed_data, region_thresholds)

    # Определяем текущий subplot
    row = i // 3
    col = i % 3
    ax = axes[row, col]

    # Отображаем heatmap
    im = ax.imshow(region_map, cmap=cmap, norm=norm, origin="upper")
    ax.set_title(folder)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

# Добавляем общий колорбар для всех подграфиков
cbar = fig.colorbar(im, ax=axes, orientation="vertical", shrink=0.8)
cbar.set_ticks([0, 1, 2])
cbar.ax.set_yticklabels(["<0.3", "0.3–0.5", ">0.5"])
cbar.set_label("RMS Accuracy Regions")

plt.show()
