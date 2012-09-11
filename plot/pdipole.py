# pdipole.py - plot dipole function
#
# v 1.0.0
# rev 2012-09-11 (SL: changed input to file prefix)
# last major: (SL: created)

import matplotlib.pyplot as plt
import numpy as np
from neuron import h as nrn
from axes_create import fig_std

def pdipole(file_prefix):
    # ddipole is dipole data
    file_name = file_prefix + '.dat'
    ddipole = np.loadtxt(open(file_name, 'rb'))

    # these are the vectors for now, but this is going to change
    t_vec = ddipole[:, 0]
    dp_total = ddipole[:, 1]

    testfig = fig_std()
    testfig.ax0.plot(t_vec, dp_total)
    # testfig.ax0.set_ylim(-4e4, 3e4)

    plt.savefig(file_prefix+'.png')
    testfig.close()
