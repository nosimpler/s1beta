# spec.py - Average time-frequency energy representation using Morlet wavelet method
#
# v 1.6.18af
# rev 2013-01-16 (MS: Possible contribution of delays accounted for in feed times)
# last major: (MS: Alpha feed hist bin size set based on length of simulation)

import os
import sys
import numpy as np
import scipy.signal as sps
import itertools as it
import matplotlib.pyplot as plt
import paramrw
import fileio as fio
from multiprocessing import Pool
from neuron import h as nrn

import fileio as fio
from spikefn import spikes_from_file, add_delay_times
from axes_create import FigSpec, FigSpec_with_hist, fig_std

# general spec write/read functions
def write(fdata_spec, t_vec, f_vec, TFR):
    np.savez_compressed(fdata_spec, time=t_vec, freq=f_vec, TFR=TFR)
    # np.savetxt(file_write, self.TFR, fmt = "%5.4f")

def read(fdata_spec):
    data_spec = np.load(fdata_spec)
    return data_spec

class MorletSpec():
    # fdata_spec will be created based on fparam and fdata, a general time series
    def __init__(self, fparam, fdata, fdata_spec, save_data):
        # Save variable portion of fdata_spec as identifying attribute
        self.name = fdata_spec

        # function is called this way because paramrw.read() returns 2 outputs
        p_dict = paramrw.read(fparam)[1]

        # Import dipole data and remove extra dimensions from signal array. 
        data_raw = np.loadtxt(open(fdata, 'rb'))
        self.S = data_raw.squeeze()

        # cutoff time in ms
        self.tmin = 150.

        # Check that tstop is greater than 150 ms:
        if p_dict['tstop'] > self.tmin:
            # Remove first 150 ms of simulation
            self.S = self.S[self.tmin / p_dict['dt']+1:, 1]

            # Array of frequencies over which to sort
            self.freqvec = np.arange(1., p_dict['spec_max_freq'])

            # Number of cycles in wavelet (>5 advisable)
            self.width = 7.

            # Calculate sampling frequency
            self.fs = 1000./p_dict['dt']

            # Generate Spec data
            self.TFR = self.__traces2TFR()

            # Add time vector as first row of TFR data
            # self.TFR = np.vstack([self.timevec, self.TFR])

            # Write data to file
            if p_dict['save_spec_data'] or save_data:
                write(fdata_spec, self.timevec, self.freqvec, self.TFR)

        else:
            print "tstop not greater than 150ms. Skipping wavelet analysis."

    # also creates self.timevec
    def __traces2TFR(self):
        self.S_trans = self.S.transpose()

        # range should probably be 0 to len(self.S_trans)
        # shift tvec to reflect change
        self.timevec = 1000. * np.arange(1, len(self.S_trans)+1)/self.fs + self.tmin

        B = np.zeros((len(self.freqvec), len(self.S_trans)))
 
        if self.S_trans.ndim == 1:
            for j in range(0, len(self.freqvec)):
                s = sps.detrend(self.S_trans[:])
                B[j,:] = B[j,:] + self.__energyvec(self.freqvec[j], self.__lnr50(s))

            return B

        else:
            for i in range(0, self.S_trans.shape[0]):
                for j in range(0, len(self.freqvec)):
                    s = sps.detrend(self.S_trans[i,:])
                    B[j,:] = B[j,:] + self.__energyvec(self.freqvec[j], self.__lnr50(s))

    def __energyvec(self, f, s):
        # Return an array containing the energy as function of time for freq f
        # The energy is calculated using Morlet's wavelets
        # f: frequency 
        # s: signal
        dt = 1. / self.fs
        sf = f / self.width
        st = 1. / (2.*np.pi*sf)

        t = np.arange(-3.5*st, 3.5*st, dt)
        m = self.__morlet(f, t)
        y = sps.fftconvolve(s, m)
        y = (2. * abs(y) / self.fs)**2
        y = y[np.ceil(len(m)/2.):len(y)-np.floor(len(m)/2.)+1]

        return y

    def __morlet(self, f, t):
        # Morlet's wavelet for frequency f and time t
        # Wavelet normalized so total energy is 1
        # f: specific frequency
        # t: not entirely sure...

        sf = f / self.width
        st = 1. / (2. * np.pi * sf)
        A = 1. / (st * np.sqrt(2.*np.pi))

        y = A * np.exp(-t**2. / (2. * st**2.)) * np.exp(1.j * 2. * np.pi * f * t)

        return y

    def __lnr50(self, s):
        # Line noise reduction (50 Hz) the amplitude and phase of the line notch is estimate.
        # A sinusoid with these characterisitics is then subtracted from the signal.
        # s: signal 

        fNoise = 50.
        tv = np.arange(0,len(s))/self.fs

        if np.ndim(s) == 1:
            Sc = np.zeros(s.shape)
            Sft = self.__ft(s[:], fNoise)
            Sc[:] = s[:] - abs(Sft) * np.cos(2. * np.pi * fNoise * tv - np.angle(Sft))

            return Sc

        else:
            s = s.transpose()
            Sc = np.zeros(s.shape)

            for k in range(0, len(s)):
                Sft = ft(s[k,:], fNoise)
                Sc[k,:] = s[k,:] - abs(Sft) * np.cos(2. * np.pi * fNoise * tv - np.angle(Sft))
                
            return Sc.tranpose()

    def __ft(self, s, f):
        tv = np.arange(0,len(s)) / self.fs
        tmp = np.exp(1.j*2. * np.pi * f * tv)
        S = 2 * sum(s * tmp) / len(s)

        return S

# Spectral plotting kernel for ONE simulation run
def pspec(dspec, f_dpl, dfig, p_dict, key_types):
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

    # Create the fig name in platform dependent manner. If OS, use eps. If linux, use png.
    if sys.platform.startswith('darwin'):
        fig_name = os.path.join(dfig, fprefix+'.eps')

    elif sys.platform.startswith('linux'):
        fig_name = os.path.join(dfig, fprefix+'.png')

    # f.f is the figure handle!
    f = FigSpec()
    pc = f.ax['spec'].imshow(TFR, extent=[timevec[0], timevec[-1], freqvec[-1], freqvec[0]], aspect='auto', origin='upper')
    f.f.colorbar(pc, ax=f.ax['spec'])

    # grab the dipole data
    data_dipole = np.loadtxt(open(f_dpl, 'r'))

    t_dpl = data_dipole[:, 0]
    dp_total = data_dipole[:, 1]

    f.ax['dipole'].plot(t_dpl, dp_total)
    x = (150., f.ax['dipole'].get_xlim()[1])

    # for now, set the xlim for the other one, force it!
    f.ax['dipole'].set_xlim(x)
    f.ax['spec'].set_xlim(x)

    # axis labels
    f.ax['spec'].set_xlabel('Time (ms)')
    f.ax['spec'].set_ylabel('Frequency (Hz)')

    # create title
    title_str = [key + ': %2.1f' % p_dict[key] for key in key_types['dynamic_keys']]
    f.f.suptitle(title_str)

    plt.savefig(fig_name)
    f.close()

# Spectral plotting kernel with alpha feed histogram for ONE simulation run
def pspec_with_hist(dspec, f_dpl, f_spk, dfig, p_dict, gid_dict, key_types):
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

    # Create the fig name in platform dependent manner. If OS, use eps. If linux, use png.
    if sys.platform.startswith('darwin'):
        fig_name = os.path.join(dfig, fprefix+'.eps')

    elif sys.platform.startswith('linux'):
        fig_name = os.path.join(dfig, fprefix+'.png')

    # f.f is the figure handle!
    f = FigSpec_with_hist()
    pc = f.ax['spec'].imshow(TFR, extent=[timevec[0], timevec[-1], freqvec[-1], freqvec[0]], aspect='auto', origin='upper')
    f.f.colorbar(pc, ax=f.ax['spec'])

    # grab the dipole data
    data_dipole = np.loadtxt(open(f_dpl, 'r'))

    t_dpl = data_dipole[:, 0]
    dp_total = data_dipole[:, 1]

    f.ax['dipole'].plot(t_dpl, dp_total)
    x = (150., f.ax['dipole'].get_xlim()[1])

    # grab alpha feed data. spikes_from_file() from spikefn.py
    s_dict = spikes_from_file(gid_dict, f_spk)

    # Account for possible delays
    s_dict = add_delay_times(s_dict, p_dict)

    # set number of bins (150 bins/1000ms)
    bins = 150. * p_dict['tstop'] / 1000.

    # Proximal feed
    f.ax['feed_prox'].hist(s_dict['alpha_feed_prox'].spike_list, bins, range=[timevec[0], timevec[-1]], color='red', label='Proximal feed')

    # Distal feed
    f.ax['feed_dist'].hist(s_dict['alpha_feed_dist'].spike_list, bins, range=[timevec[0], timevec[-1]], color='green', label='Distal feed')

    # for now, set the xlim for the other one, force it!
    f.ax['dipole'].set_xlim(x)
    f.ax['spec'].set_xlim(x)
    f.ax['feed_prox'].set_xlim(x)
    f.ax['feed_dist'].set_xlim(x)

    # axis labels
    f.ax['spec'].set_xlabel('Time (ms)')
    f.ax['spec'].set_ylabel('Frequency (Hz)')

    # Add legend to histogram
    for key in f.ax.keys():
        if 'feed' in key:
            f.ax[key].legend()

    # create title
    title_str = [key + ': %2.1f' % p_dict[key] for key in key_types['dynamic_keys']]
    f.f.suptitle(title_str)

    plt.savefig(fig_name)
    f.close()

# this must be globally available for callback function append_spec
spec_results = []

# callback function to aggregate spec results
def append_spec(spec_obj):
    spec_results.append(spec_obj)

# Does spec analysis for all files in simulation directory
# ddir comes from fileio
def analysis(ddir, p_exp, save_data=0):
    # preallocate lists for use below
    param_list = []
    dpl_list = []
    spec_list = []

    # aggregrate all file from individual expmts into lists
    for expmt_group in ddir.expmt_groups:
        # get the list of params
        # returns an alpha SORTED list
        # store expmt param list temporarily for use below
        param_tmp = ddir.file_match(expmt_group, 'param')

        # add param_tmp to list of all param files
        param_list.extend(param_tmp)

        # get the list of dipoles
        dpl_list.extend(ddir.file_match(expmt_group, 'rawdpl'))

        # create list of spec output names
        # this is sorted because of file_match
        exp_prefix_list = [fio.strip_extprefix(fparam) for fparam in param_tmp]
        spec_list.extend([ddir.create_filename(expmt_group, 'rawspec', exp_prefix) for exp_prefix in exp_prefix_list])

    # perform analysis on all runs from all exmpts at same time
    pl = Pool()
    for fparam, fdpl, fspec in it.izip(param_list, dpl_list, spec_list):
        pl.apply_async(MorletSpec, (fparam, fdpl, fspec, save_data), callback=append_spec)

    pl.close()
    pl.join()

    # sort the spec results by the spec object's name and return
    return sorted(spec_results, key=lambda spec_obj: spec_obj.name)

# returns spec results *only* for a given experimental group
def from_expmt(spec_result_list, expmt_group):
    return [spec_result for spec_result in spec_result_list if expmt_group in spec_result.name]

# Averages spec power over time, returning an array of average pwr per frequency 
def freqpwr_analysis(dspec):
    # dspec may be either raw spec data or pathway to saved spec data

    # if dspec is an instance of MorletSpec,  get data from object
    if isinstance(dspec, MorletSpec):
        timevec = dspec.timevec
        freqvec = dspec.freqvec
        TFR = dspec.TFR

        # get experiment name
        expmt = dspec.name.split('/')[6].split('.')[0]

    # otherwise dspec is path name and data must be loaded from file
    else:
        data_spec = np.load(dspec)

        timevec = data_spec['time']
        freqvec = data_spec['freq']
        TFR = data_spec['TFR']

        # get experiment name
        expmt = dspec.split('/')[6].split('.')[0]

    avg_pwr = TFR.sum(axis=1) / len(timevec)
    max_pwr = avg_pwr.max()
    freq_at_max = freqvec[avg_pwr==max_pwr]

    return {
        'avg_pwr': avg_pwr,
        'max_pwr': max_pwr,
        'freq_at_max': freq_at_max,
        'freq': freqvec,
        'expmt': expmt
    }

def pfreqpwr(file_name, results_list, fparam_list, key_types):
    f = fig_std()
    f.ax0.hold(True)

    legend_list = []

    for result, fparam in it.izip(results_list, fparam_list):
        f.ax0.plot(result['freq'], result['avg_pwr'])

        p = paramrw.read(fparam)[1]
        lgd_temp = [key + ': %2.1f' %p[key] for key in key_types['dynamic_keys']]
        legend_list.append(reduce(lambda x, y: x+', '+y, lgd_temp[:]))

    f.ax0.legend(legend_list, loc = 'upper right')

    f.ax0.set_xlabel('Freq (Hz)')
    f.ax0.set_ylabel('Avg_pwr')

    f.save(file_name)

def pmaxpwr(file_name, results_list, fparam_list):
    f = fig_std()
    f.ax0.hold(True)

    # instantiate lists for storing x and y data
    x_data = []
    y_data = []

    # plot points
    for result, fparam in it.izip(results_list, fparam_list):
        p = paramrw.read(fparam)[1]

        x_data.append(p['f_input_prox'])
        y_data.extend(result['freq_at_max'])

        f.ax0.plot(x_data[-1], y_data[-1], 'kx')

    # add trendline
    fit = np.polyfit(x_data, y_data, 1)
    fit_fn = np.poly1d(fit)

    f.ax0.plot(x_data, fit_fn(x_data), 'k-')

    # Axis stuff
    f.ax0.set_xlabel('Proximal/Distal Input Freq (Hz)')
    f.ax0.set_ylabel('Freq at which max avg power occurs (Hz)')

    f.save(file_name)

