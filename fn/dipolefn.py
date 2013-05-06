# dipolefn.py - dipole-based analysis functions
#
# v 1.7.51irec
# rev 2013-05-06 (SL: changed how FigDipoleExp() is called, not totally tested)
# last major: (SL: added pdipole_grid() but incomplete)

import fileio as fio
import numpy as np
import itertools as it
import ast
import os
import paramrw
import spikefn 
import specfn
import matplotlib.pyplot as plt
from neuron import h as nrn
import axes_create as ac

# class Dipole() is for a single set of f_dpl and f_param
# some usage: dpl = Dipole(file_dipole, file_param)
# this gives dpl.t and dpl.dpl
class Dipole():
    def __init__(self, f_dpl):
        self.__parse_f(f_dpl)

    def __parse_f(self, f_dpl):
        x = np.loadtxt(open(f_dpl, 'r'))
        self.t = x[:, 0]
        self.dpl = x[:, 1]

        # assume these are present if there are enough vectors
        if x.shape[1] > 3:
            self.dpl_L2 = x[:, 2]
            self.dpl_L5 = x[:, 3]

    # standard dipole baseline in this model is -50.207 fAm per pair of pyr cells in network
    # ext function to renormalize
    def baseline_renormalize(self, f_param):
        N_pyr_x = paramrw.find_param(f_param, 'N_pyr_x')
        N_pyr_y = paramrw.find_param(f_param, 'N_pyr_y')

        # N_pyr cells in grid. This is per layer.
        N_pyr = N_pyr_x * N_pyr_y

        # dipole offset calculation: increasing number of pyr cells (L2 and L5, simultaneously)
        # with no inputs, resulted in a roughly linear, roughly stationary (100 ms) dipole baseline
        # of -50.207 fAm. This represents the resultant correction.
        dpl_offset = N_pyr * 50.207

        # simple baseline shift of the dipole
        self.dpl += dpl_offset

# ddata is a fio.SimulationPaths() object
def calc_aggregate_dipole(ddata):
    for expmt_group in ddata.expmt_groups:
        # create the filename
        dexp = ddata.dexpmt_dict[expmt_group]
        fname_short = '%s-%s-dpl' % (ddata.sim_prefix, expmt_group)
        fname_data = os.path.join(dexp, fname_short + '.txt')

        # grab the list of raw data dipoles and assoc params in this expmt
        dpl_list = ddata.file_match(expmt_group, 'rawdpl')
        param_list = ddata.file_match(expmt_group, 'param')

        for f_dpl, f_param in it.izip(dpl_list, param_list):
            dpl = Dipole(f_dpl)
            # dpl.baseline_renormalize(f_param)

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

        # write this data to the file
        with open(fname_data, 'w') as f:
            for t, x in it.izip(t_vec, x_dpl):
                f.write("%03.3f\t%5.4f\n" % (t, x))

# calculate stimulus evoked dipole
def calc_avgdpl_stimevoked(ddata):
    for expmt_group in ddata.expmt_groups:
        # create the filename
        dexp = ddata.dexpmt_dict[expmt_group]
        fname_short = '%s-%s-dpl' % (ddata.sim_prefix, expmt_group)
        fname_data = os.path.join(dexp, fname_short + '.txt')

        # grab the list of raw data dipoles and assoc params in this expmt
        fdpl_list = ddata.file_match(expmt_group, 'rawdpl')
        param_list = ddata.file_match(expmt_group, 'param')
        spk_list = ddata.file_match(expmt_group, 'rawspk')

        # actual list of Dipole() objects
        dpl_list = [Dipole(fdpl) for fdpl in fdpl_list]
        t_truncated = []

        # iterate through the lists, grab the spike time, phase align the signals,
        # cut them to length, and then mean the dipoles
        for dpl, f_spk, f_param in it.izip(dpl_list, spk_list, param_list):
            _, p = paramrw.read(f_param)

            # grab the corresponding relevant starting spike time
            s = spikefn.spikes_from_file(f_param, f_spk)
            s = spikefn.alpha_feed_verify(s, p)
            s = spikefn.add_delay_times(s, p)

            # t_evoked is the same for all of the cells in these simulations
            t_evoked = s['evprox0'].spike_list[0][0]

            # attempt to give a 50 ms buffer
            if t_evoked > 50.:
                t0 = t_evoked - 50.
            else:
                t0 = t_evoked

            # truncate the dipole related vectors
            dpl.t = dpl.t[dpl.t > t0]
            dpl.dpl = dpl.dpl[dpl.t > t0]
            t_truncated.append(dpl.t[0])

        # find the t0_max value to compare on other dipoles
        t_truncated -= np.max(t_truncated)

        for dpl, t_adj in it.izip(dpl_list, t_truncated):
            # negative numbers mean that this vector needs to be shortened by that many ms
            T_new = dpl.t[-1] + t_adj
            dpl.dpl = dpl.dpl[dpl.t < T_new]
            dpl.t = dpl.t[dpl.t < T_new]

            if dpl is dpl_list[0]:
                dpl_total = dpl.dpl

            else:
                dpl_total += dpl.dpl

        dpl_mean = dpl_total / len(dpl_list)
        t_dpl = dpl_list[0].t

        # write this data to the file
        with open(fname_data, 'w') as f:
            for t, x in it.izip(t_dpl, dpl_mean):
                f.write("%03.3f\t%5.4f\n" % (t, x))

# plot a dipole to an axis from corresponding dipole and param files
def pdipole_ax(a, f_dpl, f_param):
    dpl = Dipole(f_dpl)
    dpl.baseline_renormalize(f_param)

    a.plot(dpl.t, dpl.dpl)

    # any further xlim sets can be done by whoever wants to do them later
    a.set_xlim((0., dpl.t[-1]))

    # at least make the ylim symmetrical about 0
    ylim = a.get_ylim()
    abs_y_max = np.max(np.abs(ylim))
    ylim = (-abs_y_max, abs_y_max)
    a.set_ylim(ylim)

    # return the actual time in form of xlim. ain't pretty but works
    return a.get_xlim()

# pdipole is for a single dipole file, should be for a 
# single dipole file combination (incl. param file)
# this should be done with an axis input too
# two separate functions, a pdipole kernel function and a specific function for this simple plot
def pdipole(f_dpl, f_param, dfig, key_types, plot_dict):
    # dpl is an obj of Dipole() class
    dpl = Dipole(f_dpl)
    dpl.baseline_renormalize(f_param)

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

    # sorry about the parity between vars here and above with xmin/xmax
    if plot_dict['ymin'] is None or plot_dict['ymax'] is None:
        pass
    else:
        f.ax0.set_ylim(plot_dict['ymin'], plot_dict['ymax'])

    # grabbing the p_dict from the f_param
    _, p_dict = paramrw.read(f_param)

    # useful for title strings
    title_str = ac.create_title(p_dict, key_types)
    f.f.suptitle(title_str)

    # create new fig name
    fig_name = os.path.join(dfig, file_prefix+'.png')

    # savefig
    plt.savefig(fig_name, dpi=300)
    f.close()

# plot vertical lines corresponding to the evoked input times
# for each individual simulation/trial
def pdipole_evoked(dfig, f_dpl, f_spk, f_param, ylim=[]):
    gid_dict, p_dict = paramrw.read(f_param)

    # get the spike dict from the files
    s_dict = spikefn.spikes_from_file(f_param, f_spk)
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

    print spk_unique

    # plot the lines
    for key in spk_unique:
        print key, spk_unique[key]
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
    f_exp = ac.FigDipoleExp(ddata.expmt_groups)
    # f_exp = ac.FigDipoleExp(N_expmt_groups)

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
            dpl = Dipole(f_dpl)
            dpl.baseline_renormalize(f_param)
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

# For a given ddata (SimulationPaths object), find the mean dipole
# over ALL trials in ALL conditions in EACH experiment
def pdipole_exp2(ddata):
    # grab the original dipole from a specific dir
    dproj = '/repo/data/s1'

    runtype = 'somethingotherthandebug'
    # runtype = 'debug'

    if runtype == 'debug':
        ddate = '2013-04-08'
        dsim = 'mubaseline-15-000'
        i_ctrl = 0
    else:
        ddate = raw_input('Short date directory? ')
        dsim = raw_input('Sim name? ')
        i_ctrl = ast.literal_eval(raw_input('Sim number: '))
    dcheck = os.path.join(dproj, ddate, dsim)

    # create a blank ddata structure
    ddata_ctrl = fio.SimulationPaths()
    dsim = ddata_ctrl.read_sim(dproj, dcheck)

    # find the mu_low and mu_high in the expmtgroup names
    # this means the group names must be well formed
    for expmt_group in ddata_ctrl.expmt_groups:
        if 'mu_low' in expmt_group:
            mu_low_group = expmt_group
        elif 'mu_high' in expmt_group:
            mu_high_group = expmt_group

    # choose the first [0] from the list of the file matches for mu_low
    fdpl_mu_low = ddata_ctrl.file_match(mu_low_group, 'rawdpl')[i_ctrl]
    fparam_mu_low = ddata_ctrl.file_match(mu_low_group, 'param')[i_ctrl]
    fspk_mu_low = ddata_ctrl.file_match(mu_low_group, 'rawspk')[i_ctrl]
    fspec_mu_low = ddata_ctrl.file_match(mu_low_group, 'rawspec')[i_ctrl]

    # choose the first [0] from the list of the file matches for mu_high
    fdpl_mu_high = ddata_ctrl.file_match(mu_high_group, 'rawdpl')[i_ctrl]
    fparam_mu_high = ddata_ctrl.file_match(mu_high_group, 'param')[i_ctrl]
    # fspk_mu_high = ddata_ctrl.file_match(mu_high_group, 'rawspk')[i_ctrl]

    # grab the relevant dipole and renormalize it for mu_low
    dpl_mu_low = Dipole(fdpl_mu_low)
    dpl_mu_low.baseline_renormalize(fparam_mu_low)

    # grab the relevant dipole and renormalize it for mu_high
    dpl_mu_high = Dipole(fdpl_mu_high)
    dpl_mu_high.baseline_renormalize(fparam_mu_high)

    # input feed information
    s = spikefn.spikes_from_file(fparam_mu_low, fspk_mu_low)
    _, p_ctrl = paramrw.read(fparam_mu_low)
    s = spikefn.alpha_feed_verify(s, p_ctrl)
    s = spikefn.add_delay_times(s, p_ctrl)

    # hard coded bin count for now
    tstop = paramrw.find_param(fparam_mu_low, 'tstop')
    bins = spikefn.bin_count(150., tstop)

    # sim_prefix
    fprefix = ddata.sim_prefix

    # create the figure name
    fname_exp = '%s_dpl' % (fprefix)
    fname_exp_fig = os.path.join(ddata.dsim, fname_exp + '.png')

    # create one figure comparing across all
    N_expmt_groups = len(ddata.expmt_groups)
    ax_handles = [
        'spec',
        'input',
        'dpl_mu_low',
        'dpl_mu_high',
    ]
    f_exp = ac.FigDipoleExp(ax_handles)
    # f_exp = ac.FigDipoleExp(4)

    # plot the ctrl dipoles
    f_exp.ax['dpl_mu_low'].plot(dpl_mu_low.t, dpl_mu_low.dpl, color='k')
    f_exp.ax['dpl_mu_low'].hold(True)
    f_exp.ax['dpl_mu_high'].plot(dpl_mu_high.t, dpl_mu_high.dpl, color='k')
    f_exp.ax['dpl_mu_high'].hold(True)
    # f_exp.ax[2].plot(dpl_mu_low.t, dpl_mu_low.dpl, color='k')
    # f_exp.ax[2].hold(True)
    # f_exp.ax[3].plot(dpl_mu_high.t, dpl_mu_high.dpl, color='k')
    # f_exp.ax[3].hold(True)

    # function creates an f_exp.ax_twinx list and returns the index of the new feed
    ax_twin_name = f_exp.create_axis_twinx('input')
    if not ax_twin_name:
        print "You've got bigger problems, I'm afraid"
    # n_dist = f_exp.create_axis_twinx(1)

    # input hist information: predicated on the fact that the input histograms
    # should be identical for *all* of the inputs represented in this figure
    spikefn.pinput_hist(f_exp.ax['input'], f_exp.ax_twinx['input'], s['alpha_feed_prox'].spike_list, s['alpha_feed_dist'].spike_list, n_bins)
    # spikefn.pinput_hist(f_exp.ax[1], f_exp.ax_twinx[n_dist], s['alpha_feed_prox'].spike_list, s['alpha_feed_dist'].spike_list, n_bins)

    # grab the max counts for both hists
    # the [0] item of hist are the counts
    max_hist = np.max([np.max(hist[key][0]) for key in hist.keys()])
    ymax = 2 * max_hist

    # plot the spec here
    pc = specfn.pspec_ax(f_exp.ax['spec'], fspec_mu_low)
    # pc = specfn.pspec_ax(f_exp.ax[0], fspec_mu_low)
    print f_exp.ax[0].get_xlim()

    # deal with the axes here
    f_exp.ax_twinx['input'].set_ylim((ymax, 0))
    f_exp.ax['input'].set_ylim((0, ymax))
    # f_exp.ax_twinx[n_dist].set_ylim((ymax, 0))
    # f_exp.ax[1].set_ylim((0, ymax))

    f_exp.ax['input'].set_xlim((50., tstop))
    f_exp.ax_twinx['input'].set_xlim((50., tstop))

    # empty list for the aggregate dipole data
    dpl_exp = []

    # go through each expmt
    # calculation is extremely redundant
    for expmt_group in ddata.expmt_groups:
        # a little sloppy, just find the param file
        # this param file was for the baseline renormalization and
        # assumes it's the same in all for this expmt_group
        # also for getting the gid_dict, also assumed to be the same
        fparam = ddata.file_match(expmt_group, 'param')[0]

        # general check to see if the aggregate dipole data exists
        if 'mu_low' in expmt_group or 'mu_high' in expmt_group:
            # check to see if these files exist
            flist = ddata.find_aggregate_file(expmt_group, 'dpl')

            # if no file exists, then find one
            if not len(flist):
                calc_aggregate_dipole(ddata)
                flist = ddata.find_aggregate_file(expmt_group, 'dpl')

            # testing the first file
            list_spk = ddata.file_match(expmt_group, 'rawspk')
            list_s_dict = [spikefn.spikes_from_file(fparam, fspk) for fspk in list_spk]
            list_evoked = [s_dict['evprox0'].spike_list[0][0] for s_dict in list_s_dict]
            lines_spk = [f_exp.ax[2].axvline(x=x_val, linewidth=0.5, color='r') for x_val in list_evoked]
            lines_spk = [f_exp.ax[3].axvline(x=x_val, linewidth=0.5, color='r') for x_val in list_evoked]

        # handle mu_low and mu_high separately
        if 'mu_low' in expmt_group:
            dpl_mu_low_ev = Dipole(flist[0])
            dpl_mu_low_ev.baseline_renormalize(fparam)
            f_exp.ax['dpl_mu_low'].plot(dpl_mu_low_ev.t, dpl_mu_low_ev.dpl)

        elif 'mu_high' in expmt_group:
            dpl_mu_high_ev = Dipole(flist[0])
            dpl_mu_high_ev.baseline_renormalize(fparam)
            f_exp.ax['dpl_mu_high'].plot(dpl_mu_high_ev.t, dpl_mu_high_ev.dpl)

    f_exp.ax['dpl_mu_low'].set_xlim(50., tstop)
    f_exp.ax['dpl_mu_high'].set_xlim(50., tstop)

    f_exp.savepng(fname_exp_fig)
    f_exp.close()

# For a given ddata (SimulationPaths object), find the mean dipole
# over ALL trials in ALL conditions in EACH experiment
def pdipole_evoked_aligned(ddata):
    # grab the original dipole from a specific dir
    dproj = '/repo/data/s1'

    runtype = 'somethingotherthandebug'
    # runtype = 'debug'

    if runtype == 'debug':
        ddate = '2013-04-08'
        dsim = 'mubaseline-04-000'
        i_ctrl = 0
    else:
        ddate = raw_input('Short date directory? ')
        dsim = raw_input('Sim name? ')
        i_ctrl = ast.literal_eval(raw_input('Sim number: '))
    dcheck = os.path.join(dproj, ddate, dsim)

    # create a blank ddata structure
    ddata_ctrl = fio.SimulationPaths()
    dsim = ddata_ctrl.read_sim(dproj, dcheck)

    # find the mu_low and mu_high in the expmtgroup names
    # this means the group names must be well formed
    for expmt_group in ddata_ctrl.expmt_groups:
        if 'mu_low' in expmt_group:
            mu_low_group = expmt_group
        elif 'mu_high' in expmt_group:
            mu_high_group = expmt_group

    # choose the first [0] from the list of the file matches for mu_low
    fdpl_mu_low = ddata_ctrl.file_match(mu_low_group, 'rawdpl')[i_ctrl]
    fparam_mu_low = ddata_ctrl.file_match(mu_low_group, 'param')[i_ctrl]
    fspk_mu_low = ddata_ctrl.file_match(mu_low_group, 'rawspk')[i_ctrl]
    fspec_mu_low = ddata_ctrl.file_match(mu_low_group, 'rawspec')[i_ctrl]

    # choose the first [0] from the list of the file matches for mu_high
    fdpl_mu_high = ddata_ctrl.file_match(mu_high_group, 'rawdpl')[i_ctrl]
    fparam_mu_high = ddata_ctrl.file_match(mu_high_group, 'param')[i_ctrl]

    # grab the relevant dipole and renormalize it for mu_low
    dpl_mu_low = Dipole(fdpl_mu_low)
    dpl_mu_low.baseline_renormalize(fparam_mu_low)

    # grab the relevant dipole and renormalize it for mu_high
    dpl_mu_high = Dipole(fdpl_mu_high)
    dpl_mu_high.baseline_renormalize(fparam_mu_high)

    # input feed information
    s = spikefn.spikes_from_file(fparam_mu_low, fspk_mu_low)
    _, p_ctrl = paramrw.read(fparam_mu_low)
    s = spikefn.alpha_feed_verify(s, p_ctrl)
    s = spikefn.add_delay_times(s, p_ctrl)

    # find tstop, assume same over all. grab the first param file, get the tstop
    tstop = paramrw.find_param(fparam_mu_low, 'tstop')

    # hard coded bin count for now
    n_bins = spikefn.bin_count(150., tstop)

    # sim_prefix
    fprefix = ddata.sim_prefix

    # create the figure name
    fname_exp = '%s_dpl_align' % (fprefix)
    fname_exp_fig = os.path.join(ddata.dsim, fname_exp + '.png')

    # create one figure comparing across all
    N_expmt_groups = len(ddata.expmt_groups)
    ax_handles = [
        'spec',
        'input',
        'dpl_mu',
        'spk',
    ]
    f_exp = ac.FigDipoleExp(ax_handles)
    # f_exp = ac.FigDipoleExp(4)

    # plot the ctrl dipoles
    f_exp.ax['dpl_mu'].plot(dpl_mu_low.t, dpl_mu_low.dpl, color='k')
    f_exp.ax['dpl_mu'].hold(True)
    f_exp.ax['dpl_mu'].plot(dpl_mu_high.t, dpl_mu_high.dpl)

    # function creates an f_exp.ax_twinx list and returns the index of the new feed
    n_dist = f_exp.create_axis_twinx(1)

    # input hist information: predicated on the fact that the input histograms
    # should be identical for *all* of the inputs represented in this figure
    # places 2 histograms on two axes (meant to be one axis flipped)
    hists = spikefn.pinput_hist(f_exp.ax['input'], f_exp.ax_twinx['input'], s['alpha_feed_prox'].spike_list, s['alpha_feed_dist'].spike_list, n_bins)
    # hists = spikefn.pinput_hist(f_exp.ax[1], f_exp.ax_twinx[n_dist], s['alpha_feed_prox'].spike_list, s['alpha_feed_dist'].spike_list, n_bins)

    # grab the max counts for both hists
    # the [0] item of hist are the counts
    max_hist = np.max([np.max(hists[key][0]) for key in hists.keys()])
    ymax = 2 * max_hist

    # plot the spec here
    pc = specfn.pspec_ax(f_exp.ax['spec'], fspec_mu_low)
    # pc = specfn.pspec_ax(f_exp.ax[0], fspec_mu_low)

    # deal with the axes here
    f_exp.ax['input'].set_ylim((0, ymax))
    f_exp.ax_twinx['input'].set_ylim((ymax, 0))
    # f_exp.ax_twinx[n_dist].set_ylim((ymax, 0))
    # f_exp.ax[1].set_ylim((0, ymax))

    # f_exp.ax[1].set_xlim((50., tstop))

    # turn hold on
    f_exp.ax[dpl_mu].hold(True)

    # empty list for the aggregate dipole data
    dpl_exp = []

    # go through each expmt
    # calculation is extremely redundant
    for expmt_group in ddata.expmt_groups:
        # a little sloppy, just find the param file
        # this param file was for the baseline renormalization and
        # assumes it's the same in all for this expmt_group
        # also for getting the gid_dict, also assumed to be the same
        fparam = ddata.file_match(expmt_group, 'param')[0]

        # general check to see if the aggregate dipole data exists
        if 'mu_low' in expmt_group or 'mu_high' in expmt_group:
            # check to see if these files exist
            flist = ddata.find_aggregate_file(expmt_group, 'dpl')

            # if no file exists, then find one
            if not len(flist):
                calc_aggregate_dipole(ddata)
                flist = ddata.find_aggregate_file(expmt_group, 'dpl')

            # testing the first file
            list_spk = ddata.file_match(expmt_group, 'rawspk')
            list_s_dict = [spikefn.spikes_from_file(fparam, fspk) for fspk in list_spk]
            list_evoked = [s_dict['evprox0'].spike_list[0][0] for s_dict in list_s_dict]
            lines_spk = [f_exp.ax['dpl_mu'].axvline(x=x_val, linewidth=0.5, color='r') for x_val in list_evoked]
            lines_spk = [f_exp.ax['spk'].axvline(x=x_val, linewidth=0.5, color='r') for x_val in list_evoked]

        # handle mu_low and mu_high separately
        if 'mu_low' in expmt_group:
            dpl_mu_low_ev = Dipole(flist[0])
            dpl_mu_low_ev.baseline_renormalize(fparam)
            f_exp.ax['spk'].plot(dpl_mu_low_ev.t, dpl_mu_low_ev.dpl, color='k')

            # get xlim stuff
            t0 = dpl_mu_low_ev.t[0]
            T = dpl_mu_low_ev.t[-1]

        elif 'mu_high' in expmt_group:
            dpl_mu_high_ev = Dipole(flist[0])
            dpl_mu_high_ev.baseline_renormalize(fparam)
            f_exp.ax['spk'].plot(dpl_mu_high_ev.t, dpl_mu_high_ev.dpl, color='b')

    f_exp.ax['input'].set_xlim(50., tstop)

    for ax_name in f_exp.ax_handles[2:]:
        ax.set_xlim((t0, T))
    # for ax in f_exp.ax[2:]:
    #     ax.set_xlim((t0, T))

    # for ax in f_exp.ax_twinx:
    #     ax.set_xlim(500., tstop)

    # f_exp.ax[2].set_ylim(-2000., 6000)

    f_exp.savepng(fname_exp_fig)
    f_exp.close()

# create a grid of all dipoles in this dir
def pdipole_grid(ddata):
    # iterate through expmt_groups
    for expmt_group in ddata.expmt_groups:
        fname_short = "%s-%s-dpl.png" % (ddata.sim_prefix, expmt_group)
        fname = os.path.join(ddata.dsim, expmt_group, fname_short)

        # simple usage, just checks how many dipole files (total in an expmt)
        # and then plots dumbly to a grid
        dpl_list = ddata.file_match(expmt_group, 'rawdpl')
        param_list = ddata.file_match(expmt_group, 'param')

        # assume tstop is the same everywhere
        tstop = paramrw.find_param(param_list[0], 'tstop')

        # length of the dpl list
        N_dpl = len(dpl_list)

        # make a 5-col figure
        N_cols = 5

        # force int arithmetic
        # this is the BASE number of rows, one might be added!
        N_rows = int(N_dpl) / int(N_cols)

        # if the mod is not 0, add a row
        if (N_dpl % N_cols):
            N_rows += 1

        # print N_dpl, N_cols, N_rows
        f = ac.FigGrid(N_rows, N_cols, tstop)

        l = []
        r = 0
        for ax_list in f.ax:
            l.extend([(r,c) for c in range(len(ax_list))])
            r += 1

        # automatically truncates the loc list to the size of dpl_list
        for loc, fdpl, fparam in it.izip(l, dpl_list, param_list):
            r = loc[0]
            c = loc[1]
            pdipole_ax(f.ax[r][c], fdpl, fparam)

        f.savepng(fname)
        f.close()
