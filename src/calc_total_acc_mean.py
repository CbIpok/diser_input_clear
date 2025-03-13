import json
import os
import re
import numpy as np
from tqdm import tqdm  # Импорт tqdm для отображения прогресса


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


class TotalAccuracyMean:
    def __init__(self, root_folder, bath_name, basis_names, wave_name):
        """
        Параметры:
          root_folder - корневая папка с данными;
          bath_name - имя bath;
          basis_names - список имён базисов (например, ['basis1', 'basis2', ...]);
          wave_name - имя волны.
        """
        self.root_folder = root_folder
        self.bath_name = bath_name
        self.basis_names = basis_names  # теперь список basis_names
        self.wave_name = wave_name

        # Загружаем конфигурацию зоны из файла zones.json
        config_path = os.path.join("..", "config", "zones.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.size = config["size"]
        self.height, self.width = self.size
        self.subduction_zone = config["subduction_zone"]
        self.sub_y_min, self.sub_y_max, self.sub_x_min, self.sub_x_max = self.subduction_zone

        # Загружаем волну
        self.wave_path = os.path.join(root_folder, "waves", f"{wave_name}.wave")
        self.wave = self._load_wave()

        # Для каждого basis_name загружаем базисные функции и коэффициенты
        self.basis = {}   # ключ: basis_name, значение: np.array базисов (n_layers, H, W)
        self.coefs = {}   # ключ: basis_name, значение: коэффициенты (rows, cols, n_layers)
        self.errors = {}  # ключ: basis_name, значение: ошибки (rows, cols)
        for bn in basis_names:
            basis_directory = os.path.join(root_folder, "basises", bn)
            self.basis[bn] = self._load_basis(basis_directory)
            coefs_path = os.path.join(
                root_folder,
                "coeffs",
                f"case_statistics_{wave_name}_{bn}_{bath_name}_all.json"
            )
            self.coefs[bn], self.errors[bn] = load_json_data(coefs_path)

    def _load_basis(self, basis_directory, regex_pattern=r".*?(\d+)\.wave"):
        """
        Загружает базисные функции из файлов в заданной директории.
        Имена файлов должны соответствовать шаблону regex_pattern для извлечения индекса.
        Каждая функция обрезается до области subduction_zone.
        Возвращает массив базисных функций с формой (n_layers, H, W).
        """
        files = os.listdir(basis_directory)
        basis_files = {}

        # Фильтрация файлов по регулярному выражению и извлечение индекса
        for filename in files:
            match = re.search(regex_pattern, filename)
            if match:
                index = int(match.group(1))
                full_path = os.path.join(basis_directory, filename)
                basis_files[index] = full_path

        loaded_bases = []
        for index in sorted(basis_files.keys()):
            data = np.loadtxt(basis_files[index])
            cropped = data[self.sub_y_min:self.sub_y_max, self.sub_x_min:self.sub_x_max]
            loaded_bases.append(cropped)
        return np.stack(loaded_bases, axis=0)

    def _load_wave(self):
        """
        Загружает волну из файла self.wave_path и обрезает её до области subduction_zone.
        """
        data = np.loadtxt(self.wave_path)
        wave = data[self.sub_y_min:self.sub_y_max, self.sub_x_min:self.sub_x_max]
        return wave

    def get_accuracy(self, chunk_size=20):
        """
        Вычисляет нормированные показатели аппроксимации для каждой точки.
        Реконструкция для каждого чанка вычисляется как среднее арифметическое реконструкций,
        полученных для каждого basis_name.
        """
        # Берем размеры коэффициентов из первого загруженного набора
        first_key = next(iter(self.coefs))
        rows, cols, _ = self.coefs[first_key].shape

        rms_accuracy = np.empty((rows, cols))
        max_accuracy = np.empty((rows, cols))
        max_value_diff = np.empty((rows, cols))
        # Вычисляем RMS и максимальное значение волны
        wave_rms = np.sqrt(np.mean(self.wave ** 2))
        wave_max = np.max(np.abs(self.wave))

        # Обработка строк коэффициентной сетки чанками
        for i in tqdm(range(0, rows, chunk_size), desc="Вычисление точности"):
            end = min(i + chunk_size, rows)
            reconstruction_list = []
            # Для каждого basis_name вычисляем реконструкцию
            for bn in self.basis_names:
                basis_stack = self.basis[bn]  # shape (n_layers, H, W)
                coefs_chunk = self.coefs[bn][i:end, :, :]  # shape (chunk, cols, n_layers)
                reconstruction_bn = np.tensordot(coefs_chunk, basis_stack, axes=([2], [0]))
                reconstruction_list.append(reconstruction_bn)
            # Вызываем отдельную функцию для усреднения реконструкций,
            # передавая в неё также имя базисной функции (пока не используется)
            reconstruction_chunk = average_reconstructions(reconstruction_list, bn)

            # Вычисляем разницу между волной и реконструкцией
            diff_chunk = self.wave - reconstruction_chunk  # broadcasting: (chunk, cols, H, W)
            # Нормированное RMS отклонение для каждой точки
            rms_accuracy[i:end, :] = np.sqrt(np.mean(diff_chunk ** 2, axis=(2, 3))) / wave_rms
            # Нормированное максимальное отклонение для каждой точки
            max_accuracy[i:end, :] = np.max(np.abs(diff_chunk), axis=(2, 3)) / wave_max
            # Дополнительный показатель: нормированная разница между максимальным значением реконструкции и wave_max
            max_reconstructed_chunk = np.max(np.abs(reconstruction_chunk), axis=(2, 3))
            max_value_diff[i:end, :] = np.abs(max_reconstructed_chunk - wave_max) / wave_max

        return {
            "rms_accuracy": rms_accuracy,
            "max_accuracy": max_accuracy,
            "max_value_diff": max_value_diff
        }
