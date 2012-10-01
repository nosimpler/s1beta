# praster.py - plot dipole function
#
# v 1.2.5
# rev 2012-10-01 (SL: imported)
# last major:

import os
import numpy as np
import matplotlib.pyplot as plt
from neuron import h as nrn
from axes_create import fig_std
import spikefn as spikefn

# file_info is (rootdir, subdir, 
def praster(gid_dict, tstop, file_name, dfig):
    # ddipole is dipole data
    s_dict = spikefn.spikes_from_file(gid_dict, file_name)

    # split to find file prefix
    file_prefix = file_name.split('/')[-1].split('.')[0]

    # create standard fig and axes
    testfig = fig_std()
    spikefn.spike_png(testfig.ax0, s_dict)

    # testfig.ax0.plot(t_vec, dp_total)
    testfig.ax0.set_xlim(0., tstop)

    fig_name = os.path.join(dfig, file_prefix+'.png')

    plt.savefig(fig_name)
    testfig.close()
