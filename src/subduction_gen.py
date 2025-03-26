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

    def gaussian(self, amplitude=1.0, sigma_x=50.0, sigma_y=50.0):
        """
        Генерирует 2D массив размера size, где за пределами subduction_zone значения равны 0,
        а внутри subduction_zone расположена гауссова функция с центром в центре этой области.
        Используются отдельные параметры sigma_x и sigma_y для осей x и y.

        Формула:
          f(x,y) = amplitude * exp(-(((x - cx)^2/(2*sigma_x^2)) + ((y - cy)^2/(2*sigma_y^2))))

        Параметры:
          amplitude - максимальное значение гаусса;
          sigma_x - параметр стандартного отклонения по оси x;
          sigma_y - параметр стандартного отклонения по оси y.
        """
        result = np.zeros((self.height, self.width), dtype=float)

        # Диапазоны индексов для subduction_zone
        y_indices = np.arange(self.sub_y_min, self.sub_y_max)
        x_indices = np.arange(self.sub_x_min, self.sub_x_max)
        if y_indices.size == 0 or x_indices.size == 0:
            return result

        # Создаем сетку
        X, Y = np.meshgrid(x_indices, y_indices)
        center_x = (self.sub_x_min + self.sub_x_max) / 2.0
        center_y = (self.sub_y_min + self.sub_y_max) / 2.0

        gauss = amplitude * np.exp(-(((X - center_x) ** 2 / (2 * sigma_x ** 2)) +
                                     ((Y - center_y) ** 2 / (2 * sigma_y ** 2))))
        result[self.sub_y_min:self.sub_y_max, self.sub_x_min:self.sub_x_max] = gauss
        return result

    def double_gaussian(self, sigma_x=50.0, sigma_y=50.0, amplitude1=1.0, amplitude2=1.0):
        """
        Генерирует 2D массив размера size, где за пределами subduction_zone значения равны 0.
        Внутри subduction_zone вычисляются две гауссовы функции по всему региону:
          - Первая с амплитудой amplitude1;
          - Вторая с амплитудой amplitude2.
        Центры гауссов по оси x совпадают (находятся в центре субдукционной зоны),
        а по оси y они сдвинуты относительно центральной линии субдукционной зоны на L/8,
        где L – высота субдукционной зоны. Таким образом, расстояние между центрами равно L/4.

        Формула:
          f(x,y) = amplitude1 * exp(-(((x - cx)^2/(2*sigma_x^2)) + ((y - (cy - L/8))^2/(2*sigma_y^2))))
                   + amplitude2 * exp(-(((x - cx)^2/(2*sigma_x^2)) + ((y - (cy + L/8))^2/(2*sigma_y^2))))

        Параметры:
          sigma_x - параметр стандартного отклонения по оси x для обеих гауссовых функций;
          sigma_y - параметр стандартного отклонения по оси y для обеих гауссовых функций;
          amplitude1 - амплитуда для верхнего гауссова распределения;
          amplitude2 - амплитуда для нижнего гауссова распределения.
        """
        result = np.zeros((self.height, self.width), dtype=float)

        y_min = self.sub_y_min
        y_max = self.sub_y_max
        x_min = self.sub_x_min
        x_max = self.sub_x_max

        if y_max <= y_min or x_max <= x_min:
            return result

        # Создаем сетку для области subduction_zone
        y_indices = np.arange(y_min, y_max)
        x_indices = np.arange(x_min, x_max)
        X, Y = np.meshgrid(x_indices, y_indices)
        center_x = (x_min + x_max) / 2.0

        # Высота субдукционной зоны
        L = y_max - y_min
        cy = (y_min + y_max) / 2.0

        # Сдвигаем центры гауссов по оси y: верхний на L/8 вверх, нижний на L/8 вниз от центра
        center_y_top = cy + L / 3.0
        center_y_bottom = cy - L / 3.0

        top_gauss = amplitude1 * np.exp(-(((X - center_x) ** 2 / (2 * sigma_x ** 2)) +
                                          ((Y - center_y_top) ** 2 / (2 * sigma_y ** 2))))
        bottom_gauss = amplitude2 * np.exp(-(((X - center_x) ** 2 / (2 * sigma_x ** 2)) +
                                             ((Y - center_y_bottom) ** 2 / (2 * sigma_y ** 2))))
        double_gauss = top_gauss + bottom_gauss
        result[y_min:y_max, x_min:x_max] = double_gauss

        # Вывод формулы поверхности внутри функции
        print("Формула поверхности f(x,y) для double_gaussian:")
        print(
            "f(x,y) = {} * exp(-(((x - {:.2f})^2/(2*{:.2f}^2)) + ((y - ({:.2f}))^2/(2*{:.2f}^2))) ) + {} * exp(-(((x - {:.2f})^2/(2*{:.2f}^2)) + ((y - ({:.2f}))^2/(2*{:.2f}^2))) )".format(
                amplitude1, center_x, sigma_x, center_y_top, sigma_y,
                amplitude2, center_x, sigma_x, center_y_bottom, sigma_y))
        return result


# Пример для самостоятельного тестирования с визуализацией:
if __name__ == "__main__":
    generator = SubductionGenerator()

    gauss_data = generator.gaussian(amplitude=1.0, sigma_x=50.0, sigma_y=50.0)
    double_gauss_data = generator.double_gaussian(sigma_x=50.0, sigma_y=50.0,
                                                  amplitude1=1.0, amplitude2=2.5)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    im0 = axes[0].imshow(gauss_data, cmap='viridis')
    axes[0].set_title("Gaussian in subduction zone")
    plt.colorbar(im0, ax=axes[0])

    im1 = axes[1].imshow(double_gauss_data, cmap='viridis')
    axes[1].set_title("Double Gaussian (Amp1=1.0, Amp2=2.5)")
    plt.colorbar(im1, ax=axes[1])

    plt.tight_layout()
    plt.show()
