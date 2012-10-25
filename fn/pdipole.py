# pdipole.py - plot dipole function
#
# v 1.1.1
# rev 2012-09-26 (SL: uses new file input and directory)
# last major: (SL: changed input to file prefix)

import os
import matplotlib.pyplot as plt
import numpy as np
from neuron import h as nrn
from axes_create import fig_std

# file_info is (rootdir, subdir, 
def pdipole(file_name, dfig):
    # ddipole is dipole data
    ddipole = np.loadtxt(open(file_name, 'rb'))

    # split to find file prefix
    file_prefix = file_name.split('/')[-1].split('.')[0]

    # these are the vectors for now, but this is going to change
    t_vec = ddipole[:, 0]
    dp_total = ddipole[:, 1]

    testfig = fig_std()
    testfig.ax0.plot(t_vec, dp_total)
    # testfig.ax0.set_ylim(-4e4, 3e4)

    fig_name = os.path.join(dfig, file_prefix+'.png')

    plt.savefig(fig_name)
    testfig.close()
