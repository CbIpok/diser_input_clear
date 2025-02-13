import json
import os

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_zones(config):
    """
    Отображает всю область и выделяет зоны на ней.

    Параметры:
      config: dict с ключами:
        - "size": [height, width] — размеры области
        - "subduction_zone": [y_min, y_max, x_min, x_max] — координаты субдукционной зоны
        - "mariogramm_zone": [y_min, y_max, x_min, x_max] — координаты зоны мариграммы
    """
    size = config["size"]
    subduction = config["subduction_zone"]
    mariogramm = config["mariogramm_zone"]

    fig, ax = plt.subplots(figsize=(8, 6))

    # Отображаем общую область
    overall_rect = patches.Rectangle(
        (0, 0), size[1], size[0],
        linewidth=1, edgecolor='black', facecolor='none'
    )
    ax.add_patch(overall_rect)

    # Отображаем субдукционную зону (красным)
    subduction_rect = patches.Rectangle(
        (subduction[2], subduction[0]),
        subduction[3] - subduction[2],
        subduction[1] - subduction[0],
        linewidth=2, edgecolor='red', facecolor='none', label='Subduction Zone'
    )
    ax.add_patch(subduction_rect)

    # Отображаем зону мариграммы (синим)
    mariogramm_rect = patches.Rectangle(
        (mariogramm[2], mariogramm[0]),
        mariogramm[3] - mariogramm[2],
        mariogramm[1] - mariogramm[0],
        linewidth=2, edgecolor='blue', facecolor='none', label='Mariogramm Zone'
    )
    ax.add_patch(mariogramm_rect)

    # Настройка осей
    ax.set_xlim(-10, size[1] + 10)
    ax.set_ylim(size[0] + 10, -10)  # инвертируем ось Y для удобства отображения
    ax.set_title("Область и зоны")
    ax.legend()
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()

# Пример для самостоятельного тестирования:
if __name__ == "__main__":
    # Пример конфигурации (можно заменить на загрузку из json)
    config_path = os.path.join("..", "config", "zones.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    plot_zones(config)
