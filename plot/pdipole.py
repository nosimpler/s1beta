# pdipole.py - plot dipole function
#
# v 0.4.6
# rev 2012-08-24 (SL: created)
# last major:

import matplotlib.pyplot as plt
import numpy as np
from neuron import h as nrn
from axes_create import fig_std

def pdipole(file_name):
    # ddipole is dipole data
    ddipole = np.loadtxt(open(file_name, 'rb'))

    # these are the vectors for now, but this is going to change
    t_vec = ddipole[:, 0]
    dp_total = ddipole[:, 2]

    testfig = fig_std()
    testfig.ax0.plot(t_vec, dp_total)

    plt.savefig('dipoletest.png')
    testfig.close()
