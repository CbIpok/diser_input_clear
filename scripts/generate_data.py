#!/usr/bin/env python3
import argparse
import numpy as np
from src.data_generator import ShapeGenerator


def save_array(data, path):
    """Сохраняет 2D массив в текстовый файл с плавающей точкой."""
    np.savetxt(path, data, fmt='%.6f')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Генерация 2D данных по заданной форме')
    parser.add_argument('--form', type=str, required=True,
                        choices=['gradient_x', 'gradient_y', 'parabola', 'parabola_sine'],
                        help="Выбор формы: gradient_x, gradient_y, parabola, parabola_sine")
    parser.add_argument('--output', type=str, required=True,
                        help="Путь для сохранения сгенерированного 2D массива")
    parser.add_argument('--min_value', type=float, default=0.0,
                        help="Минимальное значение (для градиентов и параболы)")
    parser.add_argument('--max_value', type=float, default=1.0,
                        help="Максимальное значение (для градиентов и параболы)")
    parser.add_argument('--sin_amp', type=float, default=0.5,
                        help="Амплитуда синусоидальной модуляции (только для параболы с синусом)")
    parser.add_argument('--sin_period_x', type=int, default=50,
                        help="Период синуса по оси X (только для параболы с синусом)")
    parser.add_argument('--sin_period_y', type=int, default=50,
                        help="Период синуса по оси Y (только для параболы с синусом)")

    args = parser.parse_args()

    generator = ShapeGenerator()
    data = None

    if args.form == 'gradient_x':
        data = generator.gradient_x(min_value=args.min_value, max_value=args.max_value)
    elif args.form == 'gradient_y':
        data = generator.gradient_y(min_value=args.min_value, max_value=args.max_value)
    elif args.form == 'parabola':
        data = generator.parabola(min_value=args.min_value, max_value=args.max_value)
    elif args.form == 'parabola_sine':
        data = generator.parabola_sine(min_value=args.min_value, max_value=args.max_value,
                                       sin_amp=args.sin_amp, sin_period_x=args.sin_period_x,
                                       sin_period_y=args.sin_period_y)

    if data is not None:
        save_array(data, args.output)
        print(f"Сгенерированные данные сохранены в: {args.output}")
