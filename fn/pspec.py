# pspec.py - Very long plotting methods having to do with spec.
#
# v 1.7.58
# rev 2013-06-06 (SL: minor)
# last major: (SL: using savepng from FigBase())

import os
import sys
import numpy as np
import scipy.signal as sps
import itertools as it
import matplotlib.pyplot as plt
import paramrw
import fileio as fio
import multiprocessing as mp
# from multiprocessing import Pool
from neuron import h as nrn

import fileio as fio
import currentfn
import specfn
import spikefn 
import axes_create as ac

# this is actually a plot kernel for one sim that does dipole, etc.
def pspec_dpl(dspec, f_dpl, dfig, p_dict, key_types, xlim=[0., 'tstop']):
    # if dspec is an instance of MorletSpec, get data from object
    if isinstance(dspec, specfn.MorletSpec):
        timevec = dspec.timevec
        freqvec = dspec.freqvec
        TFR = dspec.TFR

        # Generate file prefix
        fprefix = fio.strip_extprefix(dspec.name) + '-spec'

    # otherwise dspec is path name and data must be loaded from file
    else:
        data_spec = np.load(dspec)

        timevec = data_spec['time']
        freqvec = data_spec['freq']
        TFR = data_spec['TFR']

        # Generate file prefix 
        fprefix = dspec.split('/')[-1].split('.')[0]

    # using png for now
    # fig_name = os.path.join(dfig, fprefix+'.eps')
    fig_name = os.path.join(dfig, fprefix+'.png')

    # set xmin value
    if xlim[0] > timevec[0]:
        xmin = xlim[0]
    else:
        xmin = timevec[0]

    # set xmax value
    if xlim[1] == 'tstop':
        xmax = p_dict['tstop']
    else:
        xmax = xlim[1]

    # vector indices corresponding to xmin and xmax
    xmin_ind = xmin / p_dict['dt']
    xmax_ind = xmax / p_dict['dt']

    # f.f is the figure handle!
    f = ac.FigSpec()

    pc = f.ax['spec'].imshow(TFR[:, xmin_ind:xmax_ind+1], extent=[xmin, xmax, freqvec[-1], freqvec[0]], aspect='auto', origin='upper')
    f.f.colorbar(pc, ax=f.ax['spec'])

    # grab the dipole data
    data_dipole = np.loadtxt(open(f_dpl, 'r'))

    # assign vectors
    t_dpl = data_dipole[xmin_ind:xmax_ind+1, 0]
    dp_total = data_dipole[xmin_ind:xmax_ind+1, 1]

    # plot and create an xlim
    f.ax['dipole'].plot(t_dpl, dp_total)
    x = (xmin, xmax)
    xticks = f.ax['spec'].get_xticks()
    xticks[0] = xmin

    # for now, set the xlim for the other one, force it!
    f.ax['dipole'].set_xlim(x)
    f.ax['dipole'].set_xticks(xticks)
    f.ax['spec'].set_xticks(xticks)

    # set yticks on spectrogram to include 0
    # freq_max = f.ax['spec'].get_ylim()[0]
    # print freq_max
    # yticks = np.arange(0., freq_max+1, 5.)
    # print yticks
    # f.ax['spec'].set_yticks(yticks)

    # axis labels
    f.ax['spec'].set_xlabel('Time (ms)')
    f.ax['spec'].set_ylabel('Frequency (Hz)')

    # create title
    title_str = ac.create_title(p_dict, key_types)
    f.f.suptitle(title_str)
    # title_str = [key + ': %2.1f' % p_dict[key] for key in key_types['dynamic_keys']]

    # use our fig classes to save and close
    f.savepng(fig_name)
    f.close()

# Spectral plotting kernel with alpha feed histogram for ONE simulation run
def pspec_with_hist(dspec, f_dpl, f_spk, dfig, p_dict, gid_dict, key_types, xlim=[0., 'tstop']):
    # if dspec is an instance of MorletSpec,  get data from object
    if isinstance(dspec, MorletSpec):
        timevec = dspec.timevec
        freqvec = dspec.freqvec
        TFR = dspec.TFR

        # Generate file prefix
        fprefix = fio.strip_extprefix(dspec.name) + '-spec'

    # otherwise dspec is path name and data must be loaded from file
    else:
        data_spec = np.load(dspec)

        timevec = data_spec['time']
        freqvec = data_spec['freq']
        TFR = data_spec['TFR']

        # Generate file prefix 
        fprefix = dspec.split('/')[-1].split('.')[0]

    # Create the fig name
    fig_name = os.path.join(dfig, fprefix+'.png')

    # set xmin value
    if xlim[0] > timevec[0]:
        xmin = xlim[0]
    else:
        xmin = timevec[0]

    # set xmax value
    if xlim[1] == 'tstop':
        xmax = p_dict['tstop']
    else:
        xmax = xlim[1]

    # vector indeces corresponding to xmin and xmax
    xmin_ind = xmin / p_dict['dt']
    xmax_ind = xmax / p_dict['dt']

    # f.f is the figure handle!
    f = ac.FigSpecWithHist()

    pc = f.ax['spec'].imshow(TFR[:,xmin_ind:xmax_ind], extent=[xmin, xmax+1, freqvec[-1], freqvec[0]], aspect='auto', origin='upper')
    f.f.colorbar(pc, ax=f.ax['spec'])

    # grab the dipole data
    data_dipole = np.loadtxt(open(f_dpl, 'r'))

    t_dpl = data_dipole[xmin_ind:xmax_ind+1, 0]
    dp_total = data_dipole[xmin_ind:xmax_ind+1, 1]

    f.ax['dipole'].plot(t_dpl, dp_total)
    x = (xmin, xmax)

    # grab alpha feed data. spikes_from_file() from spikefn.py
    s_dict = spikefn.spikes_from_file(gid_dict, f_spk)

    # check for existance of alpha feed keys in s_dict.
    s_dict = spikefn.alpha_feed_verify(s_dict, p_dict)

    # Account for possible delays
    s_dict = spikefn.add_delay_times(s_dict, p_dict)

    # set number of bins (150 bins per 1000ms)
    bins = 150. * (xmax - xmin) / 1000.

    hist = {}

    # Proximal feed
    hist['feed_prox'] = f.ax['feed_prox'].hist(s_dict['alpha_feed_prox'].spike_list, bins, range=[xmin, xmax], color='red', label='Proximal feed', alpha=0.5)

    # f.ax['testing'] = f.ax['feed_prox'].twinx()
    # hist['feed_dist'] = f.ax['testing'].hist(s_dict['alpha_feed_dist'].spike_list, bins, range=[xmin, xmax], color='green', label='Distal feed', alpha=0.5)

    # Distal feed
    hist['feed_dist'] = f.ax['feed_dist'].hist(s_dict['alpha_feed_dist'].spike_list, bins, range=[xmin, xmax], color='green', label='Distal feed')

    # f.ax['testing'].invert_yaxis()
    f.ax['feed_dist'].invert_yaxis()

    # for now, set the xlim for the other one, force it!
    f.ax['dipole'].set_xlim(x)
    f.ax['spec'].set_xlim(x)
    f.ax['feed_prox'].set_xlim(x)
    f.ax['feed_dist'].set_xlim(x)

    # set hist axis props
    f.set_hist_props(hist)

    # axis labels
    f.ax['spec'].set_xlabel('Time (ms)')
    f.ax['spec'].set_ylabel('Frequency (Hz)')

    # Add legend to histogram
    for key in f.ax.keys():
        if 'feed' in key:
            f.ax[key].legend()

    # create title
    title_str = ac.create_title(p_dict, key_types)
    f.f.suptitle(title_str)

    f.savepng(fig_name)
    f.close()
