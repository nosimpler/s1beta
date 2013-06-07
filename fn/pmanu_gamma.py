# pmanu_gamma.py - plot functions for gamma manuscript
#
# v 1.7.59b
# rev 2013-05-31 (SL: created)
# last major:

import itertools as it
import numpy as np
import os
import fileio as fio
import dipolefn
import specfn
import spikefn
import paramrw
import ac_manu_gamma as acg

# compares PING regimes for two different trial runs
def compare_ping():
# def compare_ping(ddata0, ddata1):
    dproj = '/repo/data/s1'

    # data directories (made up for now)
    d0 = os.path.join(dproj, '2013-05-22', 'gamma_weak_L5-003')
    d1 = os.path.join(dproj, '2013-05-22', 'gamma_ping_L2-000')

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
    xlim0 = (50., tstop0)

    # grab the dipole data
    dpl0 = dipolefn.Dipole(f_dpl0)
    dpl0.convert_fAm_to_nAm()

    # grab the spike data
    s0 = spikefn.spikes_from_file(f_param0, f_spk0)
    s0_L5 = spikefn.filter_spike_dict(s0, 'L5_')

    # plot the data
    pc_L = specfn.pspec_ax(f.ax['spec_L'], f_spec0, xlim0, layer='agg')
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
    dpl1.convert_fAm_to_nAm()

    # grab the spike data
    s1 = spikefn.spikes_from_file(f_param1, f_spk1)
    s1_L5 = spikefn.filter_spike_dict(s1, 'L5_')
    s1_L2 = spikefn.filter_spike_dict(s1, 'L2_')

    # plot the data
    pc_R = specfn.pspec_ax(f.ax['spec_R'], f_spec1, xlim1, layer='agg')
    dpl1.plot(f.ax['dpl_R'], xlim1, layer='agg')
    spikefn.spike_png(f.ax['raster_R'], s1_L2)
    f.ax['raster_R'].set_xlim(xlim1)

    # save the fig in ddata0 (arbitrary)
    name_short = 'gamma_compare_ping.png'
    f_name = os.path.join(ddata0.dsim, expmt0, name_short)

    # create the colorbars
    f.f.colorbar(pc_L, ax=f.ax['spec_L'])
    f.f.colorbar(pc_R, ax=f.ax['spec_R'])

    f.savepng(f_name)
    f.close()

# needs spec for multiple experiments, will plot 2 examples and aggregate
def pgamma_distal_phase(ddata, data_L=0, data_R=1):
    layer_specific = 'agg'
    for expmt in ddata.expmt_groups:
        f = acg.FigDistalPhase()

        # deal with names
        name_short = 'gamma_distal_phase_%s.png' % expmt
        f_name = os.path.join(ddata.dsim, expmt, name_short)

        # grab file lists
        list_spec = ddata.file_match(expmt, 'rawspec')
        list_dpl = ddata.file_match(expmt, 'rawdpl')
        list_param = ddata.file_match(expmt, 'param')

        # grab the tstop and make an xlim
        T = paramrw.find_param(list_param[0], 'tstop')
        xlim = (50., T)

        print data_L, data_R

        # data_L = 0
        # data_R = 20

        # dealing with the left panel
        dpl_L = dipolefn.Dipole(list_dpl[data_L])
        dpl_L.convert_fAm_to_nAm()
        dpl_L.plot(f.ax['dpl_L'], xlim, layer='agg')

        pc_L = specfn.pspec_ax(f.ax['spec_L'], list_spec[data_L], xlim, layer=layer_specific)

        # dealing with right panel
        dpl_R = dipolefn.Dipole(list_dpl[data_R])
        dpl_R.convert_fAm_to_nAm()
        dpl_R.plot(f.ax['dpl_R'], xlim, layer='agg')

        pc_R = specfn.pspec_ax(f.ax['spec_R'], list_spec[data_R], xlim, layer=layer_specific)

        # get the vmin, vmax and add them to the master list
        list_lim_spec = []
        [vmin, vmax] = pc_L.get_clim()
        list_lim_spec.extend([vmin, vmax])

        [vmin, vmax] = pc_R.get_clim()
        list_lim_spec.extend([vmin, vmax])

        print list_lim_spec
        ylim_spec = (np.min(list_lim_spec), np.max(list_lim_spec))
        print ylim_spec

        pc_L.set_clim(ylim_spec[0], ylim_spec[1])
        pc_R.set_clim(ylim_spec[0], ylim_spec[1])

        cb = f.f.colorbar(pc_L, ax=f.ax['spec_L'])
        cb = f.f.colorbar(pc_R, ax=f.ax['spec_R'])

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
def pgamma_stdev(ddata):
    for expmt in ddata.expmt_groups:
        f = acg.FigStDev()

        name_short = 'gamma_stdev_%s.png' % expmt
        f_name = os.path.join(ddata.dsim, expmt, name_short)

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

        list_lim_spec = []
        list_handles_spec = []

        # specfn.pspec_ax(f.ax['spec_L'], list_spec[0], layer='L2')
        # for i in range(N):
        for ax_end, fdpl, fspec in it.izip(ax_suffices, list_dpl, list_spec):
            # create axis handle names
            ax_dpl = 'dpl%s' % ax_end
            ax_spec = 'spec%s' % ax_end

            # grab the dipole and convert
            dpl = dipolefn.Dipole(fdpl)
            dpl.convert_fAm_to_nAm()

            # plot relevant data
            dpl.plot(f.ax[ax_dpl], xlim, layer='agg')
            list_handles_spec.append(specfn.pspec_ax(f.ax[ax_spec], fspec, xlim, layer='L2'))

            # get the vmin, vmax and add them to the master list
            [vmin, vmax] = list_handles_spec[-1].get_clim()
            list_lim_spec.extend([vmin, vmax])

        print list_lim_spec
        ylim_spec = (np.min(list_lim_spec), np.max(list_lim_spec))
        print ylim_spec

        for pc in list_handles_spec:
            pc.set_clim(ylim_spec[0], ylim_spec[1])
        
        cb = f.f.colorbar(list_handles_spec[-1], ax=f.ax['spec_R'])

        f.savepng(f_name)
        f.close()
