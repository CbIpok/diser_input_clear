import os
import json
import numpy as np
import matplotlib.pyplot as plt


class SubductionGenerator:
    def __init__(self):
        """
        Инициализация генератора субдукционной зоны.
        Конфигурация загружается напрямую из файла config/zones.json.
        Ожидается, что zones.json содержит:
            "size": [height, width]
            "subduction_zone": [y_min, y_max, x_min, x_max]
        """
        config_path = os.path.join("config", "zones.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.height, self.width = config["size"]
        self.sub_y_min, self.sub_y_max, self.sub_x_min, self.sub_x_max = config["subduction_zone"]

    def gaussian(self, amplitude=1.0, sigma=50.0):
        """
        Генерирует 2D массив размера size, где за пределами subduction_zone значения равны 0,
        а внутри subduction_zone расположена гауссова функция с центром в центре этой области.

        Параметры:
          amplitude - максимальное значение гаусса;
          sigma - параметр стандартного отклонения.
        """
        result = np.zeros((self.height, self.width), dtype=float)

        # Определяем диапазоны индексов для subduction_zone
        y_indices = np.arange(self.sub_y_min, self.sub_y_max)
        x_indices = np.arange(self.sub_x_min, self.sub_x_max)
        if y_indices.size == 0 or x_indices.size == 0:
            return result

        # Создаем сетку для subduction_zone
        X, Y = np.meshgrid(x_indices, y_indices)
        center_x = (self.sub_x_min + self.sub_x_max) / 2.0
        center_y = (self.sub_y_min + self.sub_y_max) / 2.0

        # Вычисляем гауссову функцию
        gauss = amplitude * np.exp(-(((X - center_x) ** 2 + (Y - center_y) ** 2) / (2 * sigma ** 2)))
        result[self.sub_y_min:self.sub_y_max, self.sub_x_min:self.sub_x_max] = gauss
        return result

    def double_gaussian(self, sigma=50.0, amplitude1=1.0, amplitude2=1.0):
        """
        Генерирует 2D массив размера size, где за пределами subduction_zone значения равны 0.
        Внутри subduction_zone функция задается двумя гауссовыми распределениями,
        разделенными вертикально (по оси y): верхняя половина получает гаусс с амплитудой amplitude1,
        а нижняя – с амплитудой amplitude2.

        Параметры:
          sigma - параметр стандартного отклонения для обеих гауссовых функций;
          amplitude1 - амплитуда для верхней половины subduction_zone;
          amplitude2 - амплитуда для нижней половины subduction_zone.
        """
        result = np.zeros((self.height, self.width), dtype=float)

        # Границы subduction_zone
        y_min = self.sub_y_min
        y_max = self.sub_y_max
        x_min = self.sub_x_min
        x_max = self.sub_x_max

        if y_max <= y_min or x_max <= x_min:
            return result

        # Вычисляем разделение области по вертикали (по y)
        mid = (y_min + y_max) // 2

        cols = np.arange(x_min, x_max)
        center_x = (x_min + x_max) / 2.0

        # Верхняя половина
        top_rows = np.arange(y_min, mid)
        if top_rows.size > 0 and cols.size > 0:
            X_top, Y_top = np.meshgrid(cols, top_rows)
            center_y_top = (y_min + mid) / 2.0
            top_gauss = amplitude1 * np.exp(
                -(((X_top - center_x) ** 2 + (Y_top - center_y_top) ** 2) / (2 * sigma ** 2)))
            result[y_min:mid, x_min:x_max] = top_gauss

        # Нижняя половина
        bottom_rows = np.arange(mid, y_max)
        if bottom_rows.size > 0 and cols.size > 0:
            X_bottom, Y_bottom = np.meshgrid(cols, bottom_rows)
            center_y_bottom = (mid + y_max) / 2.0
            bottom_gauss = amplitude2 * np.exp(
                -(((X_bottom - center_x) ** 2 + (Y_bottom - center_y_bottom) ** 2) / (2 * sigma ** 2)))
            result[mid:y_max, x_min:x_max] = bottom_gauss

        return result


# Пример для самостоятельного тестирования с визуализацией:
if __name__ == "__main__":
    generator = SubductionGenerator()

    gauss_data = generator.gaussian(amplitude=1.0, sigma=50.0)
    double_gauss_data = generator.double_gaussian(sigma=50.0, amplitude1=1.0, amplitude2=2.5)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    im0 = axes[0].imshow(gauss_data, cmap='viridis')
    axes[0].set_title("Gaussian in subduction zone")
    plt.colorbar(im0, ax=axes[0])

    im1 = axes[1].imshow(double_gauss_data, cmap='viridis')
    axes[1].set_title("Double Gaussian (Amp1=1.0, Amp2=2.5)")
    plt.colorbar(im1, ax=axes[1])

    plt.tight_layout()
    plt.show()
