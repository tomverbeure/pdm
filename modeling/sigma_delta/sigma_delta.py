#! /usr/bin/env python3

import numpy as np
import matplotlib
from matplotlib import pyplot as plt

#from numpy import *
from scipy import signal
from deltasigma import *
from filter_lib import *

save_blog   = False

import platform
if platform.system() == "Darwin":
    BLOG_PATH = "/Users/tom/projects/tomverbeure.github.io/assets/pdm/sigma_delta/"
else:
    BLOG_PATH = "/home/tom/projects/tomverbeure.github.io/assets/pdm/sigma_delta/"

plot_quantization_noise                         = False
plot_sinewave_to_pdm                            = False
plot_sinewave_pdm_psd                           = False
plot_sinewave_to_pdm_different_orders           = False
plot_sinewave_pdm_psd_different_orders          = False
plot_sinewave_to_pdm_different_osr              = False
plot_sinewave_pdm_psd_different_osr             = False
plot_noise_slope_different_orders               = True

class SignalInfo:

    def __init__(self, N, sdInfo):

        self.N      = N
        self.OSD    = sdInfo.OSR
        self.freq   = 2/3

        self.fB     = int(np.ceil(self.N/(2.*sdInfo.OSR)))

        self.ftest  = np.floor(self.freq * self.fB)
        self.u      = 0.5*np.sin(2*np.pi*self.ftest/self.N*np.arange(self.N))
        self.v, xn, xmax, y = simulateDSM(self.u, sdInfo.H)

class SigmaDeltaInfo:
    def __init__(self, order, OSR, name=""):
        self.order      = order
        self.OSR        = OSR
        self.H          = synthesizeNTF(order, OSR, opt=1)

def sigma_delta_sinewave_graph(signalInfo, samplesShown = 301):

    t = np.arange(samplesShown)
    plt.step(t, signalInfo.u[t],'r')
    plt.step(t, signalInfo.v[t], 'g')
    plt.axis([0, samplesShown-1, -1.2, 1.2])

def sigma_delta_sinewave_psd(signalInfo, sdInfo, fs = 1.0):

    f = np.linspace(0, 0.5, int(signalInfo.N/2. + 1))
    spec = np.fft.fft(signalInfo.v * ds_hann(signalInfo.N))/(signalInfo.N/4)
    plt.plot(f * fs, dbv(spec[:int(signalInfo.N/2. + 1)]),'b', label='Simulation')
    figureMagic([0, 0.505 * fs], 0.05 * fs, None, [-120, 5], 20, None, None, None)
    snr = calculateSNR(spec[2:signalInfo.fB+1], signalInfo.ftest - 2)
    #plt.text(0.05 * fs, -10, 'SNR = %4.1fdB @ OSR = %d' % (snr, sdInfo.OSR), verticalalignment='center')
    plt.text(f[signalInfo.fB] * fs * 1.10, -10, 'SNR = %4.1fdB @ OSR = %d' % (snr, sdInfo.OSR), verticalalignment='center')

    NBW = 1.5/signalInfo.N
    Sqq = 4*evalTF(sdInfo.H, np.exp(2j*np.pi*f)) ** 2/3.
    plt.plot(f * fs, dbp(Sqq * NBW), 'm', linewidth=2, label='Expected PSD')
#    plt.text(0.49, -90, 'NBW = %4.1E x $f_s$' % NBW, horizontalalignment='right')

    plt.plot([f[signalInfo.fB] * fs, f[signalInfo.fB] * fs], [dbv(np.amin(np.abs(spec))), dbv(5.0)], 'g-.', linewidth=1.0)

    plt.legend(loc=4)

def sigma_delta_noise_slopes():

    OSR = 64
    N = 8192

    sd1  = SigmaDeltaInfo(1, OSR)
    sd2  = SigmaDeltaInfo(2, OSR)
    sd3  = SigmaDeltaInfo(3, OSR)
    sd4  = SigmaDeltaInfo(4, OSR)

    f = np.linspace(0, 0.105, int(N/10. + 1))

    #spec = np.fft.fft(signalInfo.v * ds_hann(signalInfo.N))/(signalInfo.N/4)
    #plt.plot(f, dbv(spec[:int(signalInfo.N/2. + 1)]),'b', label='Simulation')

    #figureMagic([0, 0.5], 0.05, None, [-120, 0], 20, None, None, None)
    figureMagic([0, 0.105], 0.05, None, [-120, 0], 20, None, None, None)

    #snr = calculateSNR(spec[2:signalInfo.fB+1], signalInfo.ftest - 2)
    #plt.text(0.05, -10, 'SNR = %4.1fdB @ OSR = %d' % (snr, sdInfo.OSR), verticalalignment='center')
    NBW = 1.5/8192

    Sqq = 4*evalTF(sd1.H, np.exp(2j*np.pi*f)) ** 2/3.
    plt.plot(f, dbp(Sqq * NBW), 'r', linewidth=2, label='PSD 1st Order')

    Sqq = 4*evalTF(sd2.H, np.exp(2j*np.pi*f)) ** 2/3.
    plt.plot(f, dbp(Sqq * NBW), 'g', linewidth=2, label='PSD 2nd Order')

    Sqq = 4*evalTF(sd3.H, np.exp(2j*np.pi*f)) ** 2/3.
    plt.plot(f, dbp(Sqq * NBW), 'b', linewidth=2, label='PSD 3rd Order')

    Sqq = 4*evalTF(sd4.H, np.exp(2j*np.pi*f)) ** 2/3.
    plt.plot(f, dbp(Sqq * NBW), 'm', linewidth=2, label='PSD 4rd Order')

    #plt.plot([f[signalInfo.fB], f[signalInfo.fB]], [dbv(np.amin(np.abs(spec))), dbv(1.0)], 'g-.', linewidth=1.0)
    plt.plot([f[N//OSR//2], f[N//OSR//2]], [-120, 0], 'g-.', linewidth=1.0)

    plt.legend(loc=4)

def decimation_without_filtering(signalInfo, sdInfo, decimation_ratio):

    v = signalInfo.v[::decimation_ratio]

    f = np.linspace(0, 0.5, int(signalInfo.N/2./decimation_ratio + 1))
    spec = np.fft.fft(v * ds_hann(signalInfo.N/decimation_ratio))/(signalInfo.N/4/decimation_ratio)

    plt.plot(f, dbv(spec[:int(signalInfo.N/2./decimation_ratio + 1)]),'b', label='Simulation')
    figureMagic([0, 0.5], 0.05, None, [-120, 0], 20, None, None, None)
    snr = calculateSNR(spec[2:signalInfo.fB+1], signalInfo.ftest - 2)
    plt.text(0.05, -10, 'SNR = %4.1fdB @ OSR = %d' % (snr, sdInfo.OSR/decimation_ratio), verticalalignment='center')

    plt.plot([f[signalInfo.fB], f[signalInfo.fB]], [-120, dbv(1.0)], 'g-.', linewidth=1.0)

    plt.legend(loc=4)

def filter_psd(length = 64, order = 1, osr = None, plotStop = None, plotPass = None):

    N = 8192
    h_orig = np.full(length, 1/length)

    h = h_orig

    for i in range(order-1):
        h = np.convolve(h, h_orig)

    h_padded = np.zeros(N)
    h_padded[0:len(h)] = h

    x = np.linspace(0., 1., N)
    H = np.fft.fft(h_padded)

    freqs = fftfreq(N)

    x_mask = freqs >= 0
    Hdb = dbv(np.abs(H))[x_mask]


    plt.grid(True)
    plt.plot(freqs[x_mask], Hdb, label="Length = %d" % length)

    if plotStop:
        stop = np.amax(Hdb[len(Hdb)*2//length::])
        print(stop)
        plt.plot([0.5/length, 2.5/length], [stop, stop], 'm-.', linewidth=1.0)

        plt.text(2.6/length, stop, "%4.1fdB" % stop, bbox=dict(facecolor='white', alpha=0.8))

    if plotPass:
        passDb = Hdb[int(len(Hdb) * 0.01 * 2)]
        plt.plot([0.009, 0.011], [passDb, passDb], 'm-.', linewidth=1.0)
        plt.text(0.012, passDb, "%4.1fdB" % passDb, bbox=dict(facecolor='white', alpha=0.8))

    if osr is not None:
        plt.plot([1/osr, 1/osr], [-120, dbv(3.0)], 'g-.', linewidth=1.0)

    plt.legend(loc=4)

def quantization_noise(quant):

    N=8192
    freq = 128
    x = np.linspace(0., 1., N)

    y1 = 0.5 * np.sin(2 * np.pi * freq * x)

    y2 = (np.floor(quant * (y1)) / quant)
    diff = y1 - y2

    plt.subplot(111)
    plt.title('Sine wave with %d quantization levels' % quant)
    x_range = np.arange(0,100)
    plt.plot((x * N)[x_range], y1[x_range], label="input")
    plt.plot((x * N)[x_range], y2[x_range], '.', label="output")
    plt.plot((x * N)[x_range], diff[x_range], label="error")

    plt.grid(True)
    plt.legend(loc=1)

#============================================================
# Sinewave to PCM with quantization noise
#============================================================

if plot_quantization_noise:
    plt.figure(figsize=(10,4))
    quantization_noise(8)

    plt.tight_layout()
    plt.savefig("quantization_noise_8.svg")
    if save_blog: plt.savefig(BLOG_PATH + "quantization_noise_8.svg")

    plt.figure(figsize=(10,4))
    quantization_noise(256)

    plt.tight_layout()
    plt.savefig("quantization_noise_256.svg")
    if save_blog: plt.savefig(BLOG_PATH + "quantization_noise_256.svg")

#============================================================
# Sinewave to PDM example
#============================================================

#plt.rc('font', size=14)

if plot_sinewave_to_pdm:
    OSR = 16
    order = 1

    sd = SigmaDeltaInfo(order, OSR)
    sinewave = SignalInfo(8192, sd)

    plt.figure(figsize=(10,3))
    plt.subplot(111)
    plt.title('Sigma-Delta Modulator - %dx Oversampling Rate, 1st Order' % OSR);
    sigma_delta_sinewave_graph(sinewave, 150)
    plt.xlabel('Sample Number')

    plt.tight_layout()
    plt.savefig("sinewave_to_pdm.svg")
    if save_blog: plt.savefig(BLOG_PATH + "sinewave_to_pdm.svg")

#============================================================
# Sinewave PSD example
#============================================================

if plot_sinewave_pdm_psd:
    OSR = 16
    order = 1

    sd = SigmaDeltaInfo(order, OSR)
    sinewave = SignalInfo(8192, sd)

    plt.figure(figsize=(10,5))
    plt.title('Output Spectrum - %dx Oversampling Rate, 1st Order' % OSR);
    sigma_delta_sinewave_psd(sinewave, sd, 768)

    plt.tight_layout()
    plt.savefig("sinewave_pdm_psd.svg")
    if save_blog: plt.savefig(BLOG_PATH + "sinewave_pdm_psd.svg")

#============================================================
# Sinewave to PDM for different orders
#============================================================

if plot_sinewave_to_pdm_different_orders:
    OSR = 16

    sd1  = SigmaDeltaInfo(1, OSR)
    sinewave_sd1  = SignalInfo(8192, sd1 )

    sd2  = SigmaDeltaInfo(2, OSR)
    sinewave_sd2  = SignalInfo(8192, sd2 )

    sd3  = SigmaDeltaInfo(3, OSR)
    sinewave_sd3  = SignalInfo(8192, sd3 )

    sd4  = SigmaDeltaInfo(4, OSR)
    sinewave_sd4  = SignalInfo(8192, sd4 )

    plt.figure(figsize=(10,8))
    plt.subplot(411)
    plt.title('Sigma-Delta Modulator with %dx Oversampling Rate, Increasing Order' % OSR);
    sigma_delta_sinewave_graph(sinewave_sd1 , 150)
    plt.ylabel('1st Order')

    plt.subplot(412)
    sigma_delta_sinewave_graph(sinewave_sd2 , 150)
    plt.ylabel('2nd Order')

    plt.subplot(413)
    sigma_delta_sinewave_graph(sinewave_sd3 , 150)
    plt.ylabel('3rd Order')

    plt.subplot(414)
    sigma_delta_sinewave_graph(sinewave_sd4 , 150)
    plt.ylabel('4th Order')

    plt.xlabel('Sample Number')
    plt.tight_layout()
    plt.savefig("sinewave_to_pdm_different_orders.svg")
    if save_blog: plt.savefig(BLOG_PATH + "sinewave_to_pdm_different_orders.svg")

#============================================================
# Sinewave PSD OSR16 for different orders
#============================================================

if plot_sinewave_pdm_psd_different_orders:
    OSR = 16

    sd1  = SigmaDeltaInfo(1, OSR)
    sinewave_sd1  = SignalInfo(8192, sd1 )

    sd2  = SigmaDeltaInfo(2, OSR)
    sinewave_sd2  = SignalInfo(8192, sd2 )

    sd3  = SigmaDeltaInfo(3, OSR)
    sinewave_sd3  = SignalInfo(8192, sd3 )

    sd4  = SigmaDeltaInfo(4, OSR)
    sinewave_sd4  = SignalInfo(8192, sd4 )

    plt.figure(figsize=(10,14))
    plt.subplot(411)
    plt.title('Output Spectrum - %dx Oversampling Rate, Increasing Order' % OSR);
    plt.ylabel('1st Order')
    sigma_delta_sinewave_psd(sinewave_sd1, sd1, 768)

    plt.subplot(412)
    plt.ylabel('2nd Order')
    sigma_delta_sinewave_psd(sinewave_sd2, sd2, 768)

    plt.subplot(413)
    plt.ylabel('3nd Order')
    sigma_delta_sinewave_psd(sinewave_sd3, sd3, 768)

    plt.subplot(414)
    plt.ylabel('4nd Order')
    plt.xlabel('Frequency (kHz)')
    sigma_delta_sinewave_psd(sinewave_sd4, sd4, 768)

    plt.tight_layout()
    plt.savefig("sinewave_pdm_psd_different_orders.svg")
    if save_blog: plt.savefig(BLOG_PATH + "sinewave_pdm_psd_different_orders.svg")

#============================================================
# Sinewave to PDM for different OSR
#============================================================

if plot_sinewave_to_pdm_different_osr:
    sd1  = SigmaDeltaInfo(4, 16)
    sinewave_sd1  = SignalInfo(8192, sd1 )

    sd2  = SigmaDeltaInfo(4, 32)
    sinewave_sd2  = SignalInfo(8192, sd2 )

    sd3  = SigmaDeltaInfo(4, 64)
    sinewave_sd3  = SignalInfo(8192, sd3 )

    plt.figure(figsize=(10,6))
    plt.subplot(311)
    plt.title('Sigma-Delta Modulator with Increasing Oversampling Rate, 4th Order');
    plt.ylabel('16x OSR')
    sigma_delta_sinewave_graph(sinewave_sd1 , 100)

    plt.subplot(312)
    plt.ylabel('32x OSR')
    sigma_delta_sinewave_graph(sinewave_sd2 , 200)

    plt.subplot(313)
    plt.ylabel('64x OSR')
    sigma_delta_sinewave_graph(sinewave_sd3 , 400)

    plt.xlabel('Sample Number')
    plt.tight_layout()
    plt.savefig("sinewave_to_pdm_different_osr.svg")
    if save_blog: plt.savefig(BLOG_PATH + "sinewave_to_pdm_different_osr.svg")

#============================================================
# PSD for different OSR
#============================================================

if plot_sinewave_pdm_psd_different_osr:
    sd1  = SigmaDeltaInfo(4, 16)
    sinewave_sd1  = SignalInfo(8192, sd1 )

    sd2  = SigmaDeltaInfo(4, 32)
    sinewave_sd2  = SignalInfo(8192, sd2 )

    sd3  = SigmaDeltaInfo(4, 64)
    sinewave_sd3  = SignalInfo(8192, sd3 )

    np.save("sine_ord4_osr64.npy", sinewave_sd3.v)

    plt.figure(figsize=(10,10))
    plt.subplot(311)
    plt.title('Output Spectrum - Increasing Oversampling Rate, 4th Order');
    plt.ylabel('16x OSR')
    sigma_delta_sinewave_psd(sinewave_sd1, sd1, 768)

    plt.subplot(312)
    plt.ylabel('32x OSR')
    sigma_delta_sinewave_psd(sinewave_sd2, sd2, 1576)

    plt.subplot(313)
    plt.ylabel('64x OSR')
    plt.xlabel('Frequency (kHz)')
    sigma_delta_sinewave_psd(sinewave_sd3, sd3, 3072)

    plt.tight_layout()
    plt.savefig("sinewave_pdm_psd_different_osr.svg")
    if save_blog: plt.savefig(BLOG_PATH + "sinewave_pdm_psd_different_osr.svg")

#============================================================
# Noise increase for different orders
#============================================================

if plot_noise_slope_different_orders:
    plt.figure(figsize=(10,4))
    plt.subplot(111)
    plt.title('Noise Slopes for a 64x Oversampling Rate Convertor');

    sigma_delta_noise_slopes()
    plt.xlabel('Normalized Frequency')

    plt.tight_layout()
    plt.savefig("noise_slope_different_orders.svg")
    if save_blog: plt.savefig(BLOG_PATH + "noise_slope_different_orders.svg")

