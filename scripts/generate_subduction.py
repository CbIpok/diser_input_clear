#!/usr/bin/env python3
import argparse
import os
import numpy as np
from src.subduction_gen import SubductionGenerator


def save_array(data, path):
    """Сохраняет 2D массив в текстовый файл (значения разделены пробелами, строки – переносами)."""
    np.savetxt(path, data, fmt='%.6f')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Генерация данных для субдукционной зоны')
    parser.add_argument('--form', type=str, required=True,
                        choices=['gaussian', 'double_gaussian'],
                        help='Выбор формы: gaussian или double_gaussian')
    parser.add_argument('--output', type=str, required=True,
                        help='Путь для сохранения сгенерированного 2D массива')
    parser.add_argument('--sigma', type=float, default=50.0,
                        help='Параметр sigma для гауссова распределения (по умолчанию 50.0)')
    # Для формы gaussian используется один параметр амплитуды:
    parser.add_argument('--amplitude', type=float, default=1.0,
                        help='Амплитуда для формы gaussian (по умолчанию 1.0)')
    # Для double_gaussian задаются две амплитуды: для верхней и нижней частей субдукционной зоны:
    parser.add_argument('--amplitude1', type=float, default=1.0,
                        help='Амплитуда для верхней половины (double_gaussian, по умолчанию 1.0)')
    parser.add_argument('--amplitude2', type=float, default=1.0,
                        help='Амплитуда для нижней половины (double_gaussian, по умолчанию 1.0)')

    args = parser.parse_args()

    generator = SubductionGenerator()
    data = None

    if args.form == 'gaussian':
        data = generator.gaussian(amplitude=args.amplitude, sigma=args.sigma)
    elif args.form == 'double_gaussian':
        data = generator.double_gaussian(sigma=args.sigma,
                                         amplitude1=args.amplitude1,
                                         amplitude2=args.amplitude2)

    if data is not None:
        save_array(data, args.output)
        print(f"Сгенерированные данные сохранены в: {args.output}")
