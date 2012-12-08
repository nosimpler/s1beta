# spec.py - Average time-frequency energy representation using Morlet wavelet method
#
# v 1.5.1
# rev 2012-12-08 (SL: added from_expmt filter)
# last major: (SL: fixed spec to work with expmts)

import os
import numpy as np
import scipy.signal as sps
import itertools as it
import matplotlib.pyplot as plt
import paramrw
import fileio as fio
from multiprocessing import Pool
from neuron import h as nrn

import fileio as fio
from axes_create import fig_spec

# general spec write/read functions
def write(fdata_spec, t_vec, f_vec, TFR):
    np.savez_compressed(fdata_spec, time=t_vec, freq=f_vec, TFR=TFR)
    # np.savetxt(file_write, self.TFR, fmt = "%5.4f")

def read(fdata_spec):
    data_spec = np.load(fdata_spec)
    return data_spec

class MorletSpec():
    # fdata_spec will be created based on fparam and fdata, a general time series
    def __init__(self, fparam, fdata, fdata_spec):
        # Save variable portion of fdata_spec as identifying attribute
        self.name = fdata_spec

        # function is called this way because paramrw.read() returns 2 outputs
        p_dict = paramrw.read(fparam)[1]

        # Import dipole data and remove extra dimensions from signal array. 
        data_raw = np.loadtxt(open(fdata, 'rb'))
        self.S = data_raw.squeeze()

        # Check that tstop is greater than 150 ms:
        if p_dict['tstop'] > 150.:
            # Remove first 150ms of simulation
            self.S = self.S[150./p_dict['dt']+1:, 1]

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
            if p_dict['save_spec_data']:
                write(fdata_spec, self.timevec, self.freqvec, self.TFR)

        else:
            print "tstop not greater than 150ms. Skipping wavelet analysis."

    def __traces2TFR(self):
        self.S_trans = self.S.transpose()

        # range should probably be 0 to len(self.S_trans)
        self.timevec = 1000. * np.arange(1, len(self.S_trans)+1)/self.fs

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

        t = np.arange(-3.5*st,3.5*st,dt) 
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
            Sc[:] = s[:] - abs(Sft) * np.cos(2.*np.pi*fNoise*tv-np.angle(Sft))

            return Sc

        else:
            s = s.transpose()
            Sc = np.zeros(s.shape)

            for k in range(0, len(s)):
                Sft = ft(s[k,:], fNoise)
                Sc[k,:] = s[k,:] - abs(Sft) * np.cos(2.*np.pi*fNoise*tv-np.angle(Sft))
                
            return Sc.tranpose()

    def __ft(self, s, f):
        tv = np.arange(0,len(s)) / self.fs
        tmp = np.exp(1.j*2. * np.pi * f * tv)
        S = 2 * sum(s * tmp) / len(s)

        return S

def pspec(dspec, dfig, p_dict, key_types):
    timevec = dspec.timevec
    freqvec = dspec.freqvec
    TFR = dspec.TFR

    # timevec = dspec['time']
    # freqvec = dspec['freq']
    # TFR = dspec['TFR']

    # timevec = dspec['TFR'][:, 0]
    # freqvec = np.arange(1, dspec['TFR'].shape[0])
    # TFR = np.delete(dspec['TFR'], (0), axis = 0)
    fprefix = fio.strip_extprefix(dspec.name)

    # Split to find file prefix
    # file_prefix = file_name.split('/')[-1].split('.')[0]
    # fig_name = os.path.join(dfig, file_prefix+'.png')
    fig_name = os.path.join(dfig, fprefix+'.eps')

    # Plot data
    f = fig_spec()
    pc = f.ax0.imshow(TFR, extent=[timevec[0], timevec[-1], freqvec[-1], freqvec[0]], aspect='auto', origin='upper')
    f.f.colorbar(pc)

    plt.xlabel('Time (ms)')
    plt.ylabel('Frequency (Hz)')

    title = [key + ': %2.1f' %p_dict[key] for key in key_types['dynamic_keys']]
    plt.title(title)

    plt.savefig(fig_name)
    f.close()

# this must be globally available for callback function append_spec
spec_results = []

# callback function to aggregate spec results
def append_spec(spec_obj):
    spec_results.append(spec_obj)

# Does spec analysis for all files in simulation directory
# ddir comes from fileio
def analysis(ddir, p_exp):
    # do this per experiment
    for expmt_group in ddir.expmt_groups:
        # get the list of params
        # returns an alpha SORTED list
        param_list = ddir.file_match(expmt_group, 'param')

        # get the list of dipoles
        dpl_list = ddir.file_match(expmt_group, 'rawdpl')

        # create list of spec output names
        # this is sorted because of file_match
        exp_prefix_list = [fio.strip_extprefix(fparam) for fparam in param_list]
        spec_list = [ddir.create_filename(expmt_group, 'rawspec', exp_prefix) for exp_prefix in exp_prefix_list]

        pl = Pool()
        for fparam, fdpl, fspec in it.izip(param_list, dpl_list, spec_list):
            pl.apply_async(MorletSpec, (fparam, fdpl, fspec), callback=append_spec)

        pl.close()
        pl.join()

    return sorted(spec_results, key=lambda spec_obj: spec_obj.name)

# returns spec results *only* for a given experimental group
def from_expmt(spec_result_list, expmt_group):
    return [spec_result for spec_result in spec_result_list if expmt_group in spec_result.name]
