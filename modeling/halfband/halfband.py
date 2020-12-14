#! /usr/bin/env python3

import numpy as np
import matplotlib
from matplotlib import pyplot as plt

from scipy import signal
from filter_lib import *

save_blog = False

plot_half_band_example          = False
plot_half_band_standalone       = True

import platform
if platform.system() == "Darwin":
    BLOG_PATH = "/Users/tom/projects/tomverbeure.github.io/assets/pdm/halfband/"
else:
    BLOG_PATH = "/home/tom/projects/tomverbeure.github.io/assets/pdm/halfband/"

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

if plot_half_band_standalone:
