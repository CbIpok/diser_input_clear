bathes = ["parabola_sine_200_2000", "x_200_2000"]
wave = ["gaus_double_0.75_0.5", "gaus_single_1_real","gaus_single_2"]
basis = [
    "basis_6", "basis_8", "basis_9", "basis_10", "basis_12",
    "basis_15", "basis_16", "basis_18", "basis_20", "basis_24",
    "basis_25", "basis_30", "basis_36", "basis_40", "basis_48"
]

l1 = []

# l3 = []
for bath in bathes:
    for i in range(len(wave)):
        for k in range(len(basis)):
            l1.append(f"TsunamiCoefficientsCalculator.exe {bath} {wave[i]} {basis[k]}")




with open("all_necessary.bat", "w", encoding="utf-8") as file:
    for command in l1:
        file.write(command + "\n")

x = 1
while (True):
    x *= x




