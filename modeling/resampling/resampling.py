#! /usr/bin/env python3

import numpy as np
from matplotlib import pyplot as plt

from scipy import signal
from filter_lib import *

import platform
if platform.system() == "Darwin":
    BLOG_PATH = "/Users/tom/projects/tomverbeure.github.io/assets/pdm/resampling/"
else:
    BLOG_PATH = "/home/tom/projects/tomverbeure.github.io/assets/pdm/resampling/"

def input_signal():
    N=10000

    x = np.linspace(0., 1., N)

    freq1 = 500
    freq2 = 350
    freq3 = 630

    y1 = 1.0 * np.sin(2 * np.pi * freq1 * x)
    y2 = 0.2 * np.sin(2 * np.pi * freq2 * x)
    y3 = 2.0 * np.sin(2 * np.pi * freq3 * x)

    np.random.seed(0)
    y = (y1 + np.random.randn(N) * 0.01)

    return y

def insert_zeros(sig_in, num_zeros):
    sig_interpol = np.zeros(sig_in.shape[0] * num_zeros)
    sig_interpol[::num_zeros] = sig_in
    return sig_interpol

def decimate(sig_in, ratio):
    sig_decimate = sig_in[::ratio]
    return sig_decimate

def plot_fft_sig(sig):

    N = len(sig)
    x = np.linspace(0., 1., N)

    n = np.arange(N)

    # Apply window
    w = 0.42 - 0.5 * np.cos(2 * np.pi * n / (N - 1) ) + \
               0.08 * np.cos(4 * np.pi * n / (N - 1) )

    spec = np.fft.fft((sig * w) /(N/4))

    plt.gca().set_xlim([0.0, N/2])
    plt.gca().set_ylim([-100, 10])
    plt.grid(True)
    plt.plot(N * x[:int(N/2. + 1)], dB20(np.abs(spec[:int(N/2. + 1)])),'b', label='Simulation')


if True:
    plt.figure(figsize=(10,10))

    L = 10
    M = 3

    # Original signal
    sig_in = input_signal()

    # Original signal - time
    plt.subplot(511)
    plt.title('Resampling')
    plt.plot(sig_in[0:100])

    # Original signal - freq
    plt.subplot(512)
    plt.title('Resampling')
    plot_fft_sig(sig_in)

    # Interpolate
    sig_interpol = insert_zeros(sig_in, L)

    plt.subplot(513)
    plot_fft_sig(sig_interpol)

    # Decimate
    sig_decimate = decimate(sig_interpol, M)

    plt.subplot(514)
    plot_fft_sig(sig_decimate)

    # output - time
    plt.subplot(515)
    plt.plot(sig_decimate[0:int(100*L/M)])

    plt.tight_layout()

    plt_name = "resampling.svg"
    plt.savefig(plt_name)
    #plt.savefig(BLOG_PATH + plt_name)

