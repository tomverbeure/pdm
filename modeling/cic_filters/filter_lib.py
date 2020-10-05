
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

