# pdipole.py - plot dipole function
#
# v 1.2.23
# rev 2012-09-30 (MS: Added p_dict input for title generation, may change in future)
# last major: (SL: uses new file input and directory)

import os
import matplotlib.pyplot as plt
import numpy as np
from neuron import h as nrn
from axes_create import fig_std

# file_info is (rootdir, subdir, 
def pdipole(file_name, p_dict, dfig):
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
    plt.title('f_input_prox: %2.1f; f_input_dist: %2.1f' %(p_dict['f_input_prox'], p_dict['f_input_dist']))

    fig_name = os.path.join(dfig, file_prefix+'.png')

    plt.savefig(fig_name)
    testfig.close()
