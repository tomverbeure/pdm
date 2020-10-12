#! /usr/bin/env python3

from filter_lib import *

Fs      = 48000
Fpb     = 6000
Fsb     = 10000
Apb     = 0.05
Asb     = 60

N = fir_find_optimal_N(Fs, Fpb, Fsb, Apb, Asb)

(h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max) =  fir_calc_filter(Fs, Fpb, Fsb, Apb, Asb, N)

plt.figure(figsize=(10,5))
plt.subplot(111)
plot_freq_response(w, H, Fs, Fpb, Fsb, Hpb_min, Hpb_max, Hsb_max)
plt.tight_layout()
plt.savefig("remez_example_find_n.svg")



