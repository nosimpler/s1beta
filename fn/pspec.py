# pspec.py - Very long plotting methods having to do with spec.
#
# v 1.8.21sc
# rev 2013-07-26 (MS: Plotting routines now use plotting methods in specfn.Spec())
# last major: (MS: Reinstituted use of xlim using logical indexing in pspec_dpl() and pspec_dpl_with_hist())

import os
import sys
import numpy as np
import scipy.signal as sps
import itertools as it
import matplotlib.pyplot as plt
import paramrw
import fileio as fio
import multiprocessing as mp
from neuron import h as nrn

import fileio as fio
import currentfn
import dipolefn
import specfn
import spikefn 
import axes_create as ac

# this is actually a plot kernel for one sim that does dipole, etc.
# needs f_param not p_dict
def pspec_dpl(f_spec, f_dpl, dfig, p_dict, key_types, xlim=None, ylim=None):
    # xlim is a time interval
    # ylim is a frequency interval

    # # Load data from file
    # data_spec = np.load(f_spec)

    # timevec = data_spec['time']
    # freqvec = data_spec['freq']
    # TFR = data_spec['TFR']

    # Generate file prefix 
    fprefix = f_spec.split('/')[-1].split('.')[0]

    # using png for now
    # fig_name = os.path.join(dfig, fprefix+'.eps')
    fig_name = os.path.join(dfig, fprefix+'.png')

    # if xlim is not None:
    #     print "WARNING: xlim input is temporarily disabled. Needs to be fixed in pspec.pspec_dpl()"

    # # Truncate timevec and TFR based on xlim values
    # if xlim:
    #     tvec = timevec[(timevec >= xlim[0]) & (timevec <= xlim[1])]
    #     TFR = TFR[:, ((timevec >= xlim[0]) & (timevec <= xlim[1]))]

    # # Now set update xlim to have values guaranteed to exist
    # xlim_new = (tvec[0], tvec[-1])
    # # for now, a temporary variable for xlim
    # # xlim_new = (timevec[0], timevec[-1])

    # f.f is the figure handle!
    f = ac.FigSpec()

    # # make the extent the entire extent for now
    # extent_xy = [xlim_new[0], xlim_new[-1], freqvec[-1], freqvec[0]]
    # pc = f.ax['spec'].imshow(TFR, extent=extent_xy, aspect='auto', origin='upper')

    # load spec data
    spec = specfn.Spec(f_spec)

    # Plot TFR data and add colorbar
    pc = spec.plot_TFR(f.ax['spec'], 'agg', xlim, ylim) 
    f.f.colorbar(pc, ax=f.ax['spec'])

    # Plot Welch data
    spec.plot_pgram(f.ax['pgram'])

    # grab the dipole data
    # data_dipole = np.loadtxt(open(f_dpl, 'r'))
    dpl = dipolefn.Dipole(f_dpl)

    # plot routine
    dpl.plot(f.ax['dipole'], xlim, 'agg')
    # dpl.plot(f.ax['dipole'], xlim_new, 'agg')

    # # this should not really be here ...
    # pgram = specfn.Welch(dpl.t, dpl.dpl['agg'], p_dict['dt'])
    # pgram.plot_to_ax(f.ax['pgram'], freqvec[-1])

    # plot and create an xlim
    xlim_new = f.ax['spec'].get_xlim()
    xticks = f.ax['spec'].get_xticks()
    xticks[0] = xlim_new[0]

    # for now, set the xlim for the other one, force it!
    f.ax['dipole'].set_xlim(xlim_new)
    f.ax['dipole'].set_xticks(xticks)
    f.ax['spec'].set_xticks(xticks)

    # axis labels
    f.ax['spec'].set_xlabel('Time (ms)')
    f.ax['spec'].set_ylabel('Frequency (Hz)')

    # create title
    title_str = ac.create_title(p_dict, key_types)
    f.f.suptitle(title_str)

    # use our fig classes to save and close
    f.savepng(fig_name)
    f.close()

# Spectral plotting kernel with alpha feed histogram for ONE simulation run
def pspec_with_hist(f_spec, f_dpl, f_spk, dfig, f_param, key_types, xlim=None, ylim=None):
    # Load data from file
    # data_spec = np.load(f_spec)

    # timevec = data_spec['time']
    # freqvec = data_spec['freq']
    # TFR = data_spec['TFR']

    # Generate file prefix 
    fprefix = f_spec.split('/')[-1].split('.')[0]

    # Create the fig name
    fig_name = os.path.join(dfig, fprefix+'.png')

    # load param dict
    _, p_dict = paramrw.read(f_param)

    # Truncate timevec and TFR based on xlim values
    # if xlim:
    #     tvec = timevec[(timevec >= xlim[0]) & (timevec <= xlim[1])]
    #     TFR = TFR[:, (timevec >= xlim[0]) & (timevec <= xlim[1])]

    # # Now set update xlim to have values guaranteed to exist
    # xlim_new = (tvec[0], tvec[-1])

    # # set xmin value
    # if xlim[0] > timevec[0]:
    #     xmin = xlim[0]
    # else:
    #     xmin = timevec[0]

    # # set xmax value
    # if xlim[1] == 'tstop':
    #     xmax = p_dict['tstop']
    # else:
    #     xmax = xlim[1]

    # # vector indeces corresponding to xmin and xmax
    # xmin_ind = xmin / p_dict['dt']
    # xmax_ind = xmax / p_dict['dt']

    # f.f is the figure handle!
    f = ac.FigSpecWithHist()

    # extent_xy = [xlim_new[0], xlim_new[-1], freqvec[-1], freqvec[0]]
    # pc = f.ax['spec'].imshow(TFR, extent=extent_xy, aspect='auto', origin='upper')
    # pc = f.ax['spec'].imshow(TFR[:,xmin_ind:xmax_ind], extent=[xmin, xmax+1, freqvec[-1], freqvec[0]], aspect='auto', origin='upper')

    # load spec data
    spec = specfn.Spec(f_spec)

    # Plot TFR data and add colorbar
    pc = spec.plot_TFR(f.ax['spec'], 'agg', xlim, ylim) 
    f.f.colorbar(pc, ax=f.ax['spec'])

    # set xlim based on TFR plot
    xlim_new = f.ax['spec'].get_xlim()

    # grab the dipole data
    dpl = dipolefn.Dipole(f_dpl)
    dpl.baseline_renormalize(f_param)
    dpl.convert_fAm_to_nAm()

    # plot routine
    dpl.plot(f.ax['dipole'], xlim_new, 'agg')

    # data_dipole = np.loadtxt(open(f_dpl, 'r'))

    # t_dpl = data_dipole[xmin_ind:xmax_ind+1, 0]
    # dp_total = data_dipole[xmin_ind:xmax_ind+1, 1]

    # f.ax['dipole'].plot(t_dpl, dp_total)
    # x = (xmin, xmax)

    # grab alpha feed data. spikes_from_file() from spikefn.py
    s_dict = spikefn.spikes_from_file(f_param, f_spk)

    # check for existance of alpha feed keys in s_dict.
    s_dict = spikefn.alpha_feed_verify(s_dict, p_dict)

    # Account for possible delays
    s_dict = spikefn.add_delay_times(s_dict, p_dict)

    # set number of bins (150 bins per 1000ms)
    bins = 150. * (xlim_new[1] - xlim_new[0]) / 1000.

    hist = {}

    # Proximal feed
    hist['feed_prox'] = f.ax['feed_prox'].hist(s_dict['alpha_feed_prox'].spike_list, bins, range=[xlim_new[0], xlim_new[1]], color='red', label='Proximal feed', alpha=0.5)

    # f.ax['testing'] = f.ax['feed_prox'].twinx()
    # hist['feed_dist'] = f.ax['testing'].hist(s_dict['alpha_feed_dist'].spike_list, bins, range=[xmin, xmax], color='green', label='Distal feed', alpha=0.5)

    # Distal feed
    hist['feed_dist'] = f.ax['feed_dist'].hist(s_dict['alpha_feed_dist'].spike_list, bins, range=[xlim_new[0], xlim_new[1]], color='green', label='Distal feed')

    # f.ax['testing'].invert_yaxis()
    f.ax['feed_dist'].invert_yaxis()

    # for now, set the xlim for the other one, force it!
    f.ax['dipole'].set_xlim(xlim_new)
    f.ax['spec'].set_xlim(xlim_new)
    f.ax['feed_prox'].set_xlim(xlim_new)
    f.ax['feed_dist'].set_xlim(xlim_new)

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

def pspecpwr(file_name, results_list, fparam_list, key_types, error_vec=[]):
    # instantiate fig
    f = ac.FigStd()
    f.set_fontsize(18)

    # pspecpwr_ax is a plot kernel for specpwr plotting
    legend_list = pspecpwr_ax(f.ax0, results_list, fparam_list, key_types)

    # Add error bars if necessary
    if len(error_vec):
        # errors are only used with avg'ed data. There will be only one entry in results_list
        pyerrorbars_ax(f.ax0, results_list[0]['freq'], results_list[0]['p_avg'], error_vec)

    # insert legend
    f.ax0.legend(legend_list, loc='upper right', prop={'size': 8})

    # axes labels
    f.ax0.set_xlabel('Freq (Hz)')
    f.ax0.set_ylabel('Avgerage Power (nAm^2)')

    # add title
    # f.set_title(fparam_list[0], key_types)

    f.save(file_name)
    # f.saveeps(file_name)
    # f.savepng(file_name)
    f.close()

# frequency-power analysis plotting kernel
def pspecpwr_ax(ax_specpwr, specpwr_list, fparam_list, key_types):
    ax_specpwr.hold(True)

    # Preallocate legend list
    legend_list = []

    # iterate over freqpwr results and param list to plot and construct legend
    for result, fparam in it.izip(specpwr_list, fparam_list):
        # Plot to axis
        ax_specpwr.plot(result['freq'], result['p_avg'])

        # Build legend
        p = paramrw.read(fparam)[1]
        lgd_temp = [key + ': %2.1f' %p[key] for key in key_types['dynamic_keys']]
        legend_list.append(reduce(lambda x, y: x+', '+y, lgd_temp[:]))

    # Do not need to return axis, apparently
    return legend_list

# Plot vertical error bars
def pyerrorbars_ax(ax, x, y, yerr_vec):
    ax.errorbar(x, y, xerr=None, yerr=yerr_vec, fmt=None, ecolor='blue')

def aggregate_with_hist(f, ax, f_spec, f_dpl, f_spk, f_param):
    # load param dict
    _, p_dict = paramrw.read(f_param)

    # load spec data from file
    spec = specfn.Spec(f_spec)
    # data_spec = np.load(f_spec)

    # timevec = data_spec['time']
    # freqvec = data_spec['freq']
    # TFR = data_spec['TFR']

    xmin = timevec[0]
    xmax = p_dict['tstop']
    x = (xmin, xmax)

    pc = spec.plot_TFR(ax['spec'], layer='agg', xlim=x)
    # pc = ax['spec'].imshow(TFR, extent=[timevec[0], timevec[-1], freqvec[-1], freqvec[0]], aspect='auto', origin='upper')
    f.f.colorbar(pc, ax=ax['spec'])

    # grab the dipole data
    dpl = dipolefn.Dipole(f_dpl)
    dpl.plot(ax['dipole'], x, layer='agg')
    # data_dipole = np.loadtxt(open(f_dpl, 'r'))

    # t_dpl = data_dipole[xmin/p_dict['dt']:, 0]
    # dp_total = data_dipole[xmin/p_dict['dt']:, 1]

    # ax['dipole'].plot(t_dpl, dp_total)

    # grab alpha feed data. spikes_from_file() from spikefn.py
    s_dict = spikefn.spikes_from_file(f_param, f_spk)

    # check for existance of alpha feed keys in s_dict.
    s_dict = spikefn.alpha_feed_verify(s_dict, p_dict)

    # Account for possible delays
    s_dict = spikefn.add_delay_times(s_dict, p_dict)

    # set number of bins (150 bins/1000ms)
    bins = 150. * (xmax - xmin) / 1000.

    hist = {}

    # Proximal feed
    hist['feed_prox'] = ax['feed_prox'].hist(s_dict['alpha_feed_prox'].spike_list, bins, range=[xmin, xmax], color='red', label='Proximal feed')

    # Distal feed
    hist['feed_dist'] = ax['feed_dist'].hist(s_dict['alpha_feed_dist'].spike_list, bins, range=[xmin, xmax], color='green', label='Distal feed')

    # for now, set the xlim for the other one, force it!
    ax['dipole'].set_xlim(x)
    ax['spec'].set_xlim(x)
    ax['feed_prox'].set_xlim(x)
    ax['feed_dist'].set_xlim(x)

    # set hist axis props
    f.set_hist_props(ax, hist)

    # axis labels
    ax['spec'].set_xlabel('Time (ms)')
    ax['spec'].set_ylabel('Frequency (Hz)')

    # Add legend to histogram
    for key in ax.keys():
        if 'feed' in key:
            ax[key].legend()

    # create title
    # title_str = ac.create_title(p_dict, key_types)
    # f.f.suptitle(title_str)
    # title_str = [key + ': %2.1f' % p_dict[key] for key in key_types['dynamic_keys']]

    # plt.savefig(fig_name)
    # f.close()
