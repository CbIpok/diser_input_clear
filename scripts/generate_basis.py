#!/usr/bin/env python3
import argparse
import os
import numpy as np
from src.basis_generator import BasisGenerator


def save_array(data, path):
    """Сохраняет 2D массив в текстовый файл с фиксированным форматом."""
    np.savetxt(path, data, fmt='%.6f')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Генерация базисных функций для субдукционной зоны')
    parser.add_argument('--tile-height', type=int, required=True, help='Высота плитки (в пикселях)')
    parser.add_argument('--tile-width', type=int, required=True, help='Ширина плитки (в пикселях)')
    parser.add_argument('--output-dir', type=str, required=True, help='Директория для сохранения базисных функций')
    parser.add_argument('--value', type=float, default=1.0,
                        help='Значение, которым заполняется выбранная плитка (по умолчанию 1.0)')

    args = parser.parse_args()

    # Создаем выходную директорию, если её нет
    os.makedirs(args.output_dir, exist_ok=True)

    generator = BasisGenerator()
    # Генерация плиток по заданным размерам
    tiles = generator.generate_tiles(tile_height=args.tile_height, tile_width=args.tile_width)

    # Визуализация разбиения subduction_zone на плитки
    generator.visualize_tiles()

    # Генерация и сохранение базисных функций для каждой плитки
    for i in range(len(tiles)):
        basis = generator.generate_basis(tile_index=i, value=args.value)
        output_file = os.path.join(args.output_dir, f'basis_{i}.txt')
        save_array(basis, output_file)
        print(f'Базисная функция для плитки {i} сохранена в: {output_file}')
