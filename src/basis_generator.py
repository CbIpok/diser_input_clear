import os
import json
import re

import numpy as np
import matplotlib.pyplot as plt


class BasisGenerator:
    def __init__(self):
        """
        Инициализация генератора базисных функций.
        Загружает конфигурацию напрямую из файла config/zones.json.
        Ожидается, что zones.json содержит:
            "size": [height, width]
            "subduction_zone": [y_min, y_max, x_min, x_max]
        """
        config_path = os.path.join("config", "zones.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.size = config["size"]
        self.height, self.width = self.size
        self.subduction_zone = config["subduction_zone"]
        self.sub_y_min, self.sub_y_max, self.sub_x_min, self.sub_x_max = self.subduction_zone
        self.tiles = []  # Список плиток (каждая плитка – кортеж (y_min, y_max, x_min, x_max))

    def generate_tiles(self, tile_height, tile_width):
        """
        Разбивает область subduction_zone на плитки заданного размера.

        Параметры:
          tile_height - высота плитки (в пикселях)
          tile_width  - ширина плитки (в пикселях)

        Требуется, чтобы высота subduction_zone делилась на tile_height, а ширина — на tile_width.
        Возвращает список плиток, упорядоченных по строкам (сначала верхние, затем нижние).
        """
        zone_height = self.sub_y_max - self.sub_y_min
        zone_width = self.sub_x_max - self.sub_x_min
        assert zone_height % tile_height == 0, "Высота subduction_zone должна делиться на tile_height"
        assert zone_width % tile_width == 0, "Ширина subduction_zone должна делиться на tile_width"

        n_tiles_y = zone_height // tile_height
        n_tiles_x = zone_width // tile_width
        self.tiles = []

        for i in range(n_tiles_y):
            for j in range(n_tiles_x):
                tile_y_min = self.sub_y_min + i * tile_height
                tile_y_max = tile_y_min + tile_height
                tile_x_min = self.sub_x_min + j * tile_width
                tile_x_max = tile_x_min + tile_width
                self.tiles.append((tile_y_min, tile_y_max, tile_x_min, tile_x_max))
        return self.tiles

    def generate_basis(self, tile_index, value=1.0):
        """
        Генерирует 2D массив (размера size), заполненный нулями, за исключением одного прямоугольника,
        соответствующего плитке с индексом tile_index, где значения устанавливаются равными value.

        Параметры:
          tile_index - индекс плитки из ранее сгенерированного списка tiles;
          value      - значение, которое будет записано внутри выбранной плитки (по умолчанию 1.0).
        """
        if not self.tiles:
            raise ValueError("Плитки не сгенерированы. Сначала вызовите generate_tiles().")
        if tile_index < 0 or tile_index >= len(self.tiles):
            raise ValueError("Неверный индекс плитки.")

        basis = np.zeros((self.height, self.width), dtype=float)
        y_min, y_max, x_min, x_max = self.tiles[tile_index]
        basis[y_min:y_max, x_min:x_max] = value
        return basis

    def visualize_tiles(self):
        """
        Отображает область subduction_zone и нарисованные по ней плитки.
        Каждая плитка обозначена синей рамкой, а вся subduction_zone – красной.
        """
        if not self.tiles:
            raise ValueError("Плитки не сгенерированы. Сначала вызовите generate_tiles().")

        import matplotlib.patches as patches

        fig, ax = plt.subplots(figsize=(8, 6))
        # Рисуем всю область subduction_zone
        sub_rect = patches.Rectangle(
            (self.sub_x_min, self.sub_y_min),
            self.sub_x_max - self.sub_x_min,
            self.sub_y_max - self.sub_y_min,
            linewidth=2, edgecolor='red', facecolor='none', label="Subduction Zone"
        )
        ax.add_patch(sub_rect)

        # Рисуем плитки
        for tile in self.tiles:
            y_min, y_max, x_min, x_max = tile
            tile_width = x_max - x_min
            tile_height = y_max - y_min
            tile_rect = patches.Rectangle(
                (x_min, y_min),
                tile_width, tile_height,
                linewidth=1, edgecolor='blue', facecolor='none'
            )
            ax.add_patch(tile_rect)

        ax.set_xlim(0, self.width)
        ax.set_ylim(self.height, 0)  # инвертируем ось Y для соответствия координатам
        ax.set_title("Разбиение subduction_zone на плитки")
        ax.legend()
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.show()

    def display_all_basis_interactive(self, value=1.0):
        """
        Отображает все базисные функции для каждой плитки в интерактивном режиме.
        При запуске отображается базисная функция для плитки 0.
        Для навигации используйте клавиши "←" и "→".
        """
        if not self.tiles:
            raise ValueError("Плитки не сгенерированы. Сначала вызовите generate_tiles().")

        current_index = 0
        fig, ax = plt.subplots(figsize=(3, 2))
        basis = self.generate_basis(tile_index=current_index, value=value)
        im = ax.imshow(basis, cmap='viridis')
        title = ax.set_title(f"Базисная функция для плитки {current_index}")
        plt.colorbar(im, ax=ax)

        def on_key(event):
            nonlocal current_index
            if event.key == 'right':
                current_index = (current_index + 1) % len(self.tiles)
            elif event.key == 'left':
                current_index = (current_index - 1) % len(self.tiles)
            else:
                return
            basis_new = self.generate_basis(tile_index=current_index, value=value)
            im.set_data(basis_new)
            title.set_text(f"Базисная функция для плитки {current_index}")
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect('key_press_event', on_key)
        plt.show()



# Пример для самостоятельного тестирования:
if __name__ == "__main__":
    generator = BasisGenerator()
    # Убедитесь, что размеры subduction_zone делятся на выбранные tile_height и tile_width.
    generator.generate_tiles(tile_height=40, tile_width=80)
    # Визуализируем разбиение плиток
    generator.visualize_tiles()
    # Отображаем интерактивное переключение базисных функций
    generator.display_all_basis_interactive(value=1.0)
