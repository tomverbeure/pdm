#! /usr/bin/env python3

import numpy as np
import matplotlib
from matplotlib import pyplot as plt

from scipy import signal
from filter_lib import *

# Sample rate of the microphone
f_pdm   = 2304000

# Sample rate of the audio output
f_out   = 48000  

f_pb    = 6000
f_sb    = 10000

# We expect maximum 0.1dB ripple in passband and at least -60dB attenuation the stop band.
a_pb    = 0.1
a_sb    = 89

save_blog = False

plot_filter_the_damn_thing      = True

import platform
if platform.system() == "Darwin":
    BLOG_PATH = "/Users/tom/projects/tomverbeure.github.io/assets/pdm/datasheet_specs/"
else:
    BLOG_PATH = "/home/tom/projects/tomverbeure.github.io/assets/pdm/datasheet_specs/"

#============================================================
# Filter the Damn Thing
#============================================================
if plot_filter_the_damn_thing:
    print()
    print("Filter the Damn Thing: f_pdm -> final = %d" % f_pdm)
    print()

    N = fir_find_optimal_N(f_pdm, f_pb, f_sb, a_pb, a_sb, Nmin = 2205, Nmax = 2500)
    print("Filter order: %d" % N)
    (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max) = fir_calc_filter(f_pdm, f_pb, f_sb, a_pb, a_sb, N)

    plt.figure(figsize=(10,4))
    plt.subplot(111)
    plot_freq_response(w, H, f_pdm, f_pb, f_sb, Hpb_min, Hpb_max, Hsb_max, Ylim_min = -120)
    plt.title("Just Filter the Damn Thing - Frequency Reponse\n%d Taps" % (N+1))

    plt.tight_layout()
    plt.savefig("filter_the_damn_thing.svg")
    if save_blog: plt.savefig(BLOG_PATH + "filter_the_damn_thing.svg")

    plt.figure(figsize=(10,5))
    plt.subplot(211)
    plt.title("Just Filter the Damn Thing - Impulse Reponse")
    plt.grid(True)
    plt.plot(h)
    plt.subplot(212)
    plt.grid(True)
    plt.plot(h[0:50])
    plt.tight_layout()
    plt.savefig("filter_the_damn_thing_impulse.svg")
    if save_blog: plt.savefig(BLOG_PATH + "filter_the_damn_thing_impulse.svg")

