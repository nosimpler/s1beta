# pmanu_gamma.py - plot functions for gamma manuscript
#
# v 1.8.12
# rev 2013-06-22 (SL: updated)
# last major: (SL: created)

import itertools as it
import numpy as np
import os
import fileio as fio
import dipolefn
import specfn
import spikefn
import paramrw
import ac_manu_gamma as acg

# all the data comes from one sim
def laminar(ddata):
    # for now grab the first experiment
    expmt = ddata.expmt_groups[0]

    # for now hard code the simulation run
    n_run = 0

    # prints the fig in ddata0
    f = acg.FigLaminarComparison()

    # grab the relevant files
    f_spec = ddata.file_match(expmt, 'rawspec')[n_run]
    f_dpl = ddata.file_match(expmt, 'rawdpl')[n_run]
    f_spk = ddata.file_match(expmt, 'rawspk')[n_run]
    f_param = ddata.file_match(expmt, 'param')[n_run]

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
    f.equalize_speclim(pc)
    list_lim_spec = []
    # for h_pc in list_cols:
    #     vmin, vmax = pc[h_pc].get_clim()
    #     list_lim_spec.extend([vmin, vmax])

    # ylim_spec = (np.min(list_lim_spec), np.max(list_lim_spec))

    # pc['L'].set_clim(ylim_spec[0], ylim_spec[1])
    # pc['M'].set_clim(ylim_spec[0], ylim_spec[1])
    # pc['R'].set_clim(ylim_spec[0], ylim_spec[1])

    # no need for outputs
    f.f.colorbar(pc['L'], ax=f.ax['spec_L'])
    f.f.colorbar(pc['M'], ax=f.ax['spec_M'])
    f.f.colorbar(pc['R'], ax=f.ax['spec_R'])

    # grab the spike data
    s = spikefn.spikes_from_file(f_param, f_spk)

    # dipoles
    dpl.plot(f.ax['dpl_L'], xlim, layer='agg')
    dpl.plot(f.ax['dpl_M'], xlim, layer='L2')
    dpl.plot(f.ax['dpl_R'], xlim, layer='L5')

    # equalize the ylim
    f.equalize_ylim(list_h_pgram)
    f.equalize_ylim(list_h_dpl)

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
    name_short = '%s_laminar.png' % ddata.sim_prefix
    f_name = os.path.join(ddata.dsim, expmt, name_short)

    # # create the colorbars
    # f.f.colorbar(pc_L, ax=f.ax['spec_L'])
    # f.f.colorbar(pc_R, ax=f.ax['spec_R'])

    f.savepng(f_name)
    f.close()

# compares PING regimes for two different trial runs
# def compare_ping(ddata0, ddata1):
def compare_ping():
    dproj = '/repo/data/s1'

    # data directories (made up for now)
    # the resultant figure is saved in d0
    d0 = os.path.join(dproj, 'pub', '2013-06-18_gamma_weak_L5-000')
    d1 = os.path.join(dproj, 'pub', '2013-06-18_gamma_ping_L5-004')

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
    f = acg.FigL5PingExample()

    # first panel data
    f_spec0 = ddata0.file_match(expmt0, 'rawspec')[run0]
    f_dpl0 = ddata0.file_match(expmt0, 'rawdpl')[run0]
    f_spk0 = ddata0.file_match(expmt0, 'rawspk')[run0]
    f_param0 = ddata0.file_match(expmt0, 'param')[run0]

    # figure out the tstop and xlim
    tstop0 = paramrw.find_param(f_param0, 'tstop')
    dt = paramrw.find_param(f_param0, 'dt')
    xlim0 = (50., tstop0)

    # grab the dipole data
    dpl0 = dipolefn.Dipole(f_dpl0)
    dpl0.baseline_renormalize(f_param0)
    dpl0.convert_fAm_to_nAm()

    # calculate the Welch periodogram
    pgram0 = specfn.Welch(dpl0.t, dpl0.dpl['agg'], dt)
    pgram0.plot_to_ax(f.ax['pgram_L'])

    # grab the spike data
    s0 = spikefn.spikes_from_file(f_param0, f_spk0)
    s0_L5 = spikefn.filter_spike_dict(s0, 'L5_')

    # plot the data
    dpl0.plot(f.ax['dpl_L'], xlim0, layer='agg')
    spikefn.spike_png(f.ax['raster_L'], s0_L5)
    f.ax['raster_L'].set_xlim(xlim0)

    # second panel data
    f_spec1 = ddata1.file_match(expmt1, 'rawspec')[run1]
    f_dpl1 = ddata1.file_match(expmt1, 'rawdpl')[run1]
    f_spk1 = ddata1.file_match(expmt1, 'rawspk')[run1]
    f_param1 = ddata1.file_match(expmt1, 'param')[run1]

    # figure out the tstop and xlim
    tstop1 = paramrw.find_param(f_param1, 'tstop')
    xlim1 = (50., tstop1)

    # grab the dipole data
    dpl1 = dipolefn.Dipole(f_dpl1)
    dpl1.baseline_renormalize(f_param1)
    dpl1.convert_fAm_to_nAm()

    # calculate the Welch periodogram
    pgram1 = specfn.Welch(dpl1.t, dpl1.dpl['agg'], dt)
    pgram1.plot_to_ax(f.ax['pgram_R'])

    # grab the spike data
    s1 = spikefn.spikes_from_file(f_param1, f_spk1)
    s1_L5 = spikefn.filter_spike_dict(s1, 'L5_')
    s1_L2 = spikefn.filter_spike_dict(s1, 'L2_')

    # plot the data
    dpl1.plot(f.ax['dpl_R'], xlim1, layer='agg')
    spikefn.spike_png(f.ax['raster_R'], s1_L5)
    f.ax['raster_R'].set_xlim(xlim1)

    # plot the spec data
    pc = {
        'L': specfn.pspec_ax(f.ax['spec_L'], f_spec0, xlim0, layer='agg'),
        'R': specfn.pspec_ax(f.ax['spec_R'], f_spec1, xlim1, layer='agg'),
    }

    f.equalize_speclim(pc)

    # grab the dipole figure handles
    list_h_dpl = [h for h in f.ax.keys() if h.startswith('dpl')]
    # f.ax['dpl_R'].set_ylim((-0.1, 0.3))
    f.equalize_ylim(list_h_dpl)

    # and the pgrams
    list_h_pgram = [h for h in f.ax.keys() if h.startswith('pgram')]
    test = f.equalize_ylim(list_h_pgram)
    print f.ax['pgram_L'].get_ylim()

    # testing something
    # f.ax['pgram_L'].set_yscale('log')
    # f.ax['pgram_R'].set_yscale('log')
    # f.ax['pgram_L'].set_ylim((1e-12, 1e-3))
    # f.ax['pgram_R'].set_ylim((1e-12, 1e-3))

    # save the fig in ddata0 (arbitrary)
    name_short = 'gamma_compare_ping.png'
    f_name = os.path.join(ddata0.dsim, expmt0, name_short)

    # create the colorbars
    cb = dict.fromkeys(pc)
    for key in pc.keys():
        key_ax = 'spec_' + key
        cb[key] = f.f.colorbar(pc[key], ax=f.ax[key_ax], format=f.fmt)
    # f.f.colorbar(pc['L'], ax=f.ax['spec_L'])
    # f.f.colorbar(pc['R'], ax=f.ax['spec_R'])

    f.savepng(f_name)
    f.close()

# needs spec for multiple experiments, will plot 2 examples and aggregate
def pgamma_distal_phase(ddata, data_L=0, data_M=1, data_R=2):
    layer_specific = 'agg'

    for expmt in ddata.expmt_groups:
        f = acg.FigDistalPhase()

        # deal with names
        name_short = 'gamma_%s_distal_phase.png' % expmt
        f_name = os.path.join(ddata.dsim, expmt, name_short)

        # grab file lists
        list_spec = ddata.file_match(expmt, 'rawspec')
        list_dpl = ddata.file_match(expmt, 'rawdpl')
        list_param = ddata.file_match(expmt, 'param')

        # grab the tstop and make an xlim
        T = paramrw.find_param(list_param[0], 'tstop')
        xlim = (50., T)

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

        f.equalize_speclim(pc)

        # pc_L.set_clim(ylim_spec[0], ylim_spec[1])
        # pc_M.set_clim(ylim_spec[0], ylim_spec[1])
        # pc_R.set_clim(ylim_spec[0], ylim_spec[1])

        # create colorbars
        f.f.colorbar(pc['L'], ax=f.ax['spec_L'])
        f.f.colorbar(pc['M'], ax=f.ax['spec_M'])
        f.f.colorbar(pc['R'], ax=f.ax['spec_R'])

        # now do the aggregate data
        list_spec_max = np.zeros(len(list_spec))
        list_theta = np.zeros(len(list_spec))
        list_delay = np.zeros(len(list_spec))

        i = 0
        for fspec, fparam in it.izip(list_spec, list_param):
            # f is 40 Hz, calculate the associated period
            f_max = 40.
            t_pd = 1000. / f_max

            # read the data
            data_spec = specfn.read(fspec)

            # use specpwr_stationary() to get an aggregate measure of power over the entire time
            p_stat = specfn.specpwr_stationary(data_spec['time'], data_spec['freq'], data_spec['TFR'])

            # this is ONLY for aggregate and NOT for individual layers right now
            # here, f_max is the hard coded one and NOT the calculated one from specpwr_stationary()
            list_spec_max[i] = p_stat['p'][p_stat['f']==f_max]
            # list_spec_max[i] = np.max(data_spec['TFR'])

            # get the relevant param's value
            t0_prox = paramrw.find_param(fparam, 't0_input_prox')
            t0_dist = paramrw.find_param(fparam, 't0_input_dist')

            # calculating these two together BUT don't need to. Cleanness beats efficiency here
            list_delay[i] = t0_dist - t0_prox
            list_theta[i] = list_delay[i] / t_pd

            i += 1

        f.ax['aggregate'].plot(list_delay, list_spec_max, marker='o')

        f.savepng(f_name)
        f.close()

# needs spec for 3 experiments
# really a generic comparison of the top 3 sims in a given exp
# the list is naturally truncated by the length of ax_suffices
def pgamma_stdev(ddata):
    for expmt in ddata.expmt_groups:
        f = acg.FigStDev()

        list_spec = ddata.file_match(expmt, 'rawspec')
        list_dpl = ddata.file_match(expmt, 'rawdpl')
        list_param = ddata.file_match(expmt, 'param')
        T = paramrw.find_param(list_param[0], 'tstop')
        xlim = (50., T)

        # assume only the first 3 files are the ones we care about
        ax_suffices = [
            '_L',
            '_M',
            '_R',
        ]

        # list_lim_spec = []
        # list_handles_spec = []
        list_handles_dpl = []

        # spec handles
        pc = {}

        # specfn.pspec_ax(f.ax['spec_L'], list_spec[0], layer='L2')
        # lists in izip are naturally truncated by the shortest list
        for ax_end, fdpl, fspec, fparam in it.izip(ax_suffices, list_dpl, list_spec, list_param):
            # create axis handle names
            ax_dpl = 'dpl%s' % ax_end
            ax_spec = 'spec%s' % ax_end

            # add to my terrible list
            list_handles_dpl.append(ax_dpl)

            # grab the dipole and convert
            dpl = dipolefn.Dipole(fdpl)
            dpl.baseline_renormalize(fparam)
            dpl.convert_fAm_to_nAm()

            # plot relevant data
            dpl.plot(f.ax[ax_dpl], xlim, layer='agg')
            pc[ax_spec] = specfn.pspec_ax(f.ax[ax_spec], fspec, xlim, layer='L2')
            f.f.colorbar(pc[ax_spec], ax=f.ax[ax_spec])

        # normalize the spec
        f.equalize_speclim(pc)

        # normalize the dpl with that hack
        ylim_hack(f, list_handles_dpl)
        # for h in list_handles_dpl:
        #     f.ax[h].set_ylim((0., 4e-5))

        # some fig naming stuff
        fprefix_short = 'gamma_%s_compare3' % expmt
        dfig = os.path.join(ddata.dsim, expmt)

        # use methods to save figs
        f.savepng_new(dfig, fprefix_short)
        f.saveeps(dfig, fprefix_short)
        f.close()

# manual setting of ylims
def ylim_hack(f, list_handles):
    ylim_centers = [1.5e-5, 2e-5, 2.5e-5]
    ylim_limit = 1.5e-5

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
