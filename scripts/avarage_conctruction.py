import json
import os
import re
import numpy as np
from tqdm import tqdm

from scripts.utils import save_array


def average_reconstructions(reconstruction_list, basis_name):
    """
    Вычисляет среднее арифметическое реконструкций.

    Параметры:
      reconstruction_list: список numpy-массивов реконструкций.
      basis_name: имя базисной функции (пока не используется).

    Возвращает:
      Среднюю реконструкцию как numpy-массив.
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
    Загружает базисные функции из файлов в заданной директории.
    Файлы выбираются по регулярному выражению, извлекающему индекс.
    Каждая функция обрезается до области, заданной параметрами sub_y_min, sub_y_max, sub_x_min, sub_x_max.

    Параметры:
      basis_directory: путь к директории с файлами базисов.
      sub_y_min, sub_y_max, sub_x_min, sub_x_max: границы обрезки.
      regex_pattern: шаблон для извлечения индекса из имени файла.

    Возвращает:
      numpy-массив базисных функций с формой (n_layers, H, W).
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
    return np.stack(loaded_bases, axis=0)


def get_accuracy(wave_path, config_path, basis_dirs, coef_paths, chunk_size=20, regex_pattern=r".*?(\d+)\.wave"):
    """
    Вычисляет нормированные показатели аппроксимации для каждой точки.

    Функция загружает:
      - волну из файла wave_path и обрезает её до области, указанной в config_path (файл zones.json);
      - базисные функции для каждого базиса из переданных директорий (basis_dirs);
      - коэффициенты и ошибки из JSON-файлов (coef_paths).

    На основе этих данных вычисляется реконструкция волны по каждому базису,
    затем выполняется их усреднение, и рассчитываются следующие метрики:
      - rms_accuracy: нормированное RMS отклонение,
      - max_accuracy: нормированное максимальное отклонение,
      - max_value_diff: нормированная разница между максимальным значением реконструкции и волны.

    Параметры:
      wave_path: путь к файлу волны (.wave).
      config_path: путь к файлу конфигурации zones.json.
      basis_dirs: словарь, где ключи — имена базисов, а значения — пути к директориям с файлами базисов.
      coef_paths: словарь, где ключи — имена базисов, а значения — пути к JSON-файлам с коэффициентами.
      chunk_size: размер чанка для обработки строк коэффициентной сетки.
      regex_pattern: регулярное выражение для выбора файлов базисов.

    Возвращает:
      Словарь с ключами:
         "rms_accuracy": нормированное RMS отклонение,
         "max_accuracy": нормированное максимальное отклонение,
         "max_value_diff": нормированная разница между максимальным значением реконструкции и максимальным значением волны.
    """
    # Загружаем конфигурацию зоны
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    subduction_zone = config["subduction_zone"]
    sub_y_min, sub_y_max, sub_x_min, sub_x_max = subduction_zone

    # Загружаем волну и обрезаем её до области subduction_zone
    wave_data = np.loadtxt(wave_path)
    wave = wave_data[sub_y_min:sub_y_max, sub_x_min:sub_x_max]

    # Загружаем базисные функции для каждого базиса
    basis = {}
    for bn, basis_directory in basis_dirs.items():
        basis[bn] = load_basis(basis_directory, sub_y_min, sub_y_max, sub_x_min, sub_x_max, regex_pattern)

    # Загружаем коэффициенты и ошибки для каждого базиса
    coefs = {}
    errors = {}
    for bn, coef_path in coef_paths.items():
        coefs[bn], errors[bn] = load_json_data(coef_path)

    # Получаем размеры коэффициентной сетки (предполагаем, что у всех они одинаковые)
    any_bn = next(iter(coefs))
    rows, cols, _ = coefs[any_bn].shape

    # Вычисляем RMS и максимальное значение волны
    wave_rms = np.sqrt(np.mean(wave ** 2))
    wave_max = np.max(np.abs(wave))

    # Инициализируем массивы для хранения метрик
    rms_accuracy = np.empty((rows, cols))
    max_accuracy = np.empty((rows, cols))
    max_value_diff = np.empty((rows, cols))

    # Обработка коэффициентной сетки чанками
    for i in tqdm(range(0, rows, chunk_size), desc="Вычисление точности"):
        end = min(i + chunk_size, rows)
        reconstruction_list = []
        # Для каждого базиса вычисляем реконструкцию
        for bn in basis_dirs.keys():
            basis_stack = basis[bn]  # форма: (n_layers, H, W)
            coefs_chunk = coefs[bn][i:end, :, :]  # форма: (chunk, cols, n_layers)
            reconstruction_bn = np.tensordot(coefs_chunk, basis_stack, axes=([2], [0]))  # форма: (chunk, cols, H, W)
            reconstruction_list.append(reconstruction_bn)
        # Усредняем реконструкции
        reconstruction_chunk = average_reconstructions(reconstruction_list, bn)

        # Вычисляем разницу между волной и реконструкцией
        diff_chunk = wave - reconstruction_chunk  # волна имеет форму (H, W), происходит broadcasting
        rms_accuracy[i:end, :] = np.sqrt(np.mean(diff_chunk ** 2, axis=(2, 3))) / wave_rms
        max_accuracy[i:end, :] = np.max(np.abs(diff_chunk), axis=(2, 3)) / wave_max
        max_reconstructed_chunk = np.max(np.abs(reconstruction_chunk), axis=(2, 3))
        max_value_diff[i:end, :] = np.abs(max_reconstructed_chunk - wave_max) / wave_max

    return {
        "rms_accuracy": rms_accuracy,
        "max_accuracy": max_accuracy,
        "max_value_diff": max_value_diff
    }
# Список базисов
basises = [
    "basis_10",
    "basis_15",
    "basis_18",
    "basis_24",
    "basis_30",
]

wave_name = "gaus_single_1_real"
bath = "parabola_sine_200_2000"
config_path = os.path.join("..", "config", "zones.json")
root_folder = r"E:\tsunami_res_dir\n_accurate_set"
wave_path = os.path.join(root_folder, "waves", f"{wave_name}.wave")

# Формируем словари с путями к директориям базисов и JSON-файлам коэффициентов
basis_dirs = {}
coef_paths = {}

for basis in basises:
    basis_dirs[basis] = os.path.join(root_folder, "basises", basis)
    coef_paths[basis] = rf"E:\tsunami_res_dir\coefs_nessesary\case_statistics_hd_y_{wave_name}_{basis}_{bath}_last.json"

# Вызов функции get_accuracy с заданными параметрами
accuracy_dict = get_accuracy(wave_path, config_path, basis_dirs, coef_paths, chunk_size=20)
for key, value in accuracy_dict.items():
    save_array(value, os.path.join("..", "data", "res_real_mean", bath, f"{key}.txt"))