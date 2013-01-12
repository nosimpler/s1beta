# praster.py - plot dipole function
#
# v 1.6.13
# rev 2013-01-12 (SL: set png res)
# last major: (SL: fixed file name)

import os
import numpy as np
import matplotlib.pyplot as plt
from neuron import h as nrn
from axes_create import fig_raster
import spikefn as spikefn

# file_info is (rootdir, subdir, 
def praster(gid_dict, tstop, file_spk, dfig):
    # ddipole is dipole data
    s_dict = spikefn.spikes_from_file(gid_dict, file_spk)

    s_dict_L2 = {}
    s_dict_L5 = {}
    s_dict_L2_extgauss = {}
    s_dict_L2_extpois = {}
    s_dict_L5_extgauss = {}
    s_dict_L5_extpois = {}

    # clean out s_dict destructively
    for key in s_dict.keys():
        # do this first to remove all extgauss feeds
        if 'extgauss' in key:
            if 'L2_' in key:
                s_dict_L2_extgauss[key] = s_dict.pop(key)

            elif 'L5_' in key:
                s_dict_L5_extgauss[key] = s_dict.pop(key)

        elif 'extpois' in key:
            # s_dict_extpois[key] = s_dict.pop(key)
            if 'L2_' in key:
                s_dict_L2_extpois[key] = s_dict.pop(key)

            elif 'L5_' in key:
                s_dict_L5_extpois[key] = s_dict.pop(key)

        # L2 next
        elif 'L2_' in key:
            s_dict_L2[key] = s_dict.pop(key)

        elif 'L5_' in key:
            s_dict_L5[key] = s_dict.pop(key)

    # split to find file prefix
    file_prefix = file_spk.split('/')[-1].split('.')[0]

    # create standard fig and axes
    f = fig_raster(tstop)
    spikefn.spike_png(f.ax['L2'], s_dict_L2)
    spikefn.spike_png(f.ax['L5'], s_dict_L5)
    spikefn.spike_png(f.ax['L2_extpois'], s_dict_L2_extpois)
    spikefn.spike_png(f.ax['L2_extgauss'], s_dict_L2_extgauss)
    spikefn.spike_png(f.ax['L5_extpois'], s_dict_L5_extpois)
    spikefn.spike_png(f.ax['L5_extgauss'], s_dict_L5_extgauss)

    # testfig.ax0.plot(t_vec, dp_total)
    fig_name = os.path.join(dfig, file_prefix+'.png')
    # fig_name = os.path.join(dfig, file_prefix+'.eps')

    plt.savefig(fig_name, dpi=300)
    f.close()
