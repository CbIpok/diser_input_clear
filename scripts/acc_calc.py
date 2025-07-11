import argparse
import os.path

from src.calc_total_acc import TotalAccuracy
from utils import plot_arrays, save_array

basises = [
    "basis_6",
    "basis_8",
    "basis_9",
    "basis_10",
    "basis_12",
    "basis_15",
    "basis_16",
    "basis_18",
    "basis_20",
    "basis_24",
    "basis_25",
    "basis_30",
    "basis_36",
    "basis_40",
    "basis_48"
]

waves = [
    "async_gaus_double_0.5_0.75",
    "async_gaus_double_0.75_0.5",
    "async_gaus_single_1_real",
    "async_gaus_single_2",
]

# Настраиваем парсер аргументов командной строки
parser = argparse.ArgumentParser(description="Запуск расчёта точности для выбранного bath и набора базисов.")
parser.add_argument("--bath", required=True, help="Имя набора bath (например, parabola_200_2000)")
args = parser.parse_args()

bath = args.bath

for wave in waves:
    for basis in basises:
        print(f"working {os.path.join("..","data","res_real",bath,wave,basis)}")
        if (os.path.exists(os.path.join("..","data","res_real",bath,wave,basis))):
            print("skipped")
            continue
        calculator = TotalAccuracy(r"E:\tsunami_res_dir\n_accurate_set", bath, basis,wave)
        accuracy_dict = calculator.get_accuracy()
        aprox_error = calculator.errors
        save_array(aprox_error, f"aprox_error_{bath}_{basis}_check.txt")
        for key, value in accuracy_dict.items():
            save_array(value,os.path.join("..","data","res_real",bath,wave,basis,f"{key}.txt"))