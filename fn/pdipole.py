# pdipole.py - plot dipole function
#
# v 1.2.25
# rev 2012-11-01 (SL: changed figure handle locally)
# last major: (MS: title includes key/val pairs for changed vals)

import os
import matplotlib.pyplot as plt
import numpy as np
from neuron import h as nrn
from axes_create import fig_std

# file_info is (rootdir, subdir, 
def pdipole(file_name, dfig, p_dict, key_types):
    # ddipole is dipole data
    ddipole = np.loadtxt(open(file_name, 'rb'))

    # split to find file prefix
    file_prefix = file_name.split('/')[-1].split('.')[0]

    # these are the vectors for now, but this is going to change
    t_vec = ddipole[:, 0]
    dp_total = ddipole[:, 1]

    f = fig_std()
    f.ax0.plot(t_vec, dp_total)
    # f.ax0.set_ylim(-4e4, 3e4)

    title = [key + ': %2.1f' %p_dict[key] for key in key_types['dynamic_keys']]
    plt.title(title)

    fig_name = os.path.join(dfig, file_prefix+'.png')

    plt.savefig(fig_name)
    f.close()
