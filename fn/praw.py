# praw.py - all of the raw data types on one fig
#
# v 1.7.53
# rev 2013-05-08 (SL: fixed the error I had accidentally introduced ... without checking ... )
# last major: (SL: added spec_current)

import fileio as fio
import numpy as np
import itertools as it
import ast
import os
import paramrw
import dipolefn
import spikefn 
import specfn
import currentfn
import matplotlib.pyplot as plt
from neuron import h as nrn
import axes_create as ac

# For a given ddata (SimulationPaths object), find the mean dipole
# over ALL trials in ALL conditions in EACH experiment
def praw(ddata):
    # grab the original dipole from a specific dir
    dproj = '/repo/data/s1'

    # check on spec data
    # generates both spec because both are needed here
    specfn.generate_missing_spec(ddata)

    # test experiment
    expmt_group = ddata.expmt_groups[0]

    ax_handles = [
        'dpl',
        'spec_dpl',
        'spk_L2',
        'spk_L5',
        'I_soma_L5Pyr',
        'spec_I',
    ]

    # iterate over exmpt groups
    for expmt_group in ddata.expmt_groups:
        dfig_dpl = ddata.dfig[expmt_group]['figdpl']

        # grab lists of files (l_)
        l_dpl = ddata.file_match(expmt_group, 'rawdpl')
        l_spk = ddata.file_match(expmt_group, 'rawspk')
        l_param = ddata.file_match(expmt_group, 'param')
        l_spec = ddata.file_match(expmt_group, 'rawspec')
        l_current = ddata.file_match(expmt_group, 'rawcurrent')
        l_spec_current = ddata.file_match(expmt_group, 'rawspeccurrent')

        for f_dpl, f_spk, f_spec, f_current, f_spec_current, f_param \
        in it.izip(l_dpl, l_spk, l_spec, l_current, l_spec_current, l_param):
            # into the pdipole directory, this will plot dipole, spec, and spikes
            # create the axis handle
            f = ac.FigDipoleExp(ax_handles)

            # create the figure name
            fprefix = fio.strip_extprefix(f_dpl) + '-dpl'
            fname = os.path.join(dfig_dpl, fprefix + '.png')

            # grab the dipole
            xlim = dipolefn.pdipole_ax(f.ax['dpl'], f_dpl, f_param)

            # plot the dipole-based spec data
            pc = specfn.pspec_ax(f.ax['spec_dpl'], f_spec)
            f.f.colorbar(pc, ax=f.ax['spec_dpl'])

            # plot the current-based spec data
            pci = specfn.pspec_ax(f.ax['spec_I'], f_spec_current)
            f.f.colorbar(pci, ax=f.ax['spec_I'])

            # get all spikes
            s = spikefn.spikes_from_file(f_param, f_spk)

            # these work primarily because of how the keys are done
            # in the spike dict s (consequence of spikefn.spikes_from_file())
            s_L2 = spikefn.filter_spike_dict(s, 'L2_')
            s_L5 = spikefn.filter_spike_dict(s, 'L5_')

            # resize xlim based on our 50 ms cutoff thingy
            xlim = (50., xlim[1])

            # plot the spikes
            spikefn.spike_png(f.ax['spk_L2'], s_L2)
            spikefn.spike_png(f.ax['spk_L5'], s_L5)

            f.ax['dpl'].set_xlim(xlim)
            f.ax['spec_dpl'].set_xlim(xlim)
            f.ax['spk_L2'].set_xlim(xlim)
            f.ax['spk_L5'].set_xlim(xlim)

            f.savepng(fname)
            f.close()
