import  numpy as np

data = np.loadtxt(r"/data/res_real_mean/parabola_sine_200_2000/rms_accuracy.txt")
np.save(r"/data/res_real_mean/parabola_sine_200_2000/rms.npy", data)