
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from scipy import signal

def pad_zeros(h, N):

    h_padded = np.zeros(N)
    h_padded[0:len(h)] = h

    return h_padded

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

def plot_freq_response(w, H, Fs, Fpb, Fsb, Hpb_min, Hpb_max, Hsb_max, Ylim_min = -90):
    plt.title("Frequency Reponse")
    plt.grid(True)
    plt.plot(w/np.pi/2*Fs,dB20(np.abs(H)), "r")
    plt.plot([0, Fpb], [dB20(Hpb_max), dB20(Hpb_max)], "b--", linewidth=1.0)
    plt.plot([0, Fpb], [dB20(Hpb_min), dB20(Hpb_min)], "b--", linewidth=1.0)
    plt.plot([Fsb, Fs/2], [dB20(Hsb_max), dB20(Hsb_max)], "b--", linewidth=1.0)
    plt.xlim(0, Fs/2)
    plt.ylim(Ylim_min, 3)


