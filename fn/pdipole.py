# pdipole.py - plot dipole functions
#
# v 1.7.25
# rev 2013-02-20 (SL: major change to inputs of pdipole: last input is a dict of settings)
# last major: (SL: added pdipole_evoked)

import os
import itertools as it
import matplotlib.pyplot as plt
import numpy as np
from neuron import h as nrn
from axes_create import FigStd, FigDplWithHist
import spikefn 
import paramrw

# file_info is (rootdir, subdir, 
def pdipole(file_name, dfig, p_dict, key_types, plot_dict):
# def pdipole(file_name, dfig, p_dict, key_types, xlim=[0, 'tstop']):
    # ddipole is dipole data
    ddipole = np.loadtxt(open(file_name, 'rb'))

    # split to find file prefix
    file_prefix = file_name.split('/')[-1].split('.')[0]

    if plot_dict['xmin'] is None:
        xmin = 0.
    else:
        xmin = plot_dict['xmin']

    if plot_dict['xmax'] is None:
        xmax = p_dict['tstop']
    else:
        xmax = plot_dict['xmax']

    # take the whole vectors
    t_vec = ddipole[:, 0]
    dp_total = ddipole[:, 1]

    # now truncate them using logical indexing
    t_vec_range = t_vec[(t_vec >= xmin) & (t_vec <= xmax)]
    dp_range = dp_total[(t_vec >= xmin) & (t_vec <= xmax)]

    f = FigStd()
    f.ax0.plot(t_vec, dp_total)

    # sorry about the parity between vars here and above with xmin/xmax
    if plot_dict['ymin'] is None or plot_dict['ymax'] is None:
        pass
    else:
        f.ax0.set_ylim(plot_dict['ymin'], plot_dict['ymax'])

    title = [key + ': %2.1f' % p_dict[key] for key in key_types['dynamic_keys']]
    plt.title(title)

    fig_name = os.path.join(dfig, file_prefix+'.png')

    plt.savefig(fig_name, dpi=300)
    f.close()

# plot vertical lines corresponding to the evoked input times
# for each individual simulation/trial
def pdipole_evoked(dfig, f_dpl, f_spk, f_param, ylim=[]):
    gid_dict, p_dict = paramrw.read(f_param)

    # get the spike dict from the files
    s_dict = spikefn.spikes_from_file_pure(f_param, f_spk)
    s = s_dict.keys()
    s.sort()

    # create an empty dict 'spk_unique'
    spk_unique = dict.fromkeys([key for key in s_dict.keys() if key.startswith(('evprox', 'evdist'))])

    for key in spk_unique:
        spk_unique[key] = s_dict[key].unique_all(0)

    # draw vertical lines for each item in this

    # x_dipole is dipole data
    x_dipole = np.loadtxt(open(f_dpl, 'r'))

    # split to find file prefix
    file_prefix = f_dpl.split('/')[-1].split('.')[0]

    # # set xmin value
    # xmin = xlim[0] / p_dict['dt']

    # # set xmax value
    # if xlim[1] == 'tstop':
    #     xmax = p_dict['tstop'] / p_dict['dt']
    # else:
    #     xmax = xlim[1] / p_dict['dt']

    # these are the vectors for now, but this is going to change
    t_vec = x_dipole[:, 0]
    dp_total = x_dipole[:, 1]

    f = FigStd()

    # hold on
    f.ax0.hold(True)

    f.ax0.plot(t_vec, dp_total)

    lines_spk = dict.fromkeys(spk_unique)

    # plot the lines
    for key in spk_unique:
        x_val = spk_unique[key][0]
        lines_spk[key] = plt.axvline(x=x_val, linewidth=0.5, color='r')

    # title_txt = [key + ': {:.2e}' % p_dict[key] for key in key_types['dynamic_keys']]
    title_txt = 'test'
    f.ax0.set_title(title_txt)

    if ylim:
        f.ax0.set_ylim(ylim)

    fig_name = os.path.join(dfig, file_prefix+'.png')

    plt.savefig(fig_name, dpi=300)
    f.close()

# Plots dipole with histogram of alpha feed inputs
def pdipole_with_hist(f_dpl, f_spk, dfig, p_dict, gid_dict, key_types, xlim=[0., 'tstop']):
    # ddipole is dipole data
    ddipole = np.loadtxt(f_dpl)

    # split to find file prefix
    file_prefix = f_dpl.split('/')[-1].split('.')[0]

    # set xmin value
    xmin = xlim[0] / p_dict['dt']

    # set xmax value
    if xlim[1] == 'tstop':
        xmax = p_dict['tstop'] / p_dict['dt']
    else:
        xmax = xlim[1] / p_dict['dt']

    # these are the vectors for now, but this is going to change
    t_vec = ddipole[xmin:xmax+1, 0]
    dp_total = ddipole[xmin:xmax+1, 1]

    # get feed input times.
    s_dict = spikefn.spikes_from_file(gid_dict, f_spk)

    # check for existance of alpha feed keys in s_dict.
    s_dict = spikefn.alpha_feed_verify(s_dict, p_dict)

    # Account for possible delays
    s_dict = spikefn.add_delay_times(s_dict, p_dict)

    # set number of bins for hist (150 bins/1000ms)
    bins = 150. * (t_vec[-1] - t_vec[0]) / 1000.

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

# For a given ddata (SimulationPaths object), find the mean dipole
# over ALL trials in ALL conditions in EACH experiment
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
