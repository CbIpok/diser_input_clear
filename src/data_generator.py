import os
import json
import numpy as np
import matplotlib.pyplot as plt


class ShapeGenerator:
    def __init__(self):
        """
        Инициализация генератора форм.
        Загружает конфигурацию исключительно из файла config/zones.json.
        """
        config_path = os.path.join("config", "zones.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.height, self.width = config["size"]

    def gradient_x(self, min_value=0.0, max_value=1.0):
        """
        Генерирует 2D массив с линейным градиентом по оси X.

        Параметры:
          min_value: минимальное значение
          max_value: максимальное значение
        """
        x = np.linspace(min_value, max_value, self.width)
        return np.tile(x, (self.height, 1))

    def gradient_y(self, min_value=0.0, max_value=1.0):
        """
        Генерирует 2D массив с линейным градиентом по оси Y.

        Параметры:
          min_value: минимальное значение
          max_value: максимальное значение
        """
        y = np.linspace(min_value, max_value, self.height)[:, None]
        return np.tile(y, (1, self.width))

    def parabola(self, min_value=0.0, max_value=1.0):
        """
        Генерирует 2D параболическую форму, которая константна по x и изменяется только по y.
        Формула:
            f(y) = min_value + (max_value - min_value) * (1 - y_norm**2),
        где y_norm = y / (height - 1) для y ∈ [0, height-1].
        В результате значение при y = 0 будет max_value, а при y = height-1 – min_value.
        """
        y_norm = np.linspace(0, 1, self.height)
        parabolic = 1 - y_norm ** 2
        parabolic_scaled = min_value + (max_value - min_value) * parabolic
        return np.tile(parabolic_scaled[:, None], (1, self.width))

    def parabola_sine(self, min_value=0.0, max_value=1.0, sin_amp=0.5, sin_period_x=50, sin_period_y=50):
        """
        Генерирует 2D форму: базовая парабола (константная по x, максимум при y=0)
        с добавлением синусоидальной модуляции по обеим осям.

        Параметры:
          min_value, max_value: минимальное и максимальное значение базовой параболы
          sin_amp: амплитуда синусоидальной модуляции
          sin_period_x: период синуса по оси X (в пикселях)
          sin_period_y: период синуса по оси Y (в пикселях)
        """
        base = self.parabola(min_value=min_value, max_value=max_value)
        y = np.linspace(0, self.height - 1, self.height)
        x = np.linspace(0, self.width - 1, self.width)
        X, Y = np.meshgrid(x, y)
        modulation = sin_amp * (np.sin(2 * np.pi * X / sin_period_x) * np.sin(2 * np.pi * Y / sin_period_y))
        return base + modulation


# Пример для самостоятельного тестирования с визуализацией:
if __name__ == "__main__":
    generator = ShapeGenerator()

    data_examples = {
        "Gradient X": generator.gradient_x(min_value=0, max_value=5),
        "Gradient Y": generator.gradient_y(min_value=0, max_value=5),
        "Parabola (max at y=0)": generator.parabola(min_value=0, max_value=5),
        "Parabola + Sine": generator.parabola_sine(min_value=0, max_value=5, sin_amp=0.2, sin_period_x=30,
                                                   sin_period_y=60)
    }

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for ax, (title, data) in zip(axes, data_examples.items()):
        im = ax.imshow(data, cmap='viridis')
        ax.set_title(title)
        plt.colorbar(im, ax=ax)

    plt.tight_layout()
    plt.show()
