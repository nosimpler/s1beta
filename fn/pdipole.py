# pdipole.py - plot dipole function
#
# v 1.7.11a
# rev 2013-01-30 (MS: Alpha feed histogram works when one feed does not exist)
# last major: (SL: pdipole_exp now takes in runtime ylim to set)

import os
import itertools as it
import matplotlib.pyplot as plt
import numpy as np
from neuron import h as nrn
from axes_create import FigStd, FigDplWithHist
import spikefn 

# file_info is (rootdir, subdir, 
def pdipole(file_name, dfig, p_dict, key_types):
    # ddipole is dipole data
    ddipole = np.loadtxt(open(file_name, 'rb'))

    # split to find file prefix
    file_prefix = file_name.split('/')[-1].split('.')[0]

    # these are the vectors for now, but this is going to change
    t_vec = ddipole[:, 0]
    dp_total = ddipole[:, 1]

    f = FigStd()
    f.ax0.plot(t_vec, dp_total)
    # f.ax0.set_ylim(-4e4, 3e4)

    title = [key + ': %2.1f' % p_dict[key] for key in key_types['dynamic_keys']]
    plt.title(title)

    fig_name = os.path.join(dfig, file_prefix+'.png')

    plt.savefig(fig_name, dpi=300)
    f.close()

# Plots dipole with histogram of alpha feed inputs
def pdipole_with_hist(f_dpl, f_spk, dfig, p_dict, gid_dict, key_types):
    # ddipole is dipole data
    ddipole = np.loadtxt(f_dpl)

    # split to find file prefix
    file_prefix = f_dpl.split('/')[-1].split('.')[0]

    # these are the vectors for now, but this is going to change
    t_vec = ddipole[:, 0]
    dp_total = ddipole[:, 1]

    # get feed input times.
    s_dict = spikefn.spikes_from_file(gid_dict, f_spk)

    # check for existance of alpha feed keys in s_dict.
    s_dict = spikefn.alpha_feed_verify(s_dict, p_dict)

    # Account for possible delays
    s_dict = spikefn.add_delay_times(s_dict, p_dict)

    # set number of bins for hist (150 bins/1000ms)
    bins = 150. * p_dict['tstop'] / 1000.

    # Plotting
    f = FigDplWithHist()

    # dipole
    f.ax['dipole'].plot(t_vec, dp_total)

    hist = {}

    # Proximal feed
    hist['feed_prox'] = f.ax['feed_prox'].hist(s_dict['alpha_feed_prox'].spike_list, bins, range=[t_vec[0], t_vec[-1]], color='red', label='Proximal feed')

    # Distal feed
    hist['feed_dist'] = f.ax['feed_dist'].hist(s_dict['alpha_feed_dist'].spike_list, bins, range=[t_vec[0], t_vec[-1]], color='green', label='Distal feed')

    # set hist axis properties
    f.set_hist_props(hist)

    # Add legend to histogram
    for key in f.ax.keys():
        if 'feed' in key:
            f.ax[key].legend()

    title = [key + ': %2.1f' % p_dict[key] for key in key_types['dynamic_keys']]
    plt.title(title)

    fig_name = os.path.join(dfig, file_prefix+'.png')
    # fig_name = 'hist_test.png'

    plt.savefig(fig_name)
    f.close()

# for a given ddata (SimulationPaths object), find the mean dipole
def pdipole_exp(ddata, ylim=[]):
    # sim_prefix
    fprefix = ddata.sim_prefix

    # go through each expmt
    for expmt_group in ddata.expmt_groups:
        # create the filename
        dexp = ddata.dexpmt_dict[expmt_group]
        fname_short = '%s-%s-dpl' % (fprefix, expmt_group)
        fname_data = os.path.join(dexp, fname_short + '.txt')
        fname_fig = os.path.join(ddata.dfig[expmt_group]['figdpl'], fname_short + '.png')

        # grab the list of raw data dipoles in this expmt
        dpl_list = ddata.file_match(expmt_group, 'rawdpl')

        for file in dpl_list:
            x_tmp = np.loadtxt(open(file, 'r'))
            if file is dpl_list[0]:
                # assume time vec stays the same throughout
                t_vec = x_tmp[:, 0]
                x_dpl = x_tmp[:, 1]

            else:
                x_dpl += x_tmp[:, 1]

        # poor man's mean
        x_dpl /= len(dpl_list)

        # write this data to the file
        with open(fname_data, 'w') as f:
            for t, x in it.izip(t_vec, x_dpl):
                f.write("%03.3f\t%5.4f\n" % (t, x))

        # create the plot I guess?
        f = FigStd()
        f.ax0.plot(t_vec, x_dpl)

        if len(ylim):
            f.ax0.set_ylim(ylim)

        f.savepng(fname_fig)
        f.close()
