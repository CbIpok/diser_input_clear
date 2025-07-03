import numpy as np
import matplotlib.pyplot as plt
import os

# Увеличиваем шрифт в 2 раза (если базовый размер был 13, теперь 26)
plt.rcParams.update({'font.size': 26})

# Список папок (наборы basis)
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

# Пороговые значения для классификации:
region_thresholds = [0.2, 0.4]

# Директории и соответствующие стили линий:
base_dirs = [
    (r"D:\dmitrienkomy\python\diser_framework\diser_input_clear\data\final\x_200_2000", "dashed"),
    (r"D:\dmitrienkomy\python\diser_framework\diser_input_clear\data\final\parabola_sine_200_2000", "solid")
]

# Извлекаем числовое значение из имени папки (например, "basis_6" -> 6)
x_values = []
for folder in basises:
    try:
        x_val = int(folder.split("_")[1])
    except Exception as e:
        print(f"Ошибка при извлечении числа из {folder}: {e}")
        x_val = np.nan
    x_values.append(x_val)
x_values = np.array(x_values)

# Задаем метки по оси x (только те, которые нужны)
ticks_required = {6, 12, 18, 24, 30, 36, 48}
xtick_values = [x for x in x_values if x in ticks_required]

# Словари для хранения результатов:
# Ключ: (base_dir, j), где j - индекс порога (0 или 1)
results_percentage = {}
results_mean = {}

# Инициализация списков для каждого сочетания base_dir и порога
for base_dir, linestyle in base_dirs:
    for j in range(len(region_thresholds)):
        results_percentage[(base_dir, j)] = []
        results_mean[(base_dir, j)] = []

# Проходим по базовым директориям и наборам
for base_dir, linestyle in base_dirs:
    for folder in basises:
        file_path = os.path.join(base_dir, folder, "rms_accuracy.txt")
        try:
            data = np.loadtxt(file_path)
        except Exception as e:
            print(f"Ошибка загрузки {file_path}: {e}")
            # Если файл не найден или произошла ошибка загрузки, заполняем результат nan
            for j in range(len(region_thresholds)):
                results_percentage[(base_dir, j)].append(np.nan)
                results_mean[(base_dir, j)].append(np.nan)
            continue

        total_points = data.size

        # Для каждого порога вычисляем процент точек и среднее значение по точкам меньше порога
        for j, threshold in enumerate(region_thresholds):
            mask = data < threshold
            count = np.sum(mask)
            percent = (count / total_points) * 100 if total_points > 0 else 0
            results_percentage[(base_dir, j)].append(percent)
            if count > 0:
                mean_val = data[mask].mean()
            else:
                mean_val = np.nan
            # Умножаем среднее значение на 100 для отображения в процентах
            results_mean[(base_dir, j)].append(mean_val * 100)

# Построение первого графика: процент точек ниже порога от basis
fig1 = plt.figure()
# Цвета для порогов: для region_thresholds[0] и region_thresholds[1]
colors = ["green", "orange"]
for base_dir, linestyle in base_dirs:
    for j, color in enumerate(colors):
        plt.plot(x_values, results_percentage[(base_dir, j)],
                 linestyle=linestyle, marker='o', color=color,
                 linewidth=5, markersize=12)
plt.xlabel("number of UnSs", fontsize=26)
plt.ylabel("Surface area (%)", fontsize=26)
plt.title("Surface area with error < 20% (green) and < 40% (yellow)", fontsize=32)
plt.grid(True)
plt.xticks(xtick_values, xtick_values, fontsize=28)
plt.yticks(fontsize=28)

# Построение второго графика: среднее значение в зоне ниже порога от basis
fig2 = plt.figure()
for base_dir, linestyle in base_dirs:
    for j, color in enumerate(colors):
        plt.plot(x_values, results_mean[(base_dir, j)],
                 linestyle=linestyle, marker='o', color=color,
                 linewidth=5, markersize=12)
plt.xlabel("number of UnSs", fontsize=26)
plt.ylabel("average value (%)", fontsize=26)
plt.title("Average value in the surface with error < 20% (green) and < 40% (yellow)", fontsize=32)
plt.grid(True)
plt.xticks(xtick_values, xtick_values, fontsize=28)
plt.yticks(fontsize=28)

plt.show()
