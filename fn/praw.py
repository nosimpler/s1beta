# praw.py - all of the raw data types on one fig
#
# v 1.7.45
# rev 2013-04-23 (SL: created)
# last major:

import fileio as fio
import numpy as np
import itertools as it
import ast
import os
import paramrw
import dipolefn
import spikefn 
import specfn
import matplotlib.pyplot as plt
from neuron import h as nrn
import axes_create as ac

# For a given ddata (SimulationPaths object), find the mean dipole
# over ALL trials in ALL conditions in EACH experiment
# def praw(f_dpl, f_spk, f_spec, f_param):
def praw(ddata):
    # grab the original dipole from a specific dir
    dproj = '/repo/data/s1'

    # check on spec data
    specfn.generate_missing_spec(ddata)

    # test experiment
    expmt_group = ddata.expmt_groups[0]

    # iterate over exmpt groups
    for expmt_group in ddata.expmt_groups:
        dfig_dpl = ddata.dfig[expmt_group]['figdpl']

        # grab lists of files (l_)
        l_dpl = ddata.file_match(expmt_group, 'rawdpl')
        l_spk = ddata.file_match(expmt_group, 'rawspk')
        l_param = ddata.file_match(expmt_group, 'param')
        l_spec = ddata.file_match(expmt_group, 'rawspec')

        for f_dpl, f_spk, f_spec, f_param in it.izip(l_dpl, l_spk, l_spec, l_param):
            # into the pdipole directory, this will plot dipole, spec, and spikes
            # create the axis handle
            f = ac.FigDipoleExp(3)

            # create the figure name
            fprefix = fio.strip_extprefix(f_dpl) + '-dpl'
            fname = os.path.join(dfig_dpl, fprefix + '.png')

            xlim = dipolefn.pdipole_ax(f.ax[0], f_dpl, f_param)
            pc = specfn.pspec_ax(f.ax[1], f_spec)
            # f.f.colorbar(pc, ax=f.ax[1])

            # empty spike dict for L2 with keys that must match keys in s
            s_new = {
                'L2_pyramidal': None,
                'L2_basket': None,
            }
            s = spikefn.spikes_from_file(f_param, f_spk)

            # clean out s to get the stuff I care about plotting
            for key in s.iterkeys():   
                if key in s_new.keys():
                    s_new[key] = s[key]

            # resize xlim based on our 50 ms cutoff thingy
            xlim = (50., xlim[1])
            spikefn.spike_png(f.ax[2], s_new)
            # f.ax[1].set_xlim(xlim)
            f.ax[2].set_xlim(xlim)

            f.savepng(fname)
            f.close()

    # # choose the first [0] from the list of the file matches for mu_low
    # fdpl_mu_low = ddata_ctrl.file_match(mu_low_group, 'rawdpl')[i_ctrl]
    # fparam_mu_low = ddata_ctrl.file_match(mu_low_group, 'param')[i_ctrl]
    # fspk_mu_low = ddata_ctrl.file_match(mu_low_group, 'rawspk')[i_ctrl]
    # fspec_mu_low = ddata_ctrl.file_match(mu_low_group, 'rawspec')[i_ctrl]

    # # choose the first [0] from the list of the file matches for mu_high
    # fdpl_mu_high = ddata_ctrl.file_match(mu_high_group, 'rawdpl')[i_ctrl]
    # fparam_mu_high = ddata_ctrl.file_match(mu_high_group, 'param')[i_ctrl]

    # # grab the relevant dipole and renormalize it for mu_low
    # dpl_mu_low = Dipole(fdpl_mu_low)
    # dpl_mu_low.baseline_renormalize(fparam_mu_low)

    # # grab the relevant dipole and renormalize it for mu_high
    # dpl_mu_high = Dipole(fdpl_mu_high)
    # dpl_mu_high.baseline_renormalize(fparam_mu_high)

    # # input feed information
    # s = spikefn.spikes_from_file(fparam_mu_low, fspk_mu_low)
    # _, p_ctrl = paramrw.read(fparam_mu_low)
    # s = spikefn.alpha_feed_verify(s, p_ctrl)
    # s = spikefn.add_delay_times(s, p_ctrl)

    # # hard coded bin count for now
    # tstop = paramrw.find_param(fparam_mu_low, 'tstop')
    # bins = spikefn.bin_count(150., tstop)

    # # create the figure name
    # fname_exp = '%s_dpl' % (fprefix)
    # fname_exp_fig = os.path.join(ddata.dsim, fname_exp + '.png')

    # # create one figure comparing across all
    # N_expmt_groups = len(ddata.expmt_groups)
    # f_exp = ac.FigDipoleExp(4)

    # # plot the ctrl dipoles
    # f_exp.ax[2].plot(dpl_mu_low.t, dpl_mu_low.dpl, color='k')
    # f_exp.ax[2].hold(True)
    # f_exp.ax[3].plot(dpl_mu_high.t, dpl_mu_high.dpl, color='k')
    # f_exp.ax[3].hold(True)

    # # function creates an f_exp.ax_twinx list and returns the index of the new feed
    # n_dist = f_exp.create_axis_twinx(1)

    # # input hist information: predicated on the fact that the input histograms
    # # should be identical for *all* of the inputs represented in this figure
    # spikefn.pinput_hist(f_exp.ax[1], f_exp.ax_twinx[n_dist], s['alpha_feed_prox'].spike_list, s['alpha_feed_dist'].spike_list, n_bins)

    # # grab the max counts for both hists
    # # the [0] item of hist are the counts
    # max_hist = np.max([np.max(hist[key][0]) for key in hist.keys()])
    # ymax = 2 * max_hist

    # # plot the spec here
    # pc = specfn.pspec_ax(f_exp.ax[0], fspec_mu_low)
    # print f_exp.ax[0].get_xlim()

    # # deal with the axes here
    # f_exp.ax_twinx[n_dist].set_ylim((ymax, 0))
    # f_exp.ax[1].set_ylim((0, ymax))

    # f_exp.ax[1].set_xlim((50., tstop))
    # f_exp.ax_twinx[n_dist].set_xlim((50., tstop))

    # # empty list for the aggregate dipole data
    # dpl_exp = []

    # # go through each expmt
    # # calculation is extremely redundant
    # for expmt_group in ddata.expmt_groups:
    #     # a little sloppy, just find the param file
    #     # this param file was for the baseline renormalization and
    #     # assumes it's the same in all for this expmt_group
    #     # also for getting the gid_dict, also assumed to be the same
    #     fparam = ddata.file_match(expmt_group, 'param')[0]

    #     # general check to see if the aggregate dipole data exists
    #     if 'mu_low' in expmt_group or 'mu_high' in expmt_group:
    #         # check to see if these files exist
    #         flist = ddata.find_aggregate_file(expmt_group, 'dpl')

    #         # if no file exists, then find one
    #         if not len(flist):
    #             calc_aggregate_dipole(ddata)
    #             flist = ddata.find_aggregate_file(expmt_group, 'dpl')

    #         # testing the first file
    #         list_spk = ddata.file_match(expmt_group, 'rawspk')
    #         list_s_dict = [spikefn.spikes_from_file(fparam, fspk) for fspk in list_spk]
    #         list_evoked = [s_dict['evprox0'].spike_list[0][0] for s_dict in list_s_dict]
    #         lines_spk = [f_exp.ax[2].axvline(x=x_val, linewidth=0.5, color='r') for x_val in list_evoked]
    #         lines_spk = [f_exp.ax[3].axvline(x=x_val, linewidth=0.5, color='r') for x_val in list_evoked]

    #     # handle mu_low and mu_high separately
    #     if 'mu_low' in expmt_group:
    #         dpl_mu_low_ev = Dipole(flist[0])
    #         dpl_mu_low_ev.baseline_renormalize(fparam)
    #         f_exp.ax[2].plot(dpl_mu_low_ev.t, dpl_mu_low_ev.dpl)

    #     elif 'mu_high' in expmt_group:
    #         dpl_mu_high_ev = Dipole(flist[0])
    #         dpl_mu_high_ev.baseline_renormalize(fparam)
    #         f_exp.ax[3].plot(dpl_mu_high_ev.t, dpl_mu_high_ev.dpl)

    # f_exp.ax[2].set_xlim(50., tstop)
    # f_exp.ax[3].set_xlim(50., tstop)

    # f_exp.savepng(fname_exp_fig)
    # f_exp.close()
