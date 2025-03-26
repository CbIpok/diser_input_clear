import argparse
import os.path

from plot_mean import PlotMeanForm
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
    # "basis_48"
]

waves = [
    # "gaus_double_1_2",
    # "gaus_double_2_1",
    "gaus_single_2"
]

calculator = PlotMeanForm(r"E:\tsunami_res_dir\n_accurate_set", "parabola_sine_200_2000", basises,waves[0])
calculator.plot(20,150)