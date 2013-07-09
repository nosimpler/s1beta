# pmanu_gamma.py - plot functions for gamma manuscript
#
# v 1.8.14
# rev 2013-07-09 (SL: updated)
# last major: (SL: updated)

import itertools as it
import numpy as np
import os
import fileio as fio
import currentfn
import dipolefn
import specfn
import spikefn
import paramrw
import ac_manu_gamma as acg

# all the data comes from one sim
def high_f():
    dproj = '/repo/data/s1'

    # data directories (made up for now)
    # the resultant figure is saved in d0
    d = os.path.join(dproj, 'pub', '2013-06-28_gamma_weak_L5-000')

    # for now grab the first experiment
    expmt = ddata.expmt_groups[0]
    ddata = fio.SimulationPaths()
    ddata.read_sim(dproj, d)

    runtype = 'debug'
    # runtype = 'pub'

    # for now hard code the simulation run
    n_run = 0

    # prints the fig in ddata0
    f = acg.FigHF(runtype)

    # grab the relevant files
    f_spec = ddata.file_match(expmt, 'rawspec')[n_run]
    f_dpl = ddata.file_match(expmt, 'rawdpl')[n_run]
    f_spk = ddata.file_match(expmt, 'rawspk')[n_run]
    f_param = ddata.file_match(expmt, 'param')[n_run]
    f_current = ddata.file_match(expmt, 'rawcurrent')[n_run]

    # figure out the tstop and xlim
    tstop = paramrw.find_param(f_param, 'tstop')
    dt = paramrw.find_param(f_param, 'dt')
    xlim = (50., tstop)

    # grab the dipole data
    dpl = dipolefn.Dipole(f_dpl)
    dpl.baseline_renormalize(f_param)
    dpl.convert_fAm_to_nAm()

    # calculate the Welch periodogram
    pgram = {
        'agg': specfn.Welch(dpl.t, dpl.dpl['agg'], dt),
        'L2': specfn.Welch(dpl.t, dpl.dpl['L2'], dt),
        'L5': specfn.Welch(dpl.t, dpl.dpl['L5'], dt),
    }

    # plot periodograms
    pgram['agg'].plot_to_ax(f.ax['pgram_L'])
    pgram['L2'].plot_to_ax(f.ax['pgram_M'])
    pgram['L5'].plot_to_ax(f.ax['pgram_R'])

    # plot currents
    I_soma = currentfn.SynapticCurrent(f_current)
    I_soma.plot_to_axis(f.ax['current_M'], 'L2')
    I_soma.plot_to_axis(f.ax['current_R'], 'L5')
    f.set_axes_pingping()

    # cols have same suffix
    list_cols = ['L', 'M', 'R']

    # create handles list
    list_h_pgram = ['pgram_'+col for col in list_cols]
    list_h_dpl = ['dpl_'+col for col in list_cols]

    # spec
    pc = {
        'L': specfn.pspec_ax(f.ax['spec_L'], f_spec, xlim, layer='agg'),
        'M': specfn.pspec_ax(f.ax['spec_M'], f_spec, xlim, layer='L2'),
        'R': specfn.pspec_ax(f.ax['spec_R'], f_spec, xlim, layer='L5'),
    }

    # create a list of spec color handles
    # list_h_spec_cb = ['pc_'+col for col in list_cols]

    # get the vmin, vmax and add them to the master list
    # f.equalize_speclim(pc)
    # list_lim_spec = []

    # no need for outputs
    if runtype == 'debug':
        f.f.colorbar(pc['L'], ax=f.ax['spec_L'], format='%.3e')
        f.f.colorbar(pc['M'], ax=f.ax['spec_M'], format='%.3e')
        f.f.colorbar(pc['R'], ax=f.ax['spec_R'], format='%.3e')
        # list_spec_handles = [ax for ax in f.ax.keys() if ax.startswith('spec')]
        list_spec_handles = ['spec_M', 'spec_R']
        f.remove_tick_labels(list_spec_handles, ax_xy='y')

    elif runtype == 'pub':
        f.f.colorbar(pc['R'], ax=f.ax['spec_R'], format='%.2e')

    # grab the spike data
    s = spikefn.spikes_from_file(f_param, f_spk)

    # dipoles
    dpl.plot(f.ax['dpl_L'], xlim, layer='agg')
    dpl.plot(f.ax['dpl_M'], xlim, layer='L2')
    dpl.plot(f.ax['dpl_R'], xlim, layer='L5')

    # equalize the ylim
    # f.equalize_ylim(list_h_pgram)
    # f.equalize_ylim(list_h_dpl)

    # spikes
    spikes = {
        'L2': spikefn.filter_spike_dict(s, 'L2_'),
        'L5': spikefn.filter_spike_dict(s, 'L5_'),
    }

    # plot the data
    spikefn.spike_png(f.ax['spk_M'], spikes['L2'])
    spikefn.spike_png(f.ax['spk_R'], spikes['L5'])
    f.ax['spk_M'].set_xlim(xlim)
    f.ax['spk_R'].set_xlim(xlim)

    # # save the fig in ddata0 (arbitrary)
    f_prefix = '%s_laminar' % ddata.sim_prefix
    dfig = os.path.join(ddata.dsim, expmt)

    f.savepng_new(dfig, f_prefix)
    f.saveeps(dfig, f_prefix)
    f.close()

def laminar(ddata):
    # for now grab the first experiment
    expmt = ddata.expmt_groups[0]

    runtype = 'debug'
    # runtype = 'pub'

    # for now hard code the simulation run
    n_run = 0

    # prints the fig in ddata0
    f = acg.FigLaminarComparison(runtype)

    # grab the relevant files
    f_spec = ddata.file_match(expmt, 'rawspec')[n_run]
    f_dpl = ddata.file_match(expmt, 'rawdpl')[n_run]
    f_spk = ddata.file_match(expmt, 'rawspk')[n_run]
    f_param = ddata.file_match(expmt, 'param')[n_run]
    f_current = ddata.file_match(expmt, 'rawcurrent')[n_run]

    # figure out the tstop and xlim
    tstop = paramrw.find_param(f_param, 'tstop')
    dt = paramrw.find_param(f_param, 'dt')
    xlim = (50., tstop)

    # grab the dipole data
    dpl = dipolefn.Dipole(f_dpl)
    dpl.baseline_renormalize(f_param)
    dpl.convert_fAm_to_nAm()

    # calculate the Welch periodogram
    pgram = {
        'agg': specfn.Welch(dpl.t, dpl.dpl['agg'], dt),
        'L2': specfn.Welch(dpl.t, dpl.dpl['L2'], dt),
        'L5': specfn.Welch(dpl.t, dpl.dpl['L5'], dt),
    }

    # plot periodograms
    pgram['agg'].plot_to_ax(f.ax['pgram_L'])
    pgram['L2'].plot_to_ax(f.ax['pgram_M'])
    pgram['L5'].plot_to_ax(f.ax['pgram_R'])

    # plot currents
    I_soma = currentfn.SynapticCurrent(f_current)
    I_soma.plot_to_axis(f.ax['current_M'], 'L2')
    I_soma.plot_to_axis(f.ax['current_R'], 'L5')
    f.set_axes_pingping()

    # cols have same suffix
    list_cols = ['L', 'M', 'R']

    # create handles list
    list_h_pgram = ['pgram_'+col for col in list_cols]
    list_h_dpl = ['dpl_'+col for col in list_cols]

    # spec
    pc = {
        'L': specfn.pspec_ax(f.ax['spec_L'], f_spec, xlim, layer='agg'),
        'M': specfn.pspec_ax(f.ax['spec_M'], f_spec, xlim, layer='L2'),
        'R': specfn.pspec_ax(f.ax['spec_R'], f_spec, xlim, layer='L5'),
    }

    # create a list of spec color handles
    # list_h_spec_cb = ['pc_'+col for col in list_cols]

    # get the vmin, vmax and add them to the master list
    # f.equalize_speclim(pc)
    # list_lim_spec = []

    # no need for outputs
    if runtype == 'debug':
        f.f.colorbar(pc['L'], ax=f.ax['spec_L'], format='%.3e')
        f.f.colorbar(pc['M'], ax=f.ax['spec_M'], format='%.3e')
        f.f.colorbar(pc['R'], ax=f.ax['spec_R'], format='%.3e')
        # list_spec_handles = [ax for ax in f.ax.keys() if ax.startswith('spec')]
        list_spec_handles = ['spec_M', 'spec_R']
        f.remove_tick_labels(list_spec_handles, ax_xy='y')

    elif runtype == 'pub':
        f.f.colorbar(pc['R'], ax=f.ax['spec_R'], format='%.2e')

    # grab the spike data
    s = spikefn.spikes_from_file(f_param, f_spk)

    # dipoles
    dpl.plot(f.ax['dpl_L'], xlim, layer='agg')
    dpl.plot(f.ax['dpl_M'], xlim, layer='L2')
    dpl.plot(f.ax['dpl_R'], xlim, layer='L5')

    # equalize the ylim
    # f.equalize_ylim(list_h_pgram)
    # f.equalize_ylim(list_h_dpl)

    # spikes
    spikes = {
        'L2': spikefn.filter_spike_dict(s, 'L2_'),
        'L5': spikefn.filter_spike_dict(s, 'L5_'),
    }

    # plot the data
    spikefn.spike_png(f.ax['spk_M'], spikes['L2'])
    spikefn.spike_png(f.ax['spk_R'], spikes['L5'])
    f.ax['spk_M'].set_xlim(xlim)
    f.ax['spk_R'].set_xlim(xlim)

    # # save the fig in ddata0 (arbitrary)
    f_prefix = '%s_laminar' % ddata.sim_prefix
    dfig = os.path.join(ddata.dsim, expmt)

    f.savepng_new(dfig, f_prefix)
    f.saveeps(dfig, f_prefix)
    f.close()

# compares PING regimes for two different trial runs
# def compare_ping(ddata0, ddata1):
def compare_ping():
    dproj = '/repo/data/s1'
    # runtype = 'pub2'
    runtype = 'debug'

    # data directories (made up for now)
    # the resultant figure is saved in d0
    d0 = os.path.join(dproj, 'pub', '2013-06-28_gamma_ping_L5-000')
    d1 = os.path.join(dproj, 'pub', '2013-06-28_gamma_weak_L5-000')

    # hard code the data for now
    ddata0 = fio.SimulationPaths()
    ddata1 = fio.SimulationPaths()

    # use read_sim() to read the simulations
    ddata0.read_sim(dproj, d0)
    ddata1.read_sim(dproj, d1)

    # for now grab the first experiment in each
    expmt0 = ddata0.expmt_groups[0]
    expmt1 = ddata1.expmt_groups[0]

    # for now hard code the simulation run
    run0 = 0
    run1 = 0

    # prints the fig in ddata0
    f = acg.FigL5PingExample(runtype)

    # first panel data
    f_spec0 = ddata0.file_match(expmt0, 'rawspec')[run0]
    f_dpl0 = ddata0.file_match(expmt0, 'rawdpl')[run0]
    f_spk0 = ddata0.file_match(expmt0, 'rawspk')[run0]
    f_param0 = ddata0.file_match(expmt0, 'param')[run0]
    f_current0 = ddata0.file_match(expmt0, 'rawcurrent')[run0]

    # figure out the tstop and xlim
    tstop0 = paramrw.find_param(f_param0, 'tstop')
    dt = paramrw.find_param(f_param0, 'dt')
    xlim0 = (50., tstop0)

    # grab the dipole data
    dpl0 = dipolefn.Dipole(f_dpl0)
    dpl0.baseline_renormalize(f_param0)
    dpl0.convert_fAm_to_nAm()

    # calculate the Welch periodogram
    f_max = 150.
    pgram0 = specfn.Welch(dpl0.t, dpl0.dpl['L5'], dt)
    pgram0.plot_to_ax(f.ax['pgram_L'], f_max)

    # grab the spike data
    s0 = spikefn.spikes_from_file(f_param0, f_spk0)
    s0_L5 = spikefn.filter_spike_dict(s0, 'L5_')

    # grab the current data
    I_soma0 = currentfn.SynapticCurrent(f_current0)

    # plot the data
    dpl0.plot(f.ax['dpl_L'], xlim0, layer='L5')
    spikefn.spike_png(f.ax['raster_L'], s0_L5)
    f.ax['raster_L'].set_xlim(xlim0)

    # second panel data
    f_spec1 = ddata1.file_match(expmt1, 'rawspec')[run1]
    f_dpl1 = ddata1.file_match(expmt1, 'rawdpl')[run1]
    f_spk1 = ddata1.file_match(expmt1, 'rawspk')[run1]
    f_param1 = ddata1.file_match(expmt1, 'param')[run1]
    f_current1 = ddata1.file_match(expmt1, 'rawcurrent')[run1]

    # figure out the tstop and xlim
    tstop1 = paramrw.find_param(f_param1, 'tstop')
    xlim1 = (50., tstop1)

    # grab the dipole data
    dpl1 = dipolefn.Dipole(f_dpl1)
    dpl1.baseline_renormalize(f_param1)
    dpl1.convert_fAm_to_nAm()

    # calculate the Welch periodogram
    pgram1 = specfn.Welch(dpl1.t, dpl1.dpl['L5'], dt)
    pgram1.plot_to_ax(f.ax['pgram_R'], f_max)

    # grab the spike data
    s1 = spikefn.spikes_from_file(f_param1, f_spk1)
    s1_L5 = spikefn.filter_spike_dict(s1, 'L5_')
    s1_L2 = spikefn.filter_spike_dict(s1, 'L2_')

    # grab the current data
    I_soma1 = currentfn.SynapticCurrent(f_current1)

    # plot the data
    dpl1.plot(f.ax['dpl_R'], xlim1, layer='L5')
    spikefn.spike_png(f.ax['raster_R'], s1_L5)
    f.ax['raster_R'].set_xlim(xlim1)

    # plot the spec data
    pc = {
        'L': specfn.pspec_ax(f.ax['spec_L'], f_spec0, xlim0, layer='L5'),
        'R': specfn.pspec_ax(f.ax['spec_R'], f_spec1, xlim1, layer='L5'),
    }

    # f.equalize_speclim(pc)

    # grab the dipole figure handles
    # list_h_dpl = [h for h in f.ax.keys() if h.startswith('dpl')]
    # f.equalize_ylim(list_h_dpl)

    # and the pgrams
    # list_h_pgram = [h for h in f.ax.keys() if h.startswith('pgram')]
    # test = f.equalize_ylim(list_h_pgram)

    # plot current and do lims
    I_soma0.plot_to_axis(f.ax['current_L'], 'L5')
    I_soma1.plot_to_axis(f.ax['current_R'], 'L5')
    for ax_handle in f.ax.keys():
        if ax_handle.startswith('current_'):
            f.ax[ax_handle].set_ylim((-2000, 0.))

    # testing something
    # f.ax['pgram_L'].set_yscale('log')
    # f.ax['pgram_R'].set_yscale('log')
    # f.ax['pgram_L'].set_ylim((1e-12, 1e-3))
    # f.ax['pgram_R'].set_ylim((1e-12, 1e-3))

    # save the fig in ddata0 (arbitrary)
    f_prefix = 'gamma_L5ping_L5weak'
    dfig = os.path.join(ddata0.dsim, expmt0)

    # create the colorbars
    cb = dict.fromkeys(pc)

    if runtype == 'debug':
        for key in pc.keys():
            key_ax = 'spec_' + key
            cb[key] = f.f.colorbar(pc[key], ax=f.ax[key_ax], format=f.fmt)
    elif runtype == 'pub':
        cb['R'] = f.f.colorbar(pc['R'], ax=f.ax['spec_R'], format=f.fmt)

    f.savepng_new(dfig, f_prefix)
    f.saveeps(dfig, f_prefix)
    f.close()

# needs spec for multiple experiments, will plot 2 examples and aggregate
def pgamma_distal_phase(ddata, data_L=0, data_M=1, data_R=2):
    layer_specific = 'agg'

    for expmt in ddata.expmt_groups:
        f = acg.FigDistalPhase()

        # grab file lists
        list_spec = ddata.file_match(expmt, 'rawspec')
        list_dpl = ddata.file_match(expmt, 'rawdpl')
        list_spk = ddata.file_match(expmt, 'rawspk')
        list_param = ddata.file_match(expmt, 'param')

        # grab the tstop and make an xlim
        T = paramrw.find_param(list_param[0], 'tstop')
        xlim = (50., T)

        # grab the input frequency, try prox before dist
        f_max = paramrw.find_param(list_param[0], 'f_input_prox')

        # only try dist if prox is 0, otherwise, use prox
        if not f_max:
            f_max = paramrw.find_param(list_param[0], 'f_input_dist')

        # dealing with the left panel
        dpl_L = dipolefn.Dipole(list_dpl[data_L])
        dpl_L.baseline_renormalize(list_param[data_L])
        dpl_L.convert_fAm_to_nAm()
        dpl_L.plot(f.ax['dpl_L'], xlim, layer='agg')

        # middle data panel
        dpl_M = dipolefn.Dipole(list_dpl[data_M])
        dpl_M.baseline_renormalize(list_param[data_M])
        dpl_M.convert_fAm_to_nAm()
        dpl_M.plot(f.ax['dpl_M'], xlim, layer='agg')

        # dealing with right panel
        dpl_R = dipolefn.Dipole(list_dpl[data_R])
        dpl_R.baseline_renormalize(list_param[data_R])
        dpl_R.convert_fAm_to_nAm()
        dpl_R.plot(f.ax['dpl_R'], xlim, layer='agg')

        # get the vmin, vmax and add them to the master list
        pc = {
            'L': specfn.pspec_ax(f.ax['spec_L'], list_spec[data_L], xlim, layer=layer_specific),
            'M': specfn.pspec_ax(f.ax['spec_M'], list_spec[data_M], xlim, layer=layer_specific),
            'R': specfn.pspec_ax(f.ax['spec_R'], list_spec[data_R], xlim, layer=layer_specific),
        }

        # use the equalize function
        f.equalize_speclim(pc)

        # create colorbars
        f.f.colorbar(pc['L'], ax=f.ax['spec_L'])
        f.f.colorbar(pc['M'], ax=f.ax['spec_M'])
        f.f.colorbar(pc['R'], ax=f.ax['spec_R'])

        # hist data
        xlim_hist = (50., 100.)

        # get the data for the left panel
        _, p_dict = paramrw.read(list_param[data_L])
        s_L = spikefn.spikes_from_file(list_param[data_L], list_spk[data_L])
        s_L = spikefn.alpha_feed_verify(s_L, p_dict)
        # n_bins = spikefn.hist_bin_opt(s_L['alpha_feed_prox'].spike_list, 10)
        n_bins = 500

        # prox and dist spike lists
        sp_list = spike_list_truncate(s_L['alpha_feed_prox'].spike_list[0])
        sd_list = spike_list_truncate(s_L['alpha_feed_dist'].spike_list[0])
        spikefn.pinput_hist(f.ax['hist_L'], f.ax_twinx['hist_L'], sp_list, sd_list, n_bins, xlim_hist)

        # same motif as previous lines, I'm tired.
        _, p_dict = paramrw.read(list_param[data_M])
        s_M = spikefn.spikes_from_file(list_param[data_M], list_spk[data_M])
        s_M = spikefn.alpha_feed_verify(s_M, p_dict)
        sp_list = spike_list_truncate(s_M['alpha_feed_prox'].spike_list[0])
        sd_list = spike_list_truncate(s_M['alpha_feed_dist'].spike_list[0])
        spikefn.pinput_hist(f.ax['hist_M'], f.ax_twinx['hist_M'], sp_list, sd_list, n_bins, xlim_hist)

        # same motif as previous lines, I'm tired.
        _, p_dict = paramrw.read(list_param[data_R])
        s_R = spikefn.spikes_from_file(list_param[data_R], list_spk[data_R])
        s_R = spikefn.alpha_feed_verify(s_R, p_dict)
        sp_list = spike_list_truncate(s_R['alpha_feed_prox'].spike_list[0])
        sd_list = spike_list_truncate(s_R['alpha_feed_dist'].spike_list[0])
        spikefn.pinput_hist(f.ax['hist_R'], f.ax_twinx['hist_R'], sp_list, sd_list, n_bins, xlim_hist)

        # now do the aggregate data
        # theta is the normalized phase
        list_spec_max = np.zeros(len(list_spec))
        list_theta = np.zeros(len(list_spec))
        list_delay = np.zeros(len(list_spec))

        i = 0
        for fspec, fparam in it.izip(list_spec, list_param):
            # f_max comes from the input f
            # f_max = 50.
            t_pd = 1000. / f_max

            # read the data
            data_spec = specfn.read(fspec)

            # use specpwr_stationary() to get an aggregate measure of power over the entire time
            p_stat = specfn.specpwr_stationary(data_spec['time'], data_spec['freq'], data_spec['TFR'])

            # this is ONLY for aggregate and NOT for individual layers right now
            # here, f_max is the hard coded one and NOT the calculated one from specpwr_stationary()
            list_spec_max[i] = p_stat['p'][p_stat['f']==f_max]

            # get the relevant param's value
            t0_prox = paramrw.find_param(fparam, 't0_input_prox')
            t0_dist = paramrw.find_param(fparam, 't0_input_dist')

            # calculating these two together BUT don't need to. Cleanness beats efficiency here
            list_delay[i] = t0_dist - t0_prox
            list_theta[i] = list_delay[i] / t_pd

            i += 1

        f.ax['aggregate'].plot(list_delay, list_spec_max, marker='o')

        # deal with names
        f_prefix = 'gamma_%s_distal_phase' % expmt
        dfig = os.path.join(ddata.dsim, expmt)

        f.savepng_new(dfig, f_prefix)
        f.saveeps(dfig, f_prefix)
        f.close()

def spike_list_truncate(s_list):
    return s_list[(s_list > 55.) & (s_list < 100.)]

# needs spec for 3 experiments
# really a generic comparison of the top 3 sims in a given exp
# the list is naturally truncated by the length of ax_suffices
def pgamma_stdev(ddata):
    for expmt in ddata.expmt_groups:
        # runtype = 'debug'
        runtype = 'pub2'

        f = acg.FigStDev(runtype)

        # data types
        list_spec = ddata.file_match(expmt, 'rawspec')
        list_dpl = ddata.file_match(expmt, 'rawdpl')
        list_param = ddata.file_match(expmt, 'param')
        list_spk = ddata.file_match(expmt, 'rawspk')

        # time info
        T = paramrw.find_param(list_param[0], 'tstop')
        xlim = (50., T)

        # assume only the first 3 files are the ones we care about
        ax_suffices = [
            '_L',
            '_M',
            '_R',
        ]

        # dpl handles list
        list_handles_dpl = []

        # spec handles
        pc = {}

        # lists in izip are naturally truncated by the shortest list
        for ax_end, fdpl, fspec, fparam, fspk in it.izip(ax_suffices, list_dpl, list_spec, list_param, list_spk):
            # create axis handle names
            ax_dpl = 'dpl%s' % ax_end
            ax_spec = 'spec%s' % ax_end
            ax_hist = 'hist%s' % ax_end

            # add to my terrible list
            list_handles_dpl.append(ax_dpl)

            # grab the dipole and convert
            dpl = dipolefn.Dipole(fdpl)
            dpl.baseline_renormalize(fparam)
            dpl.convert_fAm_to_nAm()

            # plot relevant data
            dpl.plot(f.ax[ax_dpl], xlim, layer='L5')
            pc[ax_spec] = specfn.pspec_ax(f.ax[ax_spec], fspec, xlim, layer='L5')

            # only set the colorbar for all axes in debug mode
            # otherwise set only for the rightmost spec axis
            if runtype in ('debug', 'pub2'):
                f.f.colorbar(pc[ax_spec], ax=f.ax[ax_spec])
            elif runtype == 'pub':
                if ax_end == '_R':
                    f.f.colorbar(pc[ax_spec], ax=f.ax[ax_spec])

            # histogram stuff
            _, p_dict = paramrw.read(fparam)
            s = spikefn.spikes_from_file(fparam, fspk)
            s = spikefn.alpha_feed_verify(s, p_dict)

            # result of the optimization function, for the right 2 panels. 100
            # was the value returned for the L panel for f plot
            # result for stdev plot was 290, 80, 110
            # n_bins = spikefn.hist_bin_opt(s['alpha_feed_prox'][0].spike_list, 10)
            # print n_bins
            n_bins = 110

            # plot the hist
            spikefn.pinput_hist_onesided(f.ax[ax_hist], s['alpha_feed_prox'][0].spike_list, n_bins)
            f.ax[ax_hist].set_xlim(xlim)

        # equalize ylim on hists
        list_ax_hist = [ax for ax in f.ax.keys() if ax.startswith('hist')]
        f.equalize_ylim(list_ax_hist)

        # normalize the spec
        # f.equalize_speclim(pc)
        f.remove_twinx_labels()

        # normalize the dpl with that hack
        # centers c and lim l
        # c = [1e-3, 1.2e-3, 1.8e-3]
        # l = 2e-3
        # ylim_hack(f, list_handles_dpl, c, l)
        for h in list_handles_dpl:
             f.ax[h].set_ylim((-1e-3, 3e-3))

        # some fig naming stuff
        fprefix_short = 'gamma_%s_compare3' % expmt
        dfig = os.path.join(ddata.dsim, expmt)

        # use methods to save figs
        f.savepng_new(dfig, fprefix_short)
        f.saveeps(dfig, fprefix_short)
        f.close()

# manual setting of ylims
def ylim_hack(f, list_handles, ylim_centers, ylim_limit):
    # ylim_centers = [1.5e-5, 2e-5, 2.5e-5]
    # ylim_limit = 1.5e-5

    # gross
    for h, c in it.izip(list_handles, ylim_centers):
        f.ax[h].grid(True, which='minor')
        ylim = (c - ylim_limit, c + ylim_limit)
        f.ax[h].set_ylim(ylim)
        f.f.canvas.draw()
        # labels = [tick.get_text() for tick in f.ax[list_handles[1]].get_yticklabels()]
        labels = f.ax[h].yaxis.get_ticklocs()
        labels_text = [str(label) for label in labels[:-1]]
        labels_text[0] = ''
        f.ax[h].set_yticklabels(labels_text)
        # print labels_text
