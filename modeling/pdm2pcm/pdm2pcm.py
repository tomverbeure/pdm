#! /usr/bin/env python3

import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import EngFormatter

from scipy import signal
from filter_lib import *

import json

plot_cic_decimation_passband_droop  = True
plot_cic_stages_passband_droop      = True
passband_droop_table                = False
stopband_attenuation_table          = False
passband_stopband_attenuation_table = False
number_of_muls_table                = False
plot_pdm2pcm_filters                = True

save_blog = False

import platform
if platform.system() == "Darwin":
    BLOG_PATH = "/Users/tom/projects/tomverbeure.github.io/assets/pdm/pdm2pcm/"
else:
    BLOG_PATH = "/home/tom/projects/tomverbeure.github.io/assets/pdm/pdm2pcm/"

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


cic_differential_delay  = 1


if plot_cic_decimation_passband_droop:
    #============================================================
    # CIC Passband droop vs Decimation Ratio
    #============================================================
    cic_order = 5 

    plt.figure(figsize=(10, 4))

    plt.subplot(111)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-130, 5])
    plt.title("%d CIC Stages - All Decimation Ratios - Input Range" % cic_order)
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))

    for decim in [2, 3, 4, 6, 8, 12, 16, 24, 48]:

        h_cic = cic_filter(decim, cic_order)

        h_cic_stats = FilterStats(h_cic, fsample = f_pdm, fcutoff = f_pb, fstop = f_sb, N = (16384//decim//2)*decim*2)
        plt.plot(h_cic_stats.freqs[h_cic_stats.x_mask] * f_pdm, h_cic_stats.Hdb, label="Ratio: %d" % (decim))

        print("decim: %d - pass band attn: %f" % (decim, h_cic_stats.attn_at(f_pb)))

    rect = plt.Rectangle([1000, -5], 24000, 8, fill = False)
    plt.gca().annotate("output BW: 0 to 24 kHz", [15000, -8], [30000, -40], arrowprops=dict(facecolor='black', shrink=1))
    plt.gca().add_patch(rect)
    plt.legend(loc=1)

    plt.savefig("cic_ratios_overview.svg")
    if save_blog: plt.savefig(BLOG_PATH + "cic_ratios_overview.svg")

    plt.figure(figsize=(10, 4))
    plt.title("%d CIC Stages - All Decimation Ratios - Output Range" % cic_order)
    plt.subplot(111)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_out/2])
    plt.gca().set_ylim([-0.5, 0.5])
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))

    for decim in [2, 3, 4, 6, 8, 12, 16, 24, 48]:
        print(decim)
        mov_avg_length  = decim * cic_differential_delay

        # Single stage CIC filter
        h_cic_single = np.ones(mov_avg_length) / mov_avg_length
    
        h_cic = h_cic_single
        for i in range(cic_order-1):
            h_cic = np.convolve(h_cic, h_cic_single)

        h_cic_stats = FilterStats(h_cic, fsample = f_pdm, fcutoff = f_pb, fstop = f_sb, N = (16384//decim//2)*decim*2)
        plt.plot(h_cic_stats.freqs[h_cic_stats.x_mask] * f_pdm, h_cic_stats.Hdb, label="Ratio: %d" % (decim))

    rect = plt.Rectangle([100, -a_pb], f_pb-100, 2*a_pb, fill = False)
    plt.gca().annotate("pass band: 0 to %dkHz, ripple: %.01fdB" % (f_pb/1000, a_pb), [f_pb/4*3, 0.15], [f_pb/2 * 2, 0.3], arrowprops=dict(shrink=1))
    plt.gca().add_patch(rect)

    plt.legend(loc=1)
    plt.savefig("cic_ratios_zoom.svg")
    if save_blog: plt.savefig(BLOG_PATH + "cic_ratios_zoom.svg")

if plot_cic_stages_passband_droop:
    #============================================================
    # CIC Passband droop vs Number of Stages
    #============================================================

    decim = 12 

    plt.figure(figsize=(10, 4))
    plt.title("%dx Decimation - 1 to 6 stages - Output Range" % decim)
    plt.subplot(111)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_out/2])
    plt.gca().set_ylim([-0.5, 0.5])
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))

    for cic_order in range(1, 7):
        print(cic_order)

        h_cic = cic_filter(decim, cic_order)

        h_cic_stats = FilterStats(h_cic, fsample = f_pdm, fcutoff = f_pb, fstop = f_sb, N = (16384//decim//2)*decim*2)
        plt.plot(h_cic_stats.freqs[h_cic_stats.x_mask] * f_pdm, h_cic_stats.Hdb, label="Stages: %d" % (cic_order))

    rect = plt.Rectangle([100, -a_pb], f_pb-100, 2*a_pb, fill = False)
    plt.gca().annotate("pass band: 0 to %dkHz, ripple: %.01fdB" % (f_pb/1000, a_pb), [f_pb/4*3, 0.15], [f_pb/2 * 2, 0.3], arrowprops=dict(shrink=1))
    plt.gca().add_patch(rect)

    plt.legend(loc=1)
    plt.savefig("cic_stages_zoom.svg")
    if save_blog: plt.savefig(BLOG_PATH + "cic_stages_zoom.svg")

if passband_droop_table:
    #============================================================
    # Create table with pass band ripple for a matrix of decimation/order combinations
    #============================================================

    s = ""

    s += "<table>\n"
    s += "<caption style=\"text-align:center\"><b>Pass Band Ripple (dB)</b><br/>Decimation Ratio / Nr of CIC Stages</caption>\n"
    s += "<tr>"
    s += "    <th></th>\n"
    for cic_order in [1,2,3,4,5,6]:
        s += "    <th>%d</th>\n" % cic_order

    s += "</tr>\n"

    for decim in [2, 3, 4, 6, 8, 12, 16, 24, 48]:
        s += "<tr>\n"
        s += "    <th>%d</th>\n" % decim

        for cic_order in [1,2,3,4,5,6]:

            h_cic = cic_filter(decim, cic_order)

            h_cic_stats = FilterStats(h_cic, fsample = f_pdm, fcutoff = f_pb, fstop = f_sb, N = (16384//decim//2)*decim*2)

            pb_attn = h_cic_stats.attn_at(f_pb)
            sb_attn = h_cic_stats.attn_at(2*f_pdm/2/decim - f_sb)

            pb_ok = abs(pb_attn) <= a_pb/2

            if pb_ok:
                s += "    <td style=\"background-color:#a0e0a0\">%.4f</td>\n" % pb_attn
            else:
                s += "    <td style=\"background-color:#e0a0a0\">%.4f</td>\n" % pb_attn

        s += "</tr>\n"

    s += "</table>\n"

    print(s)

if stopband_attenuation_table:
    #============================================================
    # Create table with stop band attenuation for a matrix of decimation/order combinations
    #============================================================

    s = ""

    s += "<table>\n"
    s += "<caption style=\"text-align:center\"><b>Stop Band Attenuation (dB)</b><br/>Decimation Ratio / Nr of CIC Stages</caption>\n"
    s += "<tr>"
    s += "    <th></th>\n"
    for cic_order in [1,2,3,4,5,6]:
        s += "    <th>%d</th>\n" % cic_order

    s += "</tr>\n"

    for decim in [2, 3, 4, 6, 8, 12, 16, 24, 48]:
        s += "<tr>\n"
        s += "    <th>%d</th>\n" % decim

        for cic_order in [1,2,3,4,5,6]:

            h_cic = cic_filter(decim, cic_order)

            h_cic_stats = FilterStats(h_cic, fsample = f_pdm, fcutoff = f_pb, fstop = f_sb, N = (16384//decim//2)*decim*2)

            pb_attn = h_cic_stats.attn_at(f_pb)
            sb_attn = h_cic_stats.attn_at(2*f_pdm/2/decim - f_sb)

            sb_ok = abs(sb_attn) >= a_sb

            if sb_ok:
                s += "    <td style=\"background-color:#a0e0a0\">%.1f</td>\n" % sb_attn
            else:
                s += "    <td style=\"background-color:#e0a0a0\">%.1f</td>\n" % sb_attn

        s += "</tr>\n"

    s += "</table>\n"

    print(s)

if passband_stopband_attenuation_table:
    #============================================================
    # Create table with pass band ripple and stop band attenuation for a matrix of decimation/order combinations
    #============================================================

    s = ""

    s += "<table>\n"
    s += "<caption style=\"text-align:center\"><b>Pass Band/Stop Band Attenuation (dB)</b><br/>Decimation Ratio / Nr of CIC Stages</caption>\n"
    s += "<tr>"
    s += "    <th></th>\n"
    for cic_order in [1,2,3,4,5,6]:
        s += "    <th>%d</th>\n" % cic_order

    s += "</tr>\n"

    for decim in [2, 3, 4, 6, 8, 12, 16, 24, 48]:
        s += "<tr>\n"
        s += "    <th>%d</th>\n" % decim

        for cic_order in [1,2,3,4,5,6]:

            h_cic = cic_filter(decim, cic_order)

            h_cic_stats = FilterStats(h_cic, fsample = f_pdm, fcutoff = f_pb, fstop = f_sb, N = (16384//decim//2)*decim*2)

            pb_attn = h_cic_stats.attn_at(f_pb)
            sb_attn = h_cic_stats.attn_at(2*f_pdm/2/decim - f_sb)

            pb_ok = abs(pb_attn) <= a_pb/2
            sb_ok = abs(sb_attn) >= a_sb

            if pb_ok and sb_ok:
                s += "    <td style=\"background-color:#a0e0a0\">%.4f<br/>%.1f</td>\n" % (pb_attn, sb_attn)
            else:
                s += "    <td style=\"background-color:#e0a0a0\">%.4f<br/>%.1f</td>\n" % (pb_attn, sb_attn)

        s += "</tr>\n"

    s += "</table>\n"

    print(s)

if number_of_muls_table:
    #============================================================
    # Number of muls table
    #============================================================

    cic_configs = [ 
        { "decim" :  6, "stages" : 3,                           "hb_stats" : [], "fir_stats" : [] },
        { "decim" :  8, "stages" : 4,   "single_fir" : False,   "hb_stats" : [], "fir_stats" : [] },
        { "decim" :  8, "stages" : 4,   "single_fir" : True,    "hb_stats" : [], "fir_stats" : [] },
        { "decim" : 12, "stages" : 4,                           "hb_stats" : [], "fir_stats" : [] },
        ]

    for cic_config in cic_configs:
        print("============================================================")
        print("decim: %d, stages: %d" % (cic_config["decim"], cic_config["stages"]) )
        print("============================================================")

        cic_decim   = cic_config["decim"]
        cic_order   = cic_config["stages"]

        total_muls  = 0
        hb_muls     = 0
        fir_muls    = 0

        h_cic = cic_filter(cic_decim, cic_order)

        h_cic_stats = FilterStats(h_cic, fsample = f_pdm, fcutoff = f_pb, fstop = f_sb, N = (16384//cic_decim//2)*cic_decim*2)

        cic_pb_attn = h_cic_stats.attn_at(f_pb)
        cic_sb_attn = h_cic_stats.attn_at(2*f_pdm/2/cic_decim - f_sb)

        decim_remain    = (f_pdm//cic_decim) // f_out
        f_s_remain      = f_pdm//cic_decim
        pb_attn_remain  = a_pb - abs(cic_pb_attn)

        print("After CIC: f_s = %d, decim = %d, pb_attn_remain: %.4fdB" % (f_s_remain, decim_remain, pb_attn_remain) )

        # Do as many half-band filters as there are factors of 2 in the remaining decimations
        while decim_remain % 2 == 0:
            print("------------------------------------------------------------")
            print("Half band: %d -> %d" % (f_s_remain, f_s_remain//2) )

            print("pb_attn_remain: %.5fdB" % pb_attn_remain)

            hb_N = half_band_find_optimal_N(f_s_remain, f_sb, pb_attn_remain, a_sb, verbose = False)
            (hb_h, hb_w, hb_H, hb_Rpb, hb_Rsb, hb_Hpb_min, hb_Hpb_max, hb_Hsb_max) = half_band_calc_filter(f_s_remain, f_sb, hb_N)

            muls = (hb_N/2 + 1) * f_s_remain/2
            hb_muls += muls
            total_muls += muls

            print("HB muls: %d * %d = %d" % (hb_N/2+1, f_s_remain/2, muls) )
            print("Total mul: %d" % total_muls)

            cic_config["hb_stats"].append({ "order" : hb_N, "f_out" : f_s_remain/2, "muls" : muls, "a_pb" : hb_Rpb })

            decim_remain //= 2
            f_s_remain //= 2
            pb_attn_remain -= abs(dB20(hb_Rpb))


        print("decim_remain: %d" % decim_remain)

        if decim_remain != 1 and not(cic_config["single_fir"]):
            print("------------------------------------------------------------")
            print("Decim FIR: %d -> %d" % (f_s_remain, f_s_remain/decim_remain) )

            print("pb_attn_remain: %.5fdB" % (pb_attn_remain))

            fir_N = fir_find_optimal_N(f_s_remain, f_sb, f_s_remain/decim_remain - f_sb, pb_attn_remain/2, a_sb, verbose = False)
            (fir_h, fir_w, fir_H, fir_Rpb, fir_Rsb, fir_Hpb_min, fir_Hpb_max, fir_Hsb_max) = fir_calc_filter(f_s_remain, f_sb, f_s_remain/decim_remain - f_sb, pb_attn_remain/2, a_sb, fir_N)

            muls = (fir_N + 1) * f_s_remain/decim_remain
            fir_muls += muls
            total_muls += muls

            print("FIR muls: %d * %d = %d" % (fir_N+1, f_s_remain/decim_remain, muls) )
            print("Total mul: %d" % total_muls)

            cic_config["fir_stats"].append({ "order": fir_N, "f_out": f_s_remain/decim_remain, "muls": muls, "a_pb": fir_Rpb })

            f_s_remain /= decim_remain
            decim_remain = 1
            pb_attn_remain /= 2

        print("------------------------------------------------------------")
        print("Final FIR: %d" % (f_s_remain) )
        print("f_pb: %f, f_sb: %f" % (f_pb, f_sb))
        print("pb_attn_remain: %.5fdB" % (pb_attn_remain))
        print("a_sb: %.1fdB" % (a_sb))

        fir_N = fir_find_optimal_N(f_s_remain, f_pb, f_sb, pb_attn_remain, a_sb, verbose = False)
        (fir_h, fir_w, fir_H, fir_Rpb, fir_Rsb, fir_Hpb_min, fir_Hpb_max, fir_Hsb_max) = fir_calc_filter(f_s_remain, f_pb, f_sb, pb_attn_remain, a_sb, fir_N)

        muls = (fir_N + 1) * f_s_remain/decim_remain
        fir_muls += muls
        total_muls += muls

        print("FIR muls: %d * %d = %d" % (fir_N+1, f_s_remain/decim_remain, muls) )
        print("Total mul: %d" % total_muls)

        cic_config["fir_stats"].append({ "order": fir_N, "f_out": f_s_remain/decim_remain, "muls": muls, "a_pb": fir_Rpb })

        cic_config["total_muls"] = total_muls


    s = ""
    s += "<table>\n"
    s += "<tr>\n"
    s += "    <th>CIC Config</th>\n"
    s += "    <th>HB1 mul/s</th>\n"
    s += "    <th>HB2 mul/s</th>\n"
    s += "    <th>HB3 mul/s</th>\n"
    s += "    <th>Decim FIR mul/s</th>\n"
    s += "    <th>Final FIR mul/s</th>\n"
    s += "    <th>Total mul/s</th>\n"
    s += "</tr>\n"
    for cic_config in cic_configs:
        s += "<tr>\n"
        s += "    <td>Decim:%d<br/>Stages:%d</td>\n" % (cic_config["decim"], cic_config["stages"])

        for hb_stat in cic_config["hb_stats"]:
            s += "    <td>%d x %dk = %dk</td>\n" % (hb_stat["order"]/2+1, hb_stat["f_out"]/1000, hb_stat["muls"]/1000)

        for dummy in range(3-len(cic_config["hb_stats"])):
            s += "    <td></td>\n"

        for dummy in range(2-len(cic_config["fir_stats"])):
            s += "    <td></td>\n"

        for fir_stat in cic_config["fir_stats"]:
            s += "    <td>%d x %dk = %dk</td>\n" % (fir_stat["order"]+1, fir_stat["f_out"]/1000, fir_stat["muls"]/1000)

        s += "    <td>%dk</td>\n" % (cic_config["total_muls"]/1000)
        s += "</tr>\n"
    
    s += "</table>\n"

    print(s)

if plot_pdm2pcm_filters:
    #============================================================
    # magnitude frequency plots for all the filter stages of the final architecture
    #============================================================
    plt.figure(figsize=(10, 12))


    #============================================================
    # CIC Filter
    #============================================================
    cic_decim       = 12
    cic_order       = 4


    h_cic = cic_filter(cic_decim, cic_order)
    h_cic_stats = FilterStats(h_cic, fsample = f_pdm, fcutoff = f_pb, fstop = f_sb, N = (16384//cic_decim//2)*cic_decim*2)

    plt.subplot(421)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_pdm/2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("CIC Filter - Frequency Reponse")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(h_cic_stats.freqs[h_cic_stats.x_mask] * f_pdm, h_cic_stats.Hdb)
    plt.plot([f_pb, f_pb], [-130, 5], "--", linewidth=1.0, label="Pass band")
    plt.plot([f_sb, f_sb], [-130, 5], "--", linewidth=1.0, label="Stop band")
    plt.plot([f_out/2, f_out/2], [-130, 5], "--", linewidth=1.0, label="BW out")
    plt.legend(loc=1)

    plt.subplot(422)
    plt.grid(True)
    plt.gca().set_title("Impulse Reponse")
    plt.gca().set_xlim([0, len(h_cic)-1])
    plt.stem(h_cic)

    cic_pb_attn = h_cic_stats.attn_at(f_pb)
    cic_sb_attn = h_cic_stats.attn_at(2*(f_pdm/2/cic_decim) - f_sb)

    decim_remain    = (f_pdm//cic_decim) // f_out
    f_s_remain      = f_pdm//cic_decim
    pb_attn_remain  = a_pb - abs(cic_pb_attn)

    #============================================================
    # HB1 Filter
    #============================================================

    hb1_N = half_band_find_optimal_N(f_s_remain, f_sb, pb_attn_remain, a_sb, verbose = False)
    (hb1_h, hb1_w, hb1_H, hb1_Rpb, hb1_Rsb, hb1_Hpb_min, hb1_Hpb_max, hb1_Hsb_max) = half_band_calc_filter(f_s_remain, f_sb, hb1_N)

    plt.subplot(423)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_s_remain/2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("Half-band Filter 1 - Frequency Response")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(hb1_w/np.pi/2*f_s_remain, dB20(np.abs(hb1_H)))
    plt.plot([f_pb, f_pb], [-130, 5], "--", linewidth=1.0, label="Pass band")
    plt.plot([f_sb, f_sb], [-130, 5], "--", linewidth=1.0, label="Stop band")
    plt.plot([f_out/2, f_out/2], [-130, 5], "--", linewidth=1.0, label="BW out")
    plt.legend(loc=1)

    plt.subplot(424)
    plt.grid(True)
    plt.gca().set_title("Impulse Reponse - %d Taps" % len(hb1_h))
    plt.gca().set_xlim([0, len(hb1_h)-1])
    plt.stem(hb1_h)

    decim_remain //= 2
    f_s_remain //= 2
    pb_attn_remain -= abs(dB20(hb1_Rpb))

    #============================================================
    # HB2 Filter
    #============================================================

    hb2_N = half_band_find_optimal_N(f_s_remain, f_sb, pb_attn_remain, a_sb, verbose = False)
    (hb2_h, hb2_w, hb2_H, hb2_Rpb, hb2_Rsb, hb2_Hpb_min, hb2_Hpb_max, hb2_Hsb_max) = half_band_calc_filter(f_s_remain, f_sb, hb2_N)

    plt.subplot(425)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_s_remain])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("Half-band Filter 2 - Frequency Response")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(hb2_w/np.pi/2*f_s_remain, dB20(np.abs(hb2_H)))
    plt.plot([f_pb, f_pb], [-130, 5], "--", linewidth=1.0, label="Pass band")
    plt.plot([f_sb, f_sb], [-130, 5], "--", linewidth=1.0, label="Stop band")
    plt.plot([f_out/2, f_out/2], [-130, 5], "--", linewidth=1.0, label="BW out")
    plt.plot([f_s_remain/2, f_s_remain/2], [-130, 5], "--", linewidth=1.0, label="BW in")
    plt.legend(loc=1)

    plt.subplot(426)
    plt.grid(True)
    plt.gca().set_title("Impulse Reponse - %d Taps" % len(hb2_h))
    plt.gca().set_xlim([0, len(hb2_h)-1])
    plt.stem(hb2_h)

    decim_remain //= 2
    f_s_remain //= 2
    pb_attn_remain -= abs(dB20(hb2_Rpb))

    #============================================================
    # FIR Filter
    #============================================================

    fir_N = fir_find_optimal_N(f_s_remain, f_pb, f_sb, pb_attn_remain, a_sb, verbose = False)
    (fir_h, fir_w, fir_H, fir_Rpb, fir_Rsb, fir_Hpb_min, fir_Hpb_max, fir_Hsb_max) = fir_calc_filter(f_s_remain, f_pb, f_sb, pb_attn_remain, a_sb, fir_N)

    plt.subplot(427)
    plt.grid(True)
    plt.gca().set_xlim([0.0, f_s_remain*2])
    plt.gca().set_ylim([-130, 5])
    plt.gca().set_title("Final FIR Filter - Frequency Response")
    plt.xlabel("Frequency")
    plt.ylabel("Attenuation (dB)")
    plt.gca().get_xaxis().set_major_formatter(EngFormatter(unit="Hz"))
    plt.plot(fir_w/np.pi/2*f_s_remain, dB20(np.abs(fir_H)))
    plt.plot([f_pb, f_pb], [-130, 5], "--", linewidth=1.0, label="Pass band")
    plt.plot([f_sb, f_sb], [-130, 5], "--", linewidth=1.0, label="Stop band")
    plt.plot([f_out/2, f_out/2], [-130, 5], "--", linewidth=1.0, label="BW out")
    plt.plot([f_s_remain/2, f_s_remain/2], [-130, 5], "--", linewidth=1.0, label="BW in")
    plt.legend(loc=1)

    plt.subplot(428)
    plt.grid(True)
    plt.gca().set_title("Impulse Reponse - %d Taps" % len(fir_h))
    plt.gca().set_xlim([0, len(fir_h)-1])
    plt.stem(fir_h)

    plt.tight_layout()
    plt.savefig("pdm2pcm_filters.svg")
    if save_blog: plt.savefig(BLOG_PATH + "pdm2pcm_filters.svg")


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


