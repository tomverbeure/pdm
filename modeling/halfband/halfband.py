#! /usr/bin/env python3

import numpy as np
import matplotlib
from matplotlib import pyplot as plt

from scipy import signal
from filter_lib import *

save_blog = False

plot_half_band_example          = False
plot_6x_decimation_stand_alone  = True
plot_2stage_decimation          = True

import platform
if platform.system() == "Darwin":
    BLOG_PATH = "/Users/tom/projects/tomverbeure.github.io/assets/pdm/halfband/"
else:
    BLOG_PATH = "/home/tom/projects/tomverbeure.github.io/assets/pdm/halfband/"

def dB20(array):
    with np.errstate(divide='ignore'):
        return 20 * np.log10(array)


#============================================================
# Half Band Filter
#============================================================

if plot_half_band_example: 

    f_s     = 192
    f_pb    = 45.0

    N = half_band_find_optimal_N(f_s, f_pb, 2, 10)

    (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max) = half_band_calc_filter(f_s, f_pb, N)

    plt.figure(figsize=(10,8))

    plt.subplot(211)
    plt.title("Half Band Filter\nMagnitude Response (linear)")
    plt.gca().set_xlim(0, 0.5)
    plt.gca().set_ylim(0, 1.1)
    plt.grid(True)
    plt.plot(w/np.pi/2, np.abs(H))
    plt.plot(0.25, 0.5, "r*")
    # (0.5, 0.5) symmetry axes
    plt.plot([0, 0.5], [0.5, 0.5], "r-.", linewidth=1.0)
    plt.plot([0.25, 0.25], [-1, 1.2], "r-.", linewidth=1.0)
    # Pass band
    plt.plot([f_pb/f_s, f_pb/f_s], [0.6, 1.1], "b-.", linewidth=1.0)
    plt.plot([0, f_pb/f_s], [1.0, 1.0], "b-.", linewidth=1.0)
    # Stop band
    plt.plot([0.5-f_pb/f_s, 0.5-f_pb/f_s], [0, 0.4], "b-.", linewidth=1.0)

    plt.subplot(212)
    plt.gca().set_xlim(-0.2, N+0.2)
    plt.grid(True)
    plt.stem(h)
    plt.title("%d Coefficients" % (N+1))

    plt.tight_layout()
    plt.savefig("half_band_example.svg")
    if save_blog: plt.savefig(BLOG_PATH + "half_band_example.svg")

#============================================================
# Single stage 6x decimation
#============================================================

if plot_6x_decimation_stand_alone:

    f_s     = 288000
    f_pb    = 10000
    f_sb    = 24000
    a_pb    = 0.1
    a_sb    = 90

    N = fir_find_optimal_N(f_s, f_pb, f_sb, a_pb, a_sb)

    print("Muls per second: %d * %d = %d" % (f_s/6, N+1, f_s/6 * (N+1)))

#============================================================
# 2-stage decimation
#============================================================

if plot_2stage_decimation:

    f_s     = 288000
    f_pb    = 10000
    f_sb    = 24000
    a_pb    = 0.1
    a_sb    = 90

    hb_N = half_band_find_optimal_N(f_s, f_sb, a_pb/2, a_sb)
    (hb_h, hb_w, hb_H, hb_Rpb, hb_Rsb, hb_Hpb_min, hb_Hpb_max, hb_Hsb_max) = half_band_calc_filter(f_s, f_sb, hb_N)
    hb_muls = f_s/2 * (hb_N/2+1)

    print(dB20(hb_Rpb))

    fir_N = fir_find_optimal_N(f_s/2, f_pb, f_sb, a_pb - dB20(hb_Rpb), a_sb)
    fir_muls = f_s/6 * (fir_N+1)

    print("Half band muls per second: %d * (%d/2+1) = %d" % (f_s/2, hb_N, hb_muls))
    print("FIR muls per second: %d * %d = %d" % (f_s/6, fir_N+1, fir_muls))
    print("Total muls: %d" % (hb_muls + fir_muls))




