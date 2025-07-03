import json
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def load_json_data(filename):
    """
    Загружает данные из JSON-файла и преобразует их в два массива:
    1. Массив коэффициентов размера (rows, cols, n_layers)
    2. Массив ошибок размера (rows, cols)
    """
    with open(filename, "r") as f:
        data = json.load(f)

    max_row, max_col = 0, 0
    n_layers = None

    # Определяем размеры сетки и число коэффициентов
    for key, value in data.items():
        row_str, col_str = key.strip("[]").split(",")
        row, col = int(row_str), int(col_str)
        max_row = max(max_row, row)
        max_col = max(max_col, col)
        if n_layers is None:
            n_layers = len(value["coefs"])
        else:
            if len(value["coefs"]) != n_layers:
                raise ValueError("Непоследовательное число коэффициентов в ключе " + key)

    # Инициализируем массивы с NaN для отсутствующих данных
    grid_coefs = np.empty((max_row + 1, max_col + 1, n_layers))
    grid_coefs[:] = np.nan
    grid_errors = np.empty((max_row + 1, max_col + 1))
    grid_errors[:] = np.nan

    # Заполняем массивы данными
    for key, value in data.items():
        row_str, col_str = key.strip("[]").split(",")
        row, col = int(row_str), int(col_str)
        grid_coefs[row, col, :] = value["coefs"]
        grid_errors[row, col] = value["aprox_error"]

    return grid_coefs, grid_errors


def load_config(config_path):
    """Загружает конфигурацию из файла zones.json."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


def load_wave(wave_path, sub_y_min, sub_y_max, sub_x_min, sub_x_max):
    """Загружает волну из файла и обрезает её по заданной области."""
    data = np.loadtxt(wave_path)
    return data[sub_y_min:sub_y_max, sub_x_min:sub_x_max]


def load_basis_functions(basis_directory, sub_y_min, sub_y_max, sub_x_min, sub_x_max, regex_pattern=r".*?(\d+)\.wave"):
    """
    Загружает базисные функции из файлов в директории basis_directory.
    Имена файлов сортируются по числовому индексу, извлекаемому регулярным выражением.
    Каждая базисная функция обрезается до заданной области.
    """
    files = os.listdir(basis_directory)
    basis_files = {}
    for filename in files:
        match = re.search(regex_pattern, filename)
        if match:
            index = int(match.group(1))
            full_path = os.path.join(basis_directory, filename)
            basis_files[index] = full_path
    loaded_bases = []
    for index in sorted(basis_files.keys()):
        data = np.loadtxt(basis_files[index])
        cropped = data[sub_y_min:sub_y_max, sub_x_min:sub_x_max]
        loaded_bases.append(cropped)
    return loaded_bases


def plot(x, y, config_path, wave_path, basis_directory, coefs_path):
    """
    Строит 2D графики для точки (x, y) коэффициентной сетки:
      - Исходная волна (wave)
      - Реконструкция (reconstruction)
      - Разница (wave - reconstruction)

    Аргументы:
      x, y           – индексы точки коэффициентной сетки;
      config_path    – путь к файлу zones.json;
      wave_path      – путь к файлу с волной;
      basis_directory– путь к директории с базисными функциями;
      coefs_path     – путь к JSON-файлу с коэффициентами.
    """
    # Загружаем конфигурацию и определяем область обрезки
    config = load_config(config_path)
    sub_y_min, sub_y_max, sub_x_min, sub_x_max = config["subduction_zone"]

    # Загружаем волну и базисные функции
    wave = load_wave(wave_path, sub_y_min, sub_y_max, sub_x_min, sub_x_max)
    basis_list = load_basis_functions(basis_directory, sub_y_min, sub_y_max, sub_x_min, sub_x_max)
    basis_stack = np.stack(basis_list, axis=0)

    # Загружаем коэффициенты (функция load_json_data возвращает кортеж (coefs, errors))
    coefs, _ = load_json_data(coefs_path)

    # Для точки (x, y) извлекаем коэффициенты, вычисляем реконструкцию и разницу
    coef = coefs[x, y, :]
    reconstruction = np.tensordot(coef, basis_stack, axes=([0], [0]))
    difference = wave - reconstruction

    # Строим 2D графики
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    axs[0].imshow(wave, cmap="viridis")
    axs[0].set_title("Wave")
    axs[1].imshow(reconstruction, cmap="viridis")
    axs[1].set_title("Reconstruction")
    axs[2].imshow(difference, cmap="viridis")
    axs[2].set_title("Difference (Wave - Reconstruction)")

    for ax in axs:
        ax.axis("off")
    plt.tight_layout()
    plt.show()


def plot3d(x, y, config_path, wave_path, basis_directory, coefs_path):
    """
    Строит 3D поверхности для точки (x, y) коэффициентной сетки:
      - Поверхность исходной волны (wave)
      - Поверхность реконструкции (reconstruction)
    с использованием plotly.

    Аргументы:
      x, y           – индексы точки коэффициентной сетки;
      config_path    – путь к файлу zones.json;
      wave_path      – путь к файлу с волной;
      basis_directory– путь к директории с базисными функциями;
      coefs_path     – путь к JSON-файлу с коэффициентами.
    """
    # Загружаем конфигурацию и определяем область обрезки
    config = load_config(config_path)
    sub_y_min, sub_y_max, sub_x_min, sub_x_max = config["subduction_zone"]

    # Загружаем волну и базисные функции
    wave = load_wave(wave_path, sub_y_min, sub_y_max, sub_x_min, sub_x_max)
    basis_list = load_basis_functions(basis_directory, sub_y_min, sub_y_max, sub_x_min, sub_x_max)
    basis_stack = np.stack(basis_list, axis=0)

    # Загружаем коэффициенты
    coefs, _ = load_json_data(coefs_path)

    # Для выбранной точки (x, y) извлекаем коэффициенты и вычисляем реконструкцию
    coef = coefs[x, y, :]
    reconstruction = np.tensordot(coef, basis_stack, axes=([0], [0]))

    # Создаём координатную сетку для осей X и Y
    H, W = wave.shape
    x_coords = np.arange(W)
    y_coords = np.arange(H)
    X, Y = np.meshgrid(x_coords, y_coords)

    # Строим 3D график с помощью plotly
    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=X, y=Y, z=wave,
        colorscale='Viridis',
        opacity=0.99,
        name='Wave',
        showscale=False
    ))
    fig.add_trace(go.Surface(
        x=X, y=Y, z=reconstruction,
        colorscale='Cividis',
        opacity=0.99,
        name='Reconstruction',
        showscale=False
    ))
    # Увеличиваем размер шрифта примерно в 3 раза (например, до 36)
    fig.update_layout(
        title=f"3D Plot for Point ({x}, {y})",
        title_font=dict(size=36),
        scene=dict(
            xaxis=dict(
                title='X',
                title_font=dict(size=16),
                tickfont=dict(size=16)
            ),
            yaxis=dict(
                title='Y',
                title_font=dict(size=16),
                tickfont=dict(size=16)
            ),
            zaxis=dict(
                title='Amplitude',
                title_font=dict(size=16),
                tickfont=dict(size=16)
            )
        ),
        font=dict(size=66),
        autosize=True
    )
    fig.show()

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
    "basis_48"
]

waves = [
    "gaus_double_0.5_0.75",
    "gaus_double_0.75_0.5",
    "gaus_single_1_real",
    "gaus_single_2",
]

bathes = [
        "parabola_200_2000",
        "parabola_sine_200_2000",
        "x_200_2000",
        "y_200_2000",
    ]

if __name__ == "__main__":
    config_path = os.path.join("..", "config", "zones.json")
    root_folder = r"E:\tsunami_res_dir\n_accurate_set"
    wave_name = waves[2]
    wave_path = os.path.join(root_folder, "waves", f"{wave_name}.wave")
    basis_index = 0
    basis = basises[3]
    bath = bathes[1]
    basis_directory = os.path.join(root_folder, "basises", basis)
    coefs_path = rf"E:\tsunami_res_dir\coefs_nessesary\case_statistics_hd_y_gaus_single_1_real_{basis}_{bath}_last.json"
    plot3d(400,400,config_path, wave_path, basis_directory, coefs_path)

