import os
import json
import numpy as np
import re
from tqdm import tqdm
import plotly.graph_objects as go

def average_reconstructions(reconstruction_list):
    """
    Вычисляет среднее арифметическое реконструкций.
    """
    mean_reconstruction = np.zeros_like(reconstruction_list[0])
    for rec in reconstruction_list:
        mean_reconstruction += rec
    mean_reconstruction /= len(reconstruction_list)
    return mean_reconstruction

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

    grid_coefs = np.empty((max_row + 1, max_col + 1, n_layers))
    grid_coefs[:] = np.nan
    grid_errors = np.empty((max_row + 1, max_col + 1))
    grid_errors[:] = np.nan

    for key, value in data.items():
        row_str, col_str = key.strip("[]").split(",")
        row, col = int(row_str), int(col_str)
        grid_coefs[row, col, :] = value["coefs"]
        grid_errors[row, col] = value["aprox_error"]

    return grid_coefs, grid_errors

def load_basis(basis_directory, sub_y_min, sub_y_max, sub_x_min, sub_x_max, regex_pattern=r".*?(\d+)\.wave"):
    """
    Загружает базисные функции из файлов в указанной директории и обрезает их до заданной области.
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
    for index in tqdm(sorted(basis_files.keys()), desc=f"Загрузка базиса из {basis_directory}"):
        data = np.loadtxt(basis_files[index])
        cropped = data[sub_y_min:sub_y_max, sub_x_min:sub_x_max]
        loaded_bases.append(cropped)
    return np.stack(loaded_bases, axis=0)

def plot_from_files(basises, wave_name, bath, config_path, root_folder, x, y):
    """
    Загружает данные с использованием заданных параметров и строит график сравнения исходной волны и
    усреднённой реконструкции в точке (x, y).

    Параметры:
      basises (list[str]): список имен базисов.
      wave_name (str): имя волны.
      bath (str): имя bath.
      config_path (str): путь к файлу конфигурации (zones.json).
      root_folder (str): корневая папка с данными.
      x, y (int): индексы в коэффициентной сетке, для которых вычисляется реконструкция.
    """
    # Загрузка конфигурации
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Не удалось загрузить конфигурацию {config_path}: {e}")
        return

    size = config["size"]
    subduction_zone = config["subduction_zone"]
    sub_y_min, sub_y_max, sub_x_min, sub_x_max = subduction_zone

    # Загрузка волны
    wave_path = os.path.join(root_folder, "waves", f"{wave_name}.wave")
    try:
        data = np.loadtxt(wave_path)
    except Exception as e:
        print(f"Не удалось загрузить волну {wave_path}: {e}")
        return
    wave = data[sub_y_min:sub_y_max, sub_x_min:sub_x_max]

    reconstruction_list = []
    for bn in basises:
        # Загрузка базисных функций
        basis_directory_bn = os.path.join(root_folder, "basises", bn)
        try:
            basis_array = load_basis(basis_directory_bn, sub_y_min, sub_y_max, sub_x_min, sub_x_max)
        except Exception as e:
            print(f"Ошибка при загрузке базиса из {basis_directory_bn}: {e}")
            continue

        # Формирование пути для коэффициентов согласно новым параметрам
        coefs_path = rf"E:\tsunami_res_dir\coefs_nessesary\case_statistics_hd_y_gaus_single_1_real_{bn}_{bath}_last.json"
        try:
            coefs, _ = load_json_data(coefs_path)
        except Exception as e:
            print(f"Не удалось загрузить коэффициенты {coefs_path}: {e}")
            continue

        # Извлечение коэффициентов для точки (x, y)
        try:
            coef = coefs[x, y, :]
        except Exception as e:
            print(f"Ошибка при извлечении коэффициентов для точки ({x}, {y}) из {coefs_path}: {e}")
            continue

        # Вычисление реконструкции через tensordot
        try:
            recon = np.tensordot(coef, basis_array, axes=([0], [0]))
        except Exception as e:
            print(f"Ошибка при вычислении реконструкции для базиса {bn}: {e}")
            continue

        reconstruction_list.append(recon)

    if not reconstruction_list:
        print("Не удалось получить реконструкции ни по одному базису.")
        return

    # Усреднение реконструкций
    reconstruction_avg = average_reconstructions(reconstruction_list)

    # Построение 3D-графика с использованием plotly
    fig = go.Figure()

    fig.add_trace(
        go.Surface(
            z=wave,
            name="Исходная волна",
            colorscale='Viridis',
            opacity=0.99,
            showscale=False
        )
    )

    fig.add_trace(
        go.Surface(
            z=reconstruction_avg,
            name="Средняя реконструкция",
            colorscale='Cividis',
            opacity=0.99,
            showscale=False
        )
    )

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

# Пример вызова с требуемыми параметрами:
if __name__ == "__main__":
    basises = [
        "basis_10",
        "basis_15",
        "basis_18",
        "basis_24",
        "basis_30",
    ]
    wave_name = "gaus_single_1_real"
    bath = "parabola_sine_200_2000"
    config_path = os.path.join("../..", "config", "zones.json")
    root_folder = r"E:\tsunami_res_dir\n_accurate_set"
    x = 400
    y = 400

    plot_from_files(basises, wave_name, bath, config_path, root_folder, x, y)
