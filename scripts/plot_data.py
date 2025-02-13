import argparse
import numpy as np
import matplotlib.pyplot as plt
import os


def main():
    parser = argparse.ArgumentParser(description='Plot generated 2D data')
    parser.add_argument('--input', type=str, help='Путь к входному файлу с 2D массивом (текстовый файл)')
    parser.add_argument('--output', type=str, help='Путь к выходному файлу для сохранения изображения')
    args = parser.parse_args()

    # Если указан входной файл и он существует, загружаем данные, иначе создаем тестовый массив
    if args.input and os.path.exists(args.input):
        data = np.loadtxt(args.input)
    else:
        print("Параметр --input не задан или файл не найден. Используем тестовый 2D массив.")
        # Генерируем тестовый массив (например, линейный градиент)
        height, width = 200, 300
        data = np.linspace(0, 1, height * width).reshape((height, width))

    plt.imshow(data, cmap='viridis')
    plt.colorbar()

    if args.output:
        plt.savefig(args.output)
        print(f"Изображение сохранено в: {args.output}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
