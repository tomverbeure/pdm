#! /usr/bin/env python3

import numpy as np
import matplotlib
import scipy.signal
from scipy.fftpack import fft, fftfreq

from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import EngFormatter

import os

fs_in   = 48000 * 4
N       = 100000

x = np.linspace(0.0, N/fs_in, N)

freq1 = 5000
freq2 = 8000
freq3 = 20000
freq4 = fs_in/2.5

y1 = 1 * np.sin(2 * np.pi * freq1 * x)
y2 = 1 * np.sin(2 * np.pi * freq2 * x)
y3 = 1 * np.sin(2 * np.pi * freq3 * x)
y4 = 1 * np.sin(2 * np.pi * freq4 * x)

y_in = y1 + y2 + y3 + y4 + np.random.randn(N) * 0.01

y_in_int = np.round(y_in * (2**12))
y_in = y_in_int / (2**12)

def plot_signal(x, y, fs, filename):
    N = len(x)

    w = scipy.signal.blackman(N)
    Y=fft(y * w)
    freqs = fftfreq(N)
    x_mask = freqs >= 0

    plt.figure(figsize=(10,9))
    plt.subplot(2,1,1)

    fig, (plt_y, plt_Y) = plt.subplots(2)

    plt_y.plot(x[0:200], y[0:200])
    plt_y.grid(True)
    plt_y.set_xlim(0, x[200])

    plt_Y.semilogy(freqs[x_mask] * fs, np.abs(Y)[x_mask] * 2 / N)
    plt_Y.grid(True)
    plt_Y.set_xlim(0, fs/2)

    fig.tight_layout()
    fig.savefig(filename)

plot_signal(x, y_in, fs_in, "input.svg")

with open("data_in_sines.txt", "wt+") as data_in_file:
    data_in_file.writelines("%d\n" % v for v in y_in_int)

os.system("./tb -c 41 -d 2 -i %s -o %s" % ("data_in_sines.txt", "data_out_sines.txt"))

decim = 1

y_out = []
with open("data_out_sines.txt", "rt+") as data_out_file:
    y_out = [int(l.strip()) for l in data_out_file.readlines()]

y_out = np.asarray(y_out[len(y_out)-len(y_in)//decim:])
y_out = y_out / (2**12)

print(len(y_out))
print(y_out)

N = len(y_out)

x = np.linspace(0.0, N/(fs_in/decim), N)
plot_signal(x, y_out, fs_in/decim, "output.svg")



