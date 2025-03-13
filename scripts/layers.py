import numpy as np
import plotly.graph_objects as go
from scipy.ndimage import uniform_filter
import os
from skimage import measure

# Флаг: если True, то отрисовываются только контуры, иначе – заполненные области
only_contours = False

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

# ============================
# Пороговые значения для областей.
# Изменив список ниже, можно задать сколько порогов (и, соответственно, контуров) нужно отобразить.
# Например, region_thresholds = [0.25, 0.5, 1] даст три контура:
#   Контур для значений ~0.25, для ~0.5 и для ~1.
region_thresholds = [0.25, 0.75]

# ============================
# Определяем цвета с прозрачностью.
# Для заполнённых областей (Surface) должно быть len(region_thresholds)+1 цветов.
# Для примера:
#   Зеленый, оранжевый, красный и пурпурный с прозрачностью 0.5.
region_colors = [
    'rgba(0,128,0,0.9)',     # зеленый с прозрачностью 0.5
    'rgba(255,165,0,0.1)',   # оранжевый с прозрачностью 0.5
    'rgba(255,0,0,0.2)',     # красный с прозрачностью 0.5
]
# Для контура нужно задать столько цветов, сколько порогов.
# Здесь для контуров используем цвета с чуть большей непрозрачностью (альфа = 0.7)
contour_colors = [
    'rgba(0,128,0,0.7)',     # зеленый
    'rgba(255,165,0,0.7)',   # оранжевый
    'rgba(255,0,0,0.7)'      # красный
]

# Если используется заполнение областей, создаём дискретную цветовую шкалу для Plotly.
n_regions = len(region_colors)
colorscale = []
for i, col in enumerate(region_colors):
    start = i / n_regions
    end = (i + 1) / n_regions
    colorscale.append([start, col])
    colorscale.append([end, col])

# Путь к базовой директории
base_dir = r"D:\dmitrienkomy\python\diser_framework\diser_input_clear\data\res\parabola_sine_200_2000\gaus_double_1_2"

fig = go.Figure()

for folder in basises:
    # Извлекаем значение для оси Z из имени папки (например, "basis_6" -> 6)
    try:
        z_val = int(folder.split('_')[1])
    except Exception as e:
        print(f"Ошибка при извлечении z для {folder}: {e}")
        continue

    file_path = os.path.join(base_dir, folder, "rms_accuracy.txt")
    try:
        # Загружаем 2D-массив из файла
        data = np.loadtxt(file_path)
    except Exception as e:
        print(f"Не удалось загрузить {file_path}: {e}")
        continue

    # Сглаживаем данные (окно можно подбирать, здесь 15x15)
    smoothed_data = uniform_filter(data, size=15)

    # Создаем координатную сетку для x и y
    nrows, ncols = data.shape
    x = np.linspace(0, ncols - 1, ncols)
    y = np.linspace(0, nrows - 1, nrows)
    X, Y = np.meshgrid(x, y)
    Z = np.full_like(smoothed_data, fill_value=z_val)

    if only_contours:
        # Отрисовка только контуров: для каждого порога ищем границы и добавляем линии
        for i, thr in enumerate(region_thresholds):
            contours = measure.find_contours(smoothed_data, level=thr)
            for contour in contours:
                # Перевод координат: (row, col) -> (y, x)
                x_contour = contour[:, 1]
                y_contour = contour[:, 0]
                z_contour = np.full_like(x_contour, fill_value=z_val)
                fig.add_trace(go.Scatter3d(
                    x=x_contour,
                    y=y_contour,
                    z=z_contour,
                    mode='lines',
                    line=dict(color=contour_colors[i], width=4),
                    name=f"{folder} thr={thr}",
                    showlegend=False
                ))
    else:
        # Отрисовка заполнённых областей
        region_map = np.digitize(smoothed_data, region_thresholds)
        fig.add_trace(go.Surface(
            x=X,
            y=Y,
            z=Z,
            surfacecolor=region_map,
            colorscale=colorscale,
            cmin=0,
            cmax=n_regions,
            showscale=False,
            name=f"{folder}"
        ))

fig.update_layout(
    title="3D график RMS Accuracy " + ("- Только контуры" if only_contours else "- Заштрихованные области"),
    scene=dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Basis (z)"
    )
)

fig.show()
