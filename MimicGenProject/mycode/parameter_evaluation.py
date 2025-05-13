import numpy as np
from scipy.optimize import curve_fit
import os 
import pandas as pd
import sys
import json
import glob
import shutil
import h5py
import matplotlib.pyplot as plt


data_dir = os.path.expanduser("~/MimicGenProject/MimicGenProject/data")
output_csv = os.path.join(data_dir, "Cumulative_Data.csv")
data = pd.read_csv(output_csv)

# Your sigmoid function
def sigmoid(x, L, k, x0):
    return L / (1 + np.exp(-k * (x - x0)))

# Your data
x_data = np.array([...])
y_data = np.array([...])

# Initial parameter guesses
initial_guess = [52, 20, 0.1]  # L, k, x0

params, covariance = curve_fit(sigmoid, x_data, y_data, p0=initial_guess)
L_opt, k_opt, x0_opt = params
