
import numpy as np
from matplotlib import pyplot as plt
from scipy import signal

def dB20(array):
    with np.errstate(divide='ignore'):
        return 20 * np.log10(array)


def fir_calc_filter(Fs, Fpb, Fsb, Apb, Asb, N):

    bands = np.array([0., Fpb/Fs, Fsb/Fs, .5])

    # Remez weight calculation:
    # https://www.dsprelated.com/showcode/209.php

    err_pb = (1 - 10**(-Apb/20))/2      # /2 is not part of the article above, but makes it work much better.
    err_sb = 10**(-Asb/20)

    w_pb = 1/err_pb
    w_sb = 1/err_sb
    
    h = signal.remez(
            N+1,                        # Desired number of taps
            bands,                      # All the band inflection points
            [1,0],                      # Desired gain for each of the bands: 1 in the pass band, 0 in the stop band
            [w_pb, w_sb]
            )               
    
    (w,H) = signal.freqz(h)
    
    Hpb_min = min(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
    Hpb_max = max(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
    Rpb = 1 - (Hpb_max - Hpb_min)
    
    Hsb_max = max(np.abs(H[int(Fsb/Fs*2 * len(H)+1):len(H)]))
    Rsb = Hsb_max
    
    print("Rpb: %fdB" % (-dB20(Rpb)))
    print("Rsb: %fdB" % -dB20(Rsb))

    return (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max)

def fir_find_optimal_N(Fs, Fpb, Fsb, Apb, Asb, Nmin = 1, Nmax = 1000):
    for N in range(Nmin, Nmax):
        print("Trying N=%d" % N)
        (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max) = fir_calc_filter(Fs, Fpb, Fsb, Apb, Asb, N)
        if -dB20(Rpb) <= Apb and -dB20(Rsb) >= Asb:
            return N

    return None

# Fs : sample frequency
# Fpb: pass-band frequency. 
#      Half band filters are symmatric around Fs/4, so Fpb must be smaller than that.
# N  : filter order (number of taps-1)
#      N must be a multiple of 2, but preferable not a multiple of 4
#
# For a half-band filter, the stop-band frequency Fsb = Fs/2 - Fpb
# This function uses the algorithm described in "A Trick for the Design of FIR Half-Band Filters":
# https://resolver.caltech.edu/CaltechAUTHORS:VAIieeetcs87a
#
# Ideally, N/2 should be odd, because otherwise the outer coefficients of the filter will be 0
# by definition anyway.
def half_band_calc_filter(Fs, Fpb, N):
    assert Fpb < Fs/4, "A half-band filter requires that Fpb is smaller than Fs/4"
    assert N % 2 == 0, "Filter order N must be a multiple of 2"
    assert N % 4 != 0, "Filter order N must not be a multiple of 4"

    g = signal.remez(
            N//2+1,
            [0., 2*Fpb/Fs, .5, .5],
            [1, 0],
            [1, 1]
            )

    zeros = np.zeros(N//2+1)

    h = [item for sublist in zip(g, zeros) for item in sublist][:-1]
    h[N//2] = 1.0
    h = np.array(h)/2

    (w,H) = signal.freqz(h)

    Fsb = Fs/2-Fpb
    
    Hpb_min = min(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
    Hpb_max = max(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
    Rpb = 1 - (Hpb_max - Hpb_min)
    
    Hsb_max = max(np.abs(H[int(Fsb/Fs*2 * len(H)+1):len(H)]))
    Rsb = Hsb_max
    
    print("Rpb: %fdB" % (-dB20(Rpb)))
    print("Rsb: %fdB" % -dB20(Rsb))

    return (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max)

def half_band_find_optimal_N(Fs, Fpb, Apb, Asb, Nmin = 2, Nmax = 1000):
    for N in range(Nmin, Nmax, 4):
        print("Trying N=%d" % N)
        (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max) = half_band_calc_filter(Fs, Fpb, N)
        if -dB20(Rpb) <= Apb and -dB20(Rsb) >= Asb:
            return N

    return None

def plot_freq_response(w, H, Fs, Fpb, Fsb, Hpb_min, Hpb_max, Hsb_max):
    plt.title("Frequency Reponse")
    plt.grid(True)
    plt.plot(w/np.pi/2*Fs,dB20(np.abs(H)), "r")
    plt.plot([0, Fpb], [dB20(Hpb_max), dB20(Hpb_max)], "b--", linewidth=1.0)
    plt.plot([0, Fpb], [dB20(Hpb_min), dB20(Hpb_min)], "b--", linewidth=1.0)
    plt.plot([Fsb, Fs/2], [dB20(Hsb_max), dB20(Hsb_max)], "b--", linewidth=1.0)
    plt.xlim(0, Fs/2)
    plt.ylim(-90, 3)


