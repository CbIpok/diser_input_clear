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
    "gaus_double_0.5_0.75",
    "gaus_double_0.75_0.5",
    "gaus_single_1_real",
    "gaus_single_2",
]

bathes = [
        "parabola_200_2000",
        "parabola_sine_200_2000",
        "x_200_2000",
        "y_200_2000",
    ]

if __name__ == "__main__":
    config_path = os.path.join("..", "config", "zones.json")
    root_folder = r"E:\tsunami_res_dir\n_accurate_set"
    wave_name = waves[2]
    wave_path = os.path.join(root_folder, "waves", f"{wave_name}.wave")
    basis_index = 0
    for bath in [bathes[1],bathes[2]]:
        for basis in basises:
            basis_directory = os.path.join(root_folder, "basises", basis)
            coefs_path = rf"E:\tsunami_res_dir\coefs_nessesary\case_statistics_hd_y_gaus_single_1_real_{basis}_{bath}_last.json"
            accuracy_dict = TotalAccuracy.get_accuracy_static(config_path,wave_path, basis_directory, coefs_path)
            for key, value in accuracy_dict.items():
                save_array(value, os.path.join("..", "data", "final", bath,basis, f"{key}.txt"))