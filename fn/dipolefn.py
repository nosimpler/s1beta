# dipolefn.py - dipole-based analysis functions
#
# v 1.7.38
# rev 2013-04-01 (SL: pdipole_exp now does one major aggregate output in addition)
# last major: (SL: renamed from pdipole.py)

import fileio as fio
import numpy as np
import itertools as it
import os
import paramrw
import spikefn 
import matplotlib.pyplot as plt
from neuron import h as nrn
import axes_create as ac

# class Dipole() is for a single set of f_dpl and f_param
class Dipole():
    def __init__(self, f_dpl, f_param):
        self.__parse_f(f_dpl, f_param)

    def __parse_f(self, f_dpl, f_param):
        x = np.loadtxt(open(f_dpl, 'r'))
        self.t = x[:, 0]
        self.dpl = x[:, 1]

        # grab the number of cells
        self.gid_dict, self.p = paramrw.read(f_param)

        self.p['N_pyr_x']

    # standard dipole baseline in this model is -50.207 fAm per pair of pyr cells in network
    # ext function to renormalize
    def baseline_renormalize(self):
        # N_pyr cells in grid. This is per layer.
        N_pyr = self.p['N_pyr_x'] * self.p['N_pyr_y']

        # dipole offset calculation: increasing number of pyr cells (L2 and L5, simultaneously)
        # with no inputs, resulted in a roughly linear, roughly stationary (100 ms) dipole baseline
        # of -50.207 fAm. This represents the resultant correction
        dpl_offset = N_pyr * 50.207

        # simple baseline shift of the dipole
        self.dpl += dpl_offset

# pdipole is for a single dipole file, should be for a 
# single dipole file combination (incl. param file)
# this should be done with an axis input too
# two separate functions, a pdipole kernel function and a specific function for this simple plot
def pdipole(f_dpl, f_param, dfig, key_types, plot_dict):
    # dpl is an obj of Dipole() class
    dpl = Dipole(f_dpl, f_param)
    dpl.baseline_renormalize()

    # split to find file prefix
    file_prefix = f_dpl.split('/')[-1].split('.')[0]

    # get xmin and xmax from the plot_dict
    if plot_dict['xmin'] is None:
        xmin = 0.
    else:
        xmin = plot_dict['xmin']

    if plot_dict['xmax'] is None:
        xmax = dpl.p['tstop']
    else:
        xmax = plot_dict['xmax']

    # truncate them using logical indexing
    t_range = dpl.t[(dpl.t >= xmin) & (dpl.t <= xmax)]
    dpl_range = dpl.dpl[(dpl.t >= xmin) & (dpl.t <= xmax)]

    f = ac.FigStd()
    f.ax0.plot(t_range, dpl_range)
    # f.ax0.plot(dpl.t, dpl.dpl)

    # sorry about the parity between vars here and above with xmin/xmax
    if plot_dict['ymin'] is None or plot_dict['ymax'] is None:
        pass
    else:
        f.ax0.set_ylim(plot_dict['ymin'], plot_dict['ymax'])

    title_str = ac.create_title(dpl.p, key_types)
    # title_str = ac.create_title(p_dict, key_types)
    f.f.suptitle(title_str)

    # create new fig name
    fig_name = os.path.join(dfig, file_prefix+'.png')

    # savefig
    plt.savefig(fig_name, dpi=300)
    f.close()

# # pdipole is for a single dipole file, should be for a 
# # single dipole file combination (incl. param file)
# def pdipole(f_dpl, dfig, p_dict, key_types, plot_dict):
#     # ddipole is dipole data
#     ddipole = np.loadtxt(open(f_dpl, 'rb'))
# 
#     # split to find file prefix
#     file_prefix = f_dpl.split('/')[-1].split('.')[0]
# 
#     # get xmin and xmax from the plot_dict
#     if plot_dict['xmin'] is None:
#         xmin = 0.
#     else:
#         xmin = plot_dict['xmin']
# 
#     if plot_dict['xmax'] is None:
#         xmax = p_dict['tstop']
#     else:
#         xmax = plot_dict['xmax']
# 
#     # take the whole vectors
#     t_vec = ddipole[:, 0]
#     dp_total = ddipole[:, 1]
# 
#     # now truncate them using logical indexing
#     t_vec_range = t_vec[(t_vec >= xmin) & (t_vec <= xmax)]
#     dp_range = dp_total[(t_vec >= xmin) & (t_vec <= xmax)]
# 
#     f = ac.FigStd()
#     f.ax0.plot(t_vec, dp_total)
# 
#     # sorry about the parity between vars here and above with xmin/xmax
#     if plot_dict['ymin'] is None or plot_dict['ymax'] is None:
#         pass
#     else:
#         f.ax0.set_ylim(plot_dict['ymin'], plot_dict['ymax'])
# 
#     title_str = ac.create_title(p_dict, key_types)
#     f.f.suptitle(title_str)
#     # title = [key + ': %2.1f' % p_dict[key] for key in key_types['dynamic_keys']]
# 
#     fig_name = os.path.join(dfig, file_prefix+'.png')
# 
#     plt.savefig(fig_name, dpi=300)
#     f.close()

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

    f = ac.FigStd()

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
    f = ac.FigDplWithHist()

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

    title_str = ac.create_title(p_dict, key_types)
    f.f.suptitle(title_str)
    # title = [key + ': %2.1f' % p_dict[key] for key in key_types['dynamic_keys']]

    fig_name = os.path.join(dfig, file_prefix+'.png')
    # fig_name = 'hist_test.png'

    plt.savefig(fig_name)
    f.close()

# For a given ddata (SimulationPaths object), find the mean dipole
# over ALL trials in ALL conditions in EACH experiment
def pdipole_exp(ddata, ylim=[]):
    # sim_prefix
    fprefix = ddata.sim_prefix

    # create the figure name
    fname_exp = '%s_dpl' % (fprefix)
    fname_exp_fig = os.path.join(ddata.dsim, fname_exp + '.png')

    # create one figure comparing across all
    N_expmt_groups = len(ddata.expmt_groups)
    f_exp = ac.FigDipoleExp(N_expmt_groups)

    # empty list for the aggregate dipole data
    dpl_exp = []

    # go through each expmt
    for expmt_group in ddata.expmt_groups:
        # create the filename
        dexp = ddata.dexpmt_dict[expmt_group]
        fname_short = '%s-%s-dpl' % (fprefix, expmt_group)
        fname_data = os.path.join(dexp, fname_short + '.txt')
        fname_fig = os.path.join(ddata.dfig[expmt_group]['figdpl'], fname_short + '.png')

        # grab the list of raw data dipoles and assoc params in this expmt
        dpl_list = ddata.file_match(expmt_group, 'rawdpl')
        param_list = ddata.file_match(expmt_group, 'param')

        for f_dpl, f_param in it.izip(dpl_list, param_list):
        # for file in dpl_list:
            dpl = Dipole(f_dpl, f_param)
            dpl.baseline_renormalize()
            # x_tmp = np.loadtxt(open(file, 'r'))

            # initialize and use x_dpl
            if f_dpl is dpl_list[0]:

                # assume time vec stays the same throughout
                t_vec = dpl.t
                x_dpl = dpl.dpl

            else:
                # guaranteed to exist after dpl_list[0]
                x_dpl += dpl.dpl

        # poor man's mean
        x_dpl /= len(dpl_list)

        # save this in a list to do comparison figure
        # order is same as ddata.expmt_groups
        dpl_exp.append(x_dpl)

        # write this data to the file
        with open(fname_data, 'w') as f:
            for t, x in it.izip(t_vec, x_dpl):
                f.write("%03.3f\t%5.4f\n" % (t, x))

        # create the plot I guess?
        f = ac.FigStd()
        f.ax0.plot(t_vec, x_dpl)

        if len(ylim):
            f.ax0.set_ylim(ylim)

        f.savepng(fname_fig)
        f.close()

    # plot the aggregate data using methods defined in FigDipoleExp()
    f_exp.plot(t_vec, dpl_exp)

    # attempt at setting titles
    for ax, expmt_group in it.izip(f_exp.ax, ddata.expmt_groups):
        ax.set_title(expmt_group)

    f_exp.savepng(fname_exp_fig)
    f_exp.close()
