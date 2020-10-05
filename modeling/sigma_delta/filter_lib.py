
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

