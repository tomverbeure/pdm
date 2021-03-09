#! /usr/bin/env python3

import numpy as np
import matplotlib
from matplotlib import pyplot as plt

from scipy import signal
from filter_lib import *

save_blog = False

import platform
if platform.system() == "Darwin":
    BLOG_PATH = "/Users/tom/projects/tomverbeure.github.io/assets/pdm/cic_filters/"
else:
    BLOG_PATH = "/home/tom/projects/tomverbeure.github.io/assets/pdm/cic_filters/"

def mov_avg_filter_psd(length = 64, order = 1, osr = None, plotStop = None, plotPass = None, plotLog = True):

    N = 8192
    h_orig = np.full(length, 1/length)

    h = h_orig

    for i in range(order-1):
        h = np.convolve(h, h_orig)

    h_padded = np.zeros(N)
    h_padded[0:len(h)] = h

    H = np.fft.fft(h_padded)

    freqs = np.fft.fftfreq(N)

    x_mask = freqs >= 0
    Hdb = dB20(np.abs(H))[x_mask]

    plt.grid(True)
    if plotLog:
        plt.plot(freqs[x_mask], Hdb, label="Length = %d" % length)
    else:
        plt.plot(freqs[x_mask], np.abs(H)[x_mask], label="Length = %d" % length)

    if plotStop:
        stop = np.amax(Hdb[len(Hdb)*2//length::])
        print("Stop band attenutation: %.04f" % stop)
        plt.plot([0.5/length, 2.5/length], [stop, stop], 'm-.', linewidth=1.0)

        plt.text(2.6/length, stop, "%4.1fdB" % stop, bbox=dict(facecolor='white', alpha=0.8))

    if plotPass:
        passDb = Hdb[int(len(Hdb) * 0.01 * 2)]
        plt.plot([0.009, 0.011], [passDb, passDb], 'm-.', linewidth=1.0)
        plt.text(0.012, passDb, "%4.1fdB" % passDb, bbox=dict(facecolor='white', alpha=0.8))

    if osr is not None:
        plt.plot([1/osr, 1/osr], [-120, dB20(3.0)], 'g-.', linewidth=1.0)

    plt.legend(loc=4)

def decimation_without_filtering_regular(decimation_ratio):

    N=10000

    x = np.linspace(0., 1., N, endpoint=False)

    freq1 = 100
    freq2 = 1000
    freq3 = 2800

    y1 = 0.2 * np.sin(2 * np.pi * freq1 * x)
    y2 = 0.2 * np.sin(2 * np.pi * freq2 * x)
    y3 = 2.0 * np.sin(2 * np.pi * freq3 * x)

    np.random.seed(0)
    y = (y1 + y2 + y3 + np.random.randn(N) * 0.05)[::decimation_ratio]

    n = np.arange(N/decimation_ratio)
    w = 0.42 - 0.5 * np.cos(2 * np.pi * n / (N - 1) * decimation_ratio) + \
               0.08 * np.cos(4 * np.pi * n / (N - 1) * decimation_ratio)

    spec = np.fft.fft((y * w) /(N/4/decimation_ratio))
    spec = np.fft.fft((y) /(N/4/decimation_ratio))

    plt.gca().set_xlim([0.0, N/2])
    plt.gca().set_ylim([-70, 15])
    plt.grid(True)
    plt.plot(N * x[:int(N/2./decimation_ratio + 1)], dB20(np.abs(spec[:int(N/2./decimation_ratio + 1)])),'b', label='Simulation')


#============================================================
# Moving Average Filter - Linear
#============================================================

if True:
    plt.figure(figsize=(10,10))

    plt.subplot(311)
    plt.title('Moving Average Filter Response - Linear')

    plt.gca().set_xlim([0.0, 0.5])
    mov_avg_filter_psd(2,  1, plotLog = False)
    mov_avg_filter_psd(4,  1, plotLog = False)
    mov_avg_filter_psd(8,  1, plotLog = False)
    mov_avg_filter_psd(16, 1, plotLog = False)
    mov_avg_filter_psd(64, 1, plotLog = False)
    plt.ylabel("1st Order")

    plt.subplot(312)
    plt.gca().set_xlim([0.0, 0.5])
    mov_avg_filter_psd(2,  2, plotLog = False)
    mov_avg_filter_psd(4,  2, plotLog = False)
    mov_avg_filter_psd(8,  2, plotLog = False)
    mov_avg_filter_psd(16, 2, plotLog = False)
    mov_avg_filter_psd(64, 2, plotLog = False)
    plt.ylabel("2nd Order")

    plt.subplot(313)
    plt.gca().set_xlim([0.0, 0.5])
    mov_avg_filter_psd(2,  4, plotLog = False)
    mov_avg_filter_psd(4,  4, plotLog = False)
    mov_avg_filter_psd(8,  4, plotLog = False)
    mov_avg_filter_psd(16, 4, plotLog = False)
    mov_avg_filter_psd(64, 4, plotLog = False)
    plt.ylabel("4th Order")

    plt.xlabel('Normalized frequency')

    plt.tight_layout()

    plt_name = "moving_average_filter_overview_linear.svg"
    plt.savefig(plt_name)
    if save_blog: plt.savefig(BLOG_PATH + plt_name)

#============================================================
# Moving Average Filter - dB
#============================================================

if True:
    plt.figure(figsize=(10,10))

    plt.subplot(311)
    plt.title('Moving Average Filter Response - dB')

    plt.gca().set_ylim([-120, 5])
    plt.gca().set_xlim([0.0, 0.5])

    mov_avg_filter_psd(2,  1)
    mov_avg_filter_psd(4,  1)
    mov_avg_filter_psd(8,  1)
    mov_avg_filter_psd(16, 1, osr = 64)
    mov_avg_filter_psd(64, 1, plotStop = True)
    plt.ylabel("1st Order")

    plt.subplot(312)
    plt.gca().set_ylim([-120, 5])
    plt.gca().set_xlim([0.0, 0.5])

    mov_avg_filter_psd(2,  2)
    mov_avg_filter_psd(4,  2)
    mov_avg_filter_psd(8,  2)
    mov_avg_filter_psd(16, 2, osr = 64)
    mov_avg_filter_psd(64, 2, plotStop = True)
    plt.ylabel("2nd Order")

    plt.subplot(313)
    plt.gca().set_ylim([-120, 5])
    plt.gca().set_xlim([0.0, 0.5])

    mov_avg_filter_psd(2,  5)
    mov_avg_filter_psd(4,  5)
    mov_avg_filter_psd(8,  5)
    mov_avg_filter_psd(16, 5, osr = 64)
    mov_avg_filter_psd(64, 5, plotStop = True)
    plt.ylabel("4th Order")
    plt.xlabel('Normalized frequency')

    plt.tight_layout()

    plt_name = "moving_average_filter_overview.svg"
    plt.savefig(plt_name)
    if save_blog: plt.savefig(BLOG_PATH + plt_name)

#============================================================
# Moving Average Filter Passband
#============================================================


if False:
    plt.figure(figsize=(10,4))

    plt.subplot(111)
    plt.title('Moving Average Filter Response - Passband')
    plt.gca().set_ylim([-120, 5])
    plt.gca().set_xlim([0.0, 0.05])

    mov_avg_filter_psd(2,  5)
    mov_avg_filter_psd(4,  5)
    mov_avg_filter_psd(8,  5)
    mov_avg_filter_psd(16, 5, plotPass = True)
    mov_avg_filter_psd(32, 5)
    mov_avg_filter_psd(64, 5, plotStop = True, plotPass = True, osr = 64)
    plt.ylabel("4th Order")
    plt.xlabel('Normalized frequency')

    plt.tight_layout()

    plt_name = "moving_average_filter_passband.svg"
    plt.savefig(plt_name)
    if save_blog: plt.savefig(BLOG_PATH + plt_name)

#============================================================
# 5th order CIC filter with 4x decimation
#============================================================

if True:
    f_sample = 80000
    f_cutoff = 4000
    decimation = 4
    order = 5

    h_mov_avg = np.ones(decimation) / decimation
    h_mov_avg_casc = h_mov_avg
    for i in range(order-1):
        h_mov_avg_casc = np.convolve(h_mov_avg_casc, h_mov_avg)

        h_mov_avg_casc_stats = FilterStats(h_mov_avg_casc, fsample = f_sample, fcutoff = f_cutoff, fstop = f_cutoff*1.2, N = 16384)

    plt.figure(figsize=(10,4))
    plt.subplot(111)
    plt.title("CIC Decimation by %d\n\nAttenuation before decimation" % decimation)
    h_mov_avg_casc_stats.decimation_graph_full_range(4);
    plt.gca().set_ylim([-175, 5.0])
    plt.tight_layout()

    plt_name = "cic_decimation_full_range.svg"
    plt.savefig(plt_name)
    if save_blog: plt.savefig(BLOG_PATH + plt_name)

    plt.figure(figsize=(10,4))
    plt.subplot(111)
    plt.title("CIC Decimation by %d\n\nAttenuation after decimation" % decimation)
    h_mov_avg_casc_stats.decimation_graph_aliased(4);
    plt.gca().set_ylim([-175, 5.0])
    plt.tight_layout()

    plt_name = "cic_decimation_aliased.svg"
    plt.savefig(plt_name)
    if save_blog: plt.savefig(BLOG_PATH + plt_name)

    plt.figure(figsize=(10,4))
    plt.subplot(111)
    plt.title("CIC Decimation by %d\n\nAttenuation at lower frequencies" % decimation)
    h_mov_avg_casc_stats.decimation_graph_aliased(4, 2000);
    plt.gca().set_ylim([-175, 5.0])
    plt.plot([2000, 2000], [-200, 5], "g-.", linewidth=1.5)
    plt.tight_layout()

    plt_name = "cic_decimation_lower_freqs.svg"
    plt.savefig(plt_name)
    if save_blog: plt.savefig(BLOG_PATH + plt_name)

#============================================================
# Decimation without filtering
#============================================================

if True:
    plt.figure(figsize=(10,3))
    plt.subplot(111)
    decimation_without_filtering_regular(1)
    plt.title("Original Signal - No Decimation")

    plt.tight_layout()
    plt_name = "decimation_without_filtering-no_decimation.svg"
    plt.savefig(plt_name)
    if save_blog: plt.savefig(BLOG_PATH + plt_name)

    plt.figure(figsize=(10,6))
    plt.subplot(211)
    decimation_without_filtering_regular(2)
    plt.title("Signal after 2x Decimation")

    plt.subplot(212)
    decimation_without_filtering_regular(4)
    plt.title("Signal after 4x Decimation")

    plt.tight_layout()
    plt_name = "decimation_without_filtering-2x_4x_decimation.svg"
    plt.savefig(plt_name)
    if save_blog: plt.savefig(BLOG_PATH + plt_name)
