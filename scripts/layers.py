import numpy as np
import os
import plotly.graph_objects as go
from scipy.ndimage import uniform_filter

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
]

# Базовый путь к данным
base_dir = r"D:\dmitrienkomy\python\diser_framework\diser_input_clear\data\res\parabola_sine_200_2000\gaus_double_1_2"

# ==== Определение порогов областей ====
# Здесь задаются интервалы значений и соответствующие цвета.
# Каждый интервал определён парой: [минимальное значение, максимальное значение).
# Обратите внимание: область с значениями >=1 тоже отображается.
# Изменять пороги можно, отредактировав этот список.
region_thresholds = [
    {"min": -np.inf, "max": 0.1, "color": "blue", "label": "<0.1"},
    {"min": 0.1, "max": 0.25, "color": "green", "label": "0.1–0.25"},
    {"min": 0.25, "max": 0.5, "color": "orange", "label": "0.25–0.5"},
    {"min": 0.5, "max": 1, "color": "red", "label": "0.5–1"},
    {"min": 1, "max": np.inf, "color": "magenta", "label": "≥1"}
]

# Для формирования дискретной цветовой шкалы извлекаем цвета по порядку
colors_for_regions = [region["color"] for region in region_thresholds]

# Создаём дискретную шкалу для Plotly.
# Значения шкалы нормированы от 0 до 1: здесь 5 интервалов -> шаг 0.2.
discrete_colorscale = [
    [0.0, colors_for_regions[0]],
    [0.2, colors_for_regions[0]],
    [0.2, colors_for_regions[1]],
    [0.4, colors_for_regions[1]],
    [0.4, colors_for_regions[2]],
    [0.6, colors_for_regions[2]],
    [0.6, colors_for_regions[3]],
    [0.8, colors_for_regions[3]],
    [0.8, colors_for_regions[4]],
    [1.0, colors_for_regions[4]]
]
# ==== Конец блока редактирования порогов ====

fig = go.Figure()

# Проходим по всем папкам (слоям)
for folder in basises:
    # Извлекаем числовое значение basis (например, "basis_6" → 6)
    z_val = int(folder.split('_')[1])
    file_path = os.path.join(base_dir, folder, "rms_accuracy.txt")

    try:
        # Загружаем 2D-массив из файла
        data = np.loadtxt(file_path)
    except Exception as e:
        print(f"Не удалось загрузить {file_path}: {e}")
        continue

    # Сглаживание данных (окно 5×5)
    smoothed_data = uniform_filter(data, size=5)

    # Определяем для каждого элемента, к какому региону (интервалу) он принадлежит.
    # Создаём массив той же формы, где каждому элементу присвоим индекс региона.
    region_array = np.zeros_like(smoothed_data, dtype=int)
    for i, region in enumerate(region_thresholds):
        mask = (smoothed_data >= region["min"]) & (smoothed_data < region["max"])
        region_array[mask] = i

    # Формируем координатную сетку для плоскости
    ny, nx = smoothed_data.shape
    x = np.linspace(0, nx - 1, nx)
    y = np.linspace(0, ny - 1, ny)
    X, Y = np.meshgrid(x, y)

    # Создаём поверхность для данного слоя.
    # Плоскость располагается на z = z_val, а color задаётся массивом region_array.
    fig.add_trace(go.Surface(
        x=X,
        y=Y,
        z=np.full_like(smoothed_data, z_val),
        surfacecolor=region_array,
        colorscale=discrete_colorscale,
        cmin=0,
        cmax=len(region_thresholds) - 1,
        opacity=0.9,
        colorbar=dict(
            tickmode='array',
            tickvals=list(range(len(region_thresholds))),
            ticktext=[region["label"] for region in region_thresholds],
            title="Value Range"
        ),
        showscale=True,
        name=f"Basis {z_val}"
    ))

# Настройка внешнего вида графика
fig.update_layout(
    scene=dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Basis (z)"
    ),
    title="3D-заштрихованные области RMS Accuracy по слоям"
)

fig.show()
