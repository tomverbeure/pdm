
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

class FilterStats:

    def __init__(self, h, fsample, fcutoff, fstop, N = None):

        self.h          = h
        self.fsample    = fsample
        self.fcutoff    = fcutoff
        self.fstop      = fstop

        if N is None:
            self.N      = len(h)
        else:
            self.N      = N

        h_padded = pad_zeros(h, self.N)
        
        self.H          = np.fft.fft(h_padded)

        self.recalc()

    def recalc(self):

        self.freqs       = np.fft.fftfreq(len(self.H))
        self.x_mask      = self.freqs >= 0

        self.Hdb    = dB20(np.abs(self.H))[self.x_mask]

        self.pass_max, self.pass_min   = self.attn_between(0, self.fcutoff)
        self.stop_max, self.stop_min   = self.attn_between(self.fstop, None)

    def freq_to_x(self, freq):
        x = int(round((freq/self.fsample)*len(self.Hdb)*2))

        return x

    def attn_at(self, freq):
        x_freq = self.freq_to_x(freq)
        attn = self.Hdb[x_freq]

        return attn

    def attn_between(self, freq_min, freq_max):
        if freq_max is None:
            freq_max = self.fsample/2

        x_freq_min = self.freq_to_x(freq_min)
        x_freq_max = self.freq_to_x(freq_max)

        h_min = np.min(self.Hdb[x_freq_min:x_freq_max])
        h_max = np.max(self.Hdb[x_freq_min:x_freq_max])

        return h_max, h_min

    def __str__(self):

        s = ""
        s += "Filter length: %d\n" % len(self.h)
        s += "Sample rate: %0.4f\n" % self.fsample
        s += "Cutoff: %0.4f\n" % self.fcutoff
        s += "Stop : %0.4f\n" % self.fstop
        s += "Pass max (db): %0.4f\n" % self.pass_max
        s += "Pass min (db): %0.4f\n" % self.pass_min
        s += "Stop max (db): %0.4f\n" % self.stop_max

        return s

    def plot(self, filename):
        plt.figure(figsize=(10,8))
        plt.subplot(311)
        plt.grid(True)
        plt.plot(self.h)
        
        plt.subplot(312)
        plt.grid(True)
        plt.plot(self.freqs[self.x_mask] * self.fsample, self.Hdb)
        plt.gca().set_xlim([0.0, self.fsample/2])
        plt.gca().set_ylim([-180, 0])
        plt.gca().ticklabel_format(style="plain")
        
        plt.subplot(313)
        plt.grid(True)
        plt.plot(self.freqs[self.x_mask] * self.fsample, self.Hdb)
        plt.gca().set_xlim([0.0, 1.3 * self.fstop])
        plt.gca().set_ylim([-120, 5])
        plt.plot([self.fcutoff, self.fcutoff], [5, -120],  'g-.', linewidth=1.0)
        plt.plot([self.fstop, self.fstop], [5, -120],  'g-.', linewidth=1.0)
        
        plt.tight_layout()
        plt.savefig(filename)

    def decimation_graph_full_range(self, decimation):
        plt.gca().set_xlim([0.0, self.fsample/2])
        plt.grid(True)
        plt.gca().ticklabel_format(style="plain")
        for i in range(decimation):
            x_start = self.freq_to_x(self.fsample/2/decimation * i)
            x_stop  = self.freq_to_x(self.fsample/2/decimation * (i+1))
            plt.plot(self.freqs[self.x_mask][x_start:x_stop] * self.fsample, self.Hdb[x_start:x_stop])

            if i==0 or i == 2:
                plt.plot(self.freqs[self.x_mask][x_stop] * self.fsample, self.Hdb[x_stop], "rx")
                plt.text(self.freqs[self.x_mask][x_stop] * self.fsample * 1.05, self.Hdb[x_stop], "%0.2f dB" % self.Hdb[x_stop])

    def decimation_graph_aliased(self, decimation, f_pass = None):
        plt.gca().set_xlim([0.0, self.fsample/2/decimation])
        plt.gca().set_ylim([-175, 5.0])
        plt.grid(True)

        for i in range(decimation):
            x_start = self.freq_to_x(self.fsample/2/decimation * i)
            x_stop  = self.freq_to_x(self.fsample/2/decimation * (i+1))

            x_new = self.freq_to_x(self.fsample/2/decimation)
            if i%2==0:
                plt.plot(self.freqs[self.x_mask][0:x_new] * self.fsample, self.Hdb[x_start:x_stop])
            else:
                plt.plot(self.freqs[self.x_mask][0:x_new] * self.fsample, np.flip(self.Hdb[x_start:x_stop]))

        if f_pass is not None:
            x_pass = self.freq_to_x(f_pass)
            y_pass = np.flip(self.Hdb[x_pass])
            plt.plot(f_pass, y_pass, "bx")
            plt.text(f_pass * 0.70, y_pass-10, "%.01fdB" % y_pass)

            x_pass = self.freq_to_x(self.fsample/decimation -f_pass)
            y_pass = np.flip(self.Hdb[x_pass])
            plt.plot(f_pass, y_pass, "bx")
            plt.text(f_pass * 0.60, y_pass, "%.01fdB" % y_pass)

    def decimation_graph(self, decimation, f_pass, filename):
        plt.figure(figsize=(10,10))
        plt.subplot(411)
        plt.title("CIC Decimation by %d\n\nAttenuation before decimation" % decimation)
        plt.gca().set_xlim([0.0, self.fsample/2])
        plt.gca().set_ylim([-175, 5.0])
        plt.grid(True)
        plt.gca().ticklabel_format(style="plain")
        for i in range(decimation):
            x_start = self.freq_to_x(self.fsample/2/decimation * i)
            x_stop  = self.freq_to_x(self.fsample/2/decimation * (i+1))
            plt.plot(self.freqs[self.x_mask][x_start:x_stop] * self.fsample, self.Hdb[x_start:x_stop])

            if i==0 or i == 2:
                plt.plot(self.freqs[self.x_mask][x_stop] * self.fsample, self.Hdb[x_stop], "rx")
                plt.text(self.freqs[self.x_mask][x_stop] * self.fsample * 1.05, self.Hdb[x_stop], "%0.2f dB" % self.Hdb[x_stop])


        plt.subplot(412)
        plt.title("Attenuation after decimation")
        plt.gca().set_xlim([0.0, self.fsample/2/decimation])
        plt.gca().set_ylim([-175, 5.0])
        plt.grid(True)

        Haccum = np.zeros(len(self.H)//decimation//2)

        for i in range(decimation):
            x_start = self.freq_to_x(self.fsample/2/decimation * i)
            x_stop  = self.freq_to_x(self.fsample/2/decimation * (i+1))

            x_new = self.freq_to_x(self.fsample/2/decimation)
            if i%2==0:
                Haccum = Haccum + np.abs(self.H[x_start:x_stop])
                plt.plot(self.freqs[self.x_mask][0:x_new] * self.fsample, self.Hdb[x_start:x_stop])
            else:
                Haccum = Haccum + np.abs(np.flip(self.H[x_start:x_stop]))
                plt.plot(self.freqs[self.x_mask][0:x_new] * self.fsample, np.flip(self.Hdb[x_start:x_stop]))

        plt.subplot(413)
        plt.gca().set_xlim([0.0, self.fsample/2/decimation])
        plt.grid(True)

        plt.plot(self.freqs[self.x_mask][0:len(Haccum)] * self.fsample, self.Hdb[0:len(Haccum)])
        plt.plot(self.freqs[self.x_mask][0:len(Haccum)] * self.fsample, dB20(Haccum))

        plt.subplot(414)
        plt.gca().set_xlim([0.0, self.fsample/2/decimation])
        plt.grid(True)

        x_pass = self.freq_to_x(f_pass)
        Haccum[0:x_pass] = Haccum[0:x_pass] - np.abs(self.H[0:x_pass])

        plt.plot(self.freqs[self.x_mask][0:len(Haccum)] * self.fsample, dB20(Haccum))


        plt.tight_layout()
        plt.savefig(filename)

def reduce_bits(h, nr_bits):

    steps = (2**nr_bits)-1

    h_max = np.max(h)
    h_min = np.min(h)

#    h_delta = h_max-h_min
    h_delta = 2*np.max(np.abs(h))
    float_step = h_delta / steps

    h_int = np.around(h / float_step).astype(int)
    h_round = h_int * float_step

    return h_round, h_int

def fir_calc_filter(Fs, Fpb, Fsb, Apb, Asb, order, H_nr_points = 512, coef_bits = None, verbose = True):

    bands = np.array([0., Fpb/Fs, Fsb/Fs, .5])

    # Remez weight calculation:
    # https://www.dsprelated.com/showcode/209.php

    err_pb = (1 - 10**(-Apb/20))/2      # /2 is not part of the article above, but makes it work much better.
    err_sb = 10**(-Asb/20)

    w_pb = 1/err_pb
    w_sb = 1/err_sb
    
    h = signal.remez(
            order+1,                    # Desired number of taps
            bands,                      # All the band inflection points
            [1,0],                      # Desired gain for each of the bands: 1 in the pass band, 0 in the stop band
            [w_pb, w_sb]
            )               

    if coef_bits is not None:
        h, h_int = reduce_bits(h, coef_bits)
    
    (w,H) = signal.freqz(h, worN = H_nr_points)
    
    Hpb_min = min(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
    Hpb_max = max(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
    Rpb = 1 - (Hpb_max - Hpb_min)
    
    Hsb_max = max(np.abs(H[int(Fsb/Fs*2 * len(H)+1):len(H)]))
    Rsb = Hsb_max
    
    if verbose: print("Rpb: %fdB" % (-dB20(Rpb)))
    if verbose: print("Rsb: %fdB" % -dB20(Rsb))

    return (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max)

def fir_find_optimal_N(Fs, Fpb, Fsb, Apb, Asb, Nmin = 1, Nmax = 1000, H_nr_points = 512, verbose = True):
    for N in range(Nmin, Nmax):
        if verbose: print("Trying N=%d" % N)
        (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max) = fir_calc_filter(Fs, Fpb, Fsb, Apb, Asb, N, H_nr_points = H_nr_points, verbose = verbose)
        if -dB20(Rpb) <= Apb and -dB20(Rsb) >= Asb:
            return N

    return None

# Fs     : sample frequency
# Fpb    : pass-band frequency. 
#          Half band filters are symmatric around Fs/4, so Fpb must be smaller than that.
# order  : filter order (number of taps-1)
#      N must be a multiple of 2, but preferable not a multiple of 4
#
# For a half-band filter, the stop-band frequency Fsb = Fs/2 - Fpb
# This function uses the algorithm described in "A Trick for the Design of FIR Half-Band Filters":
# https://resolver.caltech.edu/CaltechAUTHORS:VAIieeetcs87a
#
# Ideally, N/2 should be odd, because otherwise the outer coefficients of the filter will be 0
# by definition anyway.
def half_band_calc_filter(Fs, Fpb, order, H_nr_points = 512, coef_bits = None, verbose = True):
    assert Fpb < Fs/4, "A half-band filter requires that Fpb is smaller than Fs/4"
    assert order % 2 == 0, "Filter order must be a multiple of 2"
    assert order % 4 != 0, "Filter order must not be a multiple of 4"

    g = signal.remez(
            order//2+1,
            [0., 2*Fpb/Fs, .5, .5],
            [1, 0],
            [1, 1]
            )

    zeros = np.zeros(order//2+1)

    h = [item for sublist in zip(g, zeros) for item in sublist][:-1]
    h[order//2] = 1.0
    h = np.array(h)/2

    if coef_bits is not None:
        h, h_int = reduce_bits(h, coef_bits)

    (w,H) = signal.freqz(h, worN = H_nr_points)

    Fsb = Fs/2-Fpb
    
    Hpb_min = min(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
    Hpb_max = max(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
    Rpb = 1 - (Hpb_max - Hpb_min)
    
    Hsb_max = max(np.abs(H[int(Fsb/Fs*2 * len(H)+1):len(H)]))
    Rsb = Hsb_max
    
    if verbose: print("Rpb: %fdB" % (-dB20(Rpb)))
    if verbose: print("Rsb: %fdB" % -dB20(Rsb))

    return (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max)

def half_band_find_optimal_N(Fs, Fpb, Apb, Asb, Nmin = 2, Nmax = 1000, verbose = True):
    for N in range(Nmin, Nmax, 4):
        if verbose: print("Trying N=%d" % N)
        (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max) = half_band_calc_filter(Fs, Fpb, N, verbose = verbose)
        if -dB20(Rpb) <= Apb and -dB20(Rsb) >= Asb:
            return N

    return None

# decimation:
# This determines the number of samples that are averaged together thus
# frequency behavior in terms of where the attenuation becomes infinite etc.
#
# order:
# the number of cascaded CIC filter sections.
#
# differential_delay:
# the number of delays in the integrator part of the CIC cascade.
# The differential delay is almost always 1, or sometimes 2.

def cic_filter(decimation, order, differential_delay = 1):

        mov_avg_length  = decimation * differential_delay

        # Single stage CIC filter
        # Implemented as generic FIR, because a 'true' CIC filter only works
        # with lossless integer operations.
        h_cic_single = np.ones(mov_avg_length) / mov_avg_length
    
        # Convolve against itself as much as needed for a higher order CIC filter
        h_cic = h_cic_single
        for i in range(order-1):
            h_cic = np.convolve(h_cic, h_cic_single)

        return h_cic

# Unfolds the frequency response by a given decimation ratio
def H_unfold(Hin, ratio):

    Hout = []

    for i in range(ratio):

        if i%2 == 0:
            Hout = np.append(Hout, Hin)
        else:
            Hout = np.append(Hout, Hin[::-1])

    return Hout


def plot_freq_response(w, H, Fs, Fpb, Fsb, Hpb_min, Hpb_max, Hsb_max, Ylim_min = -90):
    plt.title("Frequency Reponse")
    plt.grid(True)
    plt.plot(w/np.pi/2*Fs,dB20(np.abs(H)), "r")
    plt.plot([0, Fpb], [dB20(Hpb_max), dB20(Hpb_max)], "b--", linewidth=1.0)
    plt.plot([0, Fpb], [dB20(Hpb_min), dB20(Hpb_min)], "b--", linewidth=1.0)
    plt.plot([Fsb, Fs/2], [dB20(Hsb_max), dB20(Hsb_max)], "b--", linewidth=1.0)
    plt.xlim(0, Fs/2)
    plt.ylim(Ylim_min, 3)


