# praw.py - all of the raw data types on one fig
#
# v 1.7.50irec
# rev 2013-05-01 (SL: Plots raw L5 somatic current)
# last major: (SL: added crude check for L2 versus L5 spikes to plot)

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
        l_current = ddata.file_match(expmt_group, 'rawcurrent')

        for f_dpl, f_spk, f_spec, f_current, f_param in it.izip(l_dpl, l_spk, l_spec, l_current, l_param):
            # into the pdipole directory, this will plot dipole, spec, and spikes
            # create the axis handle
            f = ac.FigDipoleExp(5)

            # create the figure name
            fprefix = fio.strip_extprefix(f_dpl) + '-dpl'
            fname = os.path.join(dfig_dpl, fprefix + '.png')

            # grab the dipole
            xlim = dipolefn.pdipole_ax(f.ax[0], f_dpl, f_param)
            pc = specfn.pspec_ax(f.ax[1], f_spec)
            # f.f.colorbar(pc, ax=f.ax[1])

            # get all spikes
            s = spikefn.spikes_from_file(f_param, f_spk)

            # # crude test to try and automatically choose L2 or L5 spikes
            # N_spikes_true = 0
            # N_spikes_false = 0

            # # test L2 pyrs first
            # for item in s['L2_pyramidal'].spike_list:
            #     # could use a while loop here, but don't need to overcomplicate things
            #     if item.size:
            #         N_spikes_true += 1
            #     else:
            #         N_spikes_false += 1

            # # for now do a total replacement
            # # if there are a
            # if N_spikes_true:
            #     # empty spike dict for L2 with keys that must match keys in s
            #     s_new = {
            #         'L2_pyramidal': None,
            #         'L2_basket': None,
            #     }
            # else:
            #     # use L5 spikes instead
            #     s_new = {
            #         'L5_pyramidal': None,
            #         'L5_basket': None,
            #     }

            # s_new = {
            #     'L2_pyramidal': None,
            #     'L2_basket': None,
            # }

            # these work primarily because of how the keys are done
            # in the spike dict s (consequence of spikefn.spikes_from_file())
            s_L2 = spikefn.filter_spike_dict(s, 'L2_')
            s_L5 = spikefn.filter_spike_dict(s, 'L5_')

            # # clean out s to get the stuff I care about plotting
            # for key in s.iterkeys():
            #     if key in s_new.keys():
            #         s_new[key] = s[key]

            # resize xlim based on our 50 ms cutoff thingy
            xlim = (50., xlim[1])

            # plot the spikes
            spikefn.spike_png(f.ax[2], s_L2)
            spikefn.spike_png(f.ax[3], s_L5)
            f.ax[0].set_xlim(xlim)
            f.ax[2].set_xlim(xlim)
            f.ax[3].set_xlim(xlim)

            # plot the current directly from the file
            currentfn.pcurrent(f.ax[-1], f_current)

            f.savepng(fname)
            f.close()
