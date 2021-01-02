#! /usr/bin/env python3

import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import EngFormatter

from scipy import signal
from filter_lib import *

import json

plot_combined_freq_response         = False
plot_reduced_bits                   = True

save_blog = False

import platform
if platform.system() == "Darwin":
    BLOG_PATH = "/Users/tom/projects/tomverbeure.github.io/assets/pdm/pdm_pcm2rtl/"
else:
    BLOG_PATH = "/home/tom/projects/tomverbeure.github.io/assets/pdm/pdm_pcm2rtl/"

#============================================================
# Overall filter requirements:
#============================================================

# Note: changing the numbers below will not automagically make the graphs and
# tables adjust correctly.
# There are a whole lot of hardcoded numbers, such as xlim and ylim ranges
# in graphs etc.

# Sample rate of the microphone
f_pdm   = 2304000

# Sample rate of the audio output
f_out   = 48000  

# End of passband
f_pb    = 6000

# Start of stopband
f_sb    = 10000

# Maximum ripple in the pass band
a_pb    = 0.1

# Maximum ripple in the stop band
a_sb    = 89


total_decim = f_pdm//f_out

if plot_combined_freq_response:

    # If we make the length of H a multiple of the total decimation rate, we can
    # easily slice and dice them into all the factors of the decimation.
    print(total_decim)
    H_size = round(65536/(total_decim*2)) * (total_decim*2)

    #============================================================
    # CIC Filter
    #============================================================
    cic_decim       = 12
    cic_order       = 4


    h_cic = cic_filter(cic_decim, cic_order)
    h_cic_stats = FilterStats(h_cic, fsample = f_pdm, fcutoff = f_pb, fstop = f_sb, N = H_size)
    cic_w, cic_H = signal.freqz(h_cic, worN = H_size)

    cic_pb_attn = h_cic_stats.attn_at(f_pb)
    cic_sb_attn = h_cic_stats.attn_at(2*(f_pdm/2/cic_decim) - f_sb)

    decim_remain    = (f_pdm//cic_decim) // f_out
    f_s_remain      = f_pdm//cic_decim
    pb_attn_remain  = a_pb - abs(cic_pb_attn)

    #============================================================
    # HB1 Filter
    #============================================================

    hb1_N = half_band_find_optimal_N(f_s_remain, f_sb, pb_attn_remain, a_sb, verbose = False)
    (hb1_h, hb1_w, hb1_H, hb1_Rpb, hb1_Rsb, hb1_Hpb_min, hb1_Hpb_max, hb1_Hsb_max) = half_band_calc_filter(f_s_remain, f_sb, order = hb1_N, H_nr_points = H_size)

    decim_remain //= 2
    f_s_remain //= 2
    pb_attn_remain -= abs(dB20(hb1_Rpb))

    #============================================================
    # HB2 Filter
    #============================================================

    hb2_N = half_band_find_optimal_N(f_s_remain, f_sb, pb_attn_remain, a_sb, verbose = False)
    (hb2_h, hb2_w, hb2_H, hb2_Rpb, hb2_Rsb, hb2_Hpb_min, hb2_Hpb_max, hb2_Hsb_max) = half_band_calc_filter(f_s_remain, f_sb, order = hb2_N, H_nr_points = H_size)

    decim_remain //= 2
    f_s_remain //= 2
    pb_attn_remain -= abs(dB20(hb2_Rpb))

    #============================================================
    # FIR Filter
    #============================================================

    fir_N = fir_find_optimal_N(f_s_remain, f_pb, f_sb, pb_attn_remain, a_sb, verbose = False)
    (fir_h, fir_w, fir_H, fir_Rpb, fir_Rsb, fir_Hpb_min, fir_Hpb_max, fir_Hsb_max) = fir_calc_filter(f_s_remain, f_pb, f_sb, pb_attn_remain, a_sb, order = fir_N, H_nr_points = H_size)


    #============================================================
    # 
    #============================================================

    hb1_H_no_decim  = H_unfold(hb1_H, 12)[::12]
    hb2_H_no_decim  = H_unfold(hb2_H, 24)[::24]
    fir_H_no_decim  = H_unfold(fir_H, 48)[::48]

    cic_hb1_H           = cic_H * hb1_H_no_decim
    cic_hb1_hb2_H       = cic_H * hb1_H_no_decim * hb2_H_no_decim
    cic_hb1_hb2_fir_H   = cic_H * hb1_H_no_decim * hb2_H_no_decim * fir_H_no_decim

    plt.figure(figsize=(10, 12))

    # ============================================================
    # CIC
    plt.subplot(4,2,1)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("CIC Filter")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(cic_H)))

    plt.subplot(4,2,2)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-260, 5])
    plt.gca().set_title("CIC Filter")
    plt.xlabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(cic_H)))

    # ============================================================
    # HB1
    plt.subplot(4,2,3)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("HB1 Filter")
    plt.xlabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(hb1_H_no_decim)))

    plt.subplot(4,2,4)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-260, 5])
    plt.gca().set_title("CIC + HB1 Filter")
    plt.xlabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(cic_hb1_H)))

    # ============================================================
    # HB2
    plt.subplot(4,2,5)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("HB2 Filter")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(hb2_H_no_decim)))

    plt.subplot(4,2,6)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-260, 5])
    plt.gca().set_title("CIC + HB1 + HB2 Filter")
    plt.xlabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(cic_hb1_hb2_H)))

    # ============================================================
    # FIR
    plt.subplot(4,2,7)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("FIR Filter")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    #plt.plot(cic_w, dB20(np.abs(cic_H)))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(fir_H_no_decim)))

    plt.subplot(4,2,8)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-260, 5])
    plt.gca().set_title("CIC + HB1 + HB2 + FIR Filter")
    plt.xlabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(cic_hb1_hb2_fir_H)))

    plt.tight_layout()
    plt.savefig("pdm_pcm2rtl_joint_filters.svg")
    if save_blog: plt.savefig(BLOG_PATH + "pdm_pcm2rtl_joint_filters.svg")

    # ============================================================
    # Decimate H

    plt.figure(figsize=(10, 5))

    H_decimated_len = len(cic_hb1_hb2_fir_H)//48
    H_decimated = np.zeros(H_decimated_len)

    for i in range(0, 48):

        if i%2 == 0:
            H_decimated = H_decimated + cic_hb1_hb2_fir_H[i*H_decimated_len:(i+1)*H_decimated_len]
        else:
            H_decimated = H_decimated + np.flip(cic_hb1_hb2_fir_H[i*H_decimated_len:(i+1)*H_decimated_len])

    plt.subplot(2,1,1)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2/48])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("After Decimation - Full Range")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w[0:len(H_decimated)]/np.pi/2*f_pdm, dB20(np.abs(H_decimated)))

    plt.subplot(2,1,2)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pb * 1.2])
    plt.gca().set_ylim([-a_pb*1.5, a_pb*1.5])
    plt.gca().set_title("After Decimation - Pass Band")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w[0:len(H_decimated)]/np.pi/2*f_pdm, dB20(np.abs(H_decimated)))


    plt.tight_layout()
    plt.savefig("pdm_pcm2rtl_joint_filters_after_decimation.svg")
    if save_blog: plt.savefig(BLOG_PATH + "pdm_pcm2rtl_joint_filters_after_decimation.svg")

if plot_reduced_bits:

    coef_bits = 17
    a_sb      = 101

    # If we make the length of H a multiple of the total decimation rate, we can
    # easily slice and dice them into all the factors of the decimation.
    print(total_decim)
    H_size = round(65536/(total_decim*2)) * (total_decim*2)

    #============================================================
    # CIC Filter
    #============================================================
    cic_decim       = 12
    cic_order       = 4


    h_cic = cic_filter(cic_decim, cic_order)
    h_cic_stats = FilterStats(h_cic, fsample = f_pdm, fcutoff = f_pb, fstop = f_sb, N = H_size)
    cic_w, cic_H = signal.freqz(h_cic, worN = H_size)

    cic_pb_attn = h_cic_stats.attn_at(f_pb)
    cic_sb_attn = h_cic_stats.attn_at(2*(f_pdm/2/cic_decim) - f_sb)

    decim_remain    = (f_pdm//cic_decim) // f_out
    f_s_remain      = f_pdm//cic_decim
    pb_attn_remain  = a_pb - abs(cic_pb_attn)

    #============================================================
    # HB1 Filter
    #============================================================

    hb1_N = half_band_find_optimal_N(f_s_remain, f_sb, pb_attn_remain, a_sb, verbose = False)
    (hb1_h, hb1_w, hb1_H, hb1_Rpb, hb1_Rsb, hb1_Hpb_min, hb1_Hpb_max, hb1_Hsb_max) = half_band_calc_filter(f_s_remain, f_sb, order = hb1_N, coef_bits = coef_bits, H_nr_points = H_size)

    decim_remain //= 2
    f_s_remain //= 2
    pb_attn_remain -= abs(dB20(hb1_Rpb))

    #============================================================
    # HB2 Filter
    #============================================================

    hb2_N = half_band_find_optimal_N(f_s_remain, f_sb, pb_attn_remain, a_sb, verbose = False)
    (hb2_h, hb2_w, hb2_H, hb2_Rpb, hb2_Rsb, hb2_Hpb_min, hb2_Hpb_max, hb2_Hsb_max) = half_band_calc_filter(f_s_remain, f_sb, order = hb2_N, coef_bits = coef_bits, H_nr_points = H_size)

    decim_remain //= 2
    f_s_remain //= 2
    pb_attn_remain -= abs(dB20(hb2_Rpb))

    #============================================================
    # FIR Filter
    #============================================================

    fir_N = fir_find_optimal_N(f_s_remain, f_pb, f_sb, pb_attn_remain, a_sb, H_nr_points = H_size, verbose = True)
    (fir_h, fir_w, fir_H, fir_Rpb, fir_Rsb, fir_Hpb_min, fir_Hpb_max, fir_Hsb_max) = fir_calc_filter(f_s_remain, f_pb, f_sb, pb_attn_remain, a_sb, order = fir_N, coef_bits = coef_bits, H_nr_points = H_size)


    #============================================================
    # 
    #============================================================

    hb1_H_no_decim  = H_unfold(hb1_H, 12)[::12]
    hb2_H_no_decim  = H_unfold(hb2_H, 24)[::24]
    fir_H_no_decim  = H_unfold(fir_H, 48)[::48]

    cic_hb1_H           = cic_H * hb1_H_no_decim
    cic_hb1_hb2_H       = cic_H * hb1_H_no_decim * hb2_H_no_decim
    cic_hb1_hb2_fir_H   = cic_H * hb1_H_no_decim * hb2_H_no_decim * fir_H_no_decim

    plt.figure(figsize=(10, 12))

    # ============================================================
    # CIC
    plt.subplot(4,2,1)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("CIC Filter")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(cic_H)))

    plt.subplot(4,2,2)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-260, 5])
    plt.gca().set_title("CIC Filter")
    plt.xlabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(cic_H)))

    # ============================================================
    # HB1
    plt.subplot(4,2,3)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("HB1 Filter")
    plt.xlabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(hb1_H_no_decim)))

    plt.subplot(4,2,4)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-260, 5])
    plt.gca().set_title("CIC + HB1 Filter")
    plt.xlabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(cic_hb1_H)))

    # ============================================================
    # HB2
    plt.subplot(4,2,5)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("HB2 Filter")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(hb2_H_no_decim)))

    plt.subplot(4,2,6)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-260, 5])
    plt.gca().set_title("CIC + HB1 + HB2 Filter")
    plt.xlabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(cic_hb1_hb2_H)))

    # ============================================================
    # FIR
    plt.subplot(4,2,7)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("FIR Filter")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    #plt.plot(cic_w, dB20(np.abs(cic_H)))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(fir_H_no_decim)))

    plt.subplot(4,2,8)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-260, 5])
    plt.gca().set_title("CIC + HB1 + HB2 + FIR Filter")
    plt.xlabel("Frequency")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w/np.pi/2*f_pdm, dB20(np.abs(cic_hb1_hb2_fir_H)))

    plt.tight_layout()
    plt.savefig("pdm_pcm2rtl_joint_filters.svg")
    if save_blog: plt.savefig(BLOG_PATH + "pdm_pcm2rtl_joint_filters.svg")

    # ============================================================
    # Decimate H

    plt.figure(figsize=(10, 5))

    H_decimated_len = len(cic_hb1_hb2_fir_H)//48
    H_decimated = np.zeros(H_decimated_len)

    for i in range(0, 48):

        if i%2 == 0:
            H_decimated = H_decimated + cic_hb1_hb2_fir_H[i*H_decimated_len:(i+1)*H_decimated_len]
        else:
            H_decimated = H_decimated + np.flip(cic_hb1_hb2_fir_H[i*H_decimated_len:(i+1)*H_decimated_len])

    plt.subplot(2,1,1)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2/48])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("After Decimation - Full Range")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w[0:len(H_decimated)]/np.pi/2*f_pdm, dB20(np.abs(H_decimated)))

    plt.subplot(2,1,2)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pb * 1.2])
    plt.gca().set_ylim([-a_pb*1.5, a_pb*1.5])
    plt.gca().set_title("After Decimation - Pass Band")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(cic_w[0:len(H_decimated)]/np.pi/2*f_pdm, dB20(np.abs(H_decimated)))


    plt.tight_layout()
    plt.savefig("pdm_pcm2rtl_joint_filters_after_decimation.svg")
    if save_blog: plt.savefig(BLOG_PATH + "pdm_pcm2rtl_joint_filters_after_decimation.svg")

    #============================================================
    # Write all filter parameters are json 
    #============================================================

    all_filters = [
            {
                'name'          : "CIC",
                'is_cic'        : True,
                'decimation'    : 12,
                'cic_order'     : 4,
            },
            {
                'name'          : "HB1",
                'is_fir'        : True,
                'is_halfband'   : True,
                'decimation'    : 2, 
                'coefs'         : hb1_h.tolist(),
            },
            {
                'name'          : "HB2",
                'is_fir'        : True,
                'is_halfband'   : True,
                'decimation'    : 2, 
                'coefs'         : hb2_h.tolist(),
            },
            {
                'name'          : "FIR",
                'is_fir'        : True,
                'is_halfband'   : False,
                'decimation'    : 2, 
                'coefs'         : fir_h.tolist(),
            },
        ]

    with open("pdm_pcm_filters.json", 'w') as pdm_pcm_filters:
        json.dump(all_filters, pdm_pcm_filters, indent=4)

