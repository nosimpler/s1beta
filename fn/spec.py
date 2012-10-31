# spec.py - Average time-frequency energy representation using Morlet wavelet method
#
# v 1.2.24
# rev 2012-10-31 (MS: title includes key/value pairs for keys whose value changes over runs)
# last major: (MS: Added tstop check before analysis, p_dict input for title generation)

import os
import numpy as np
import scipy.signal as sps
import itertools as it
import matplotlib.pyplot as plt
from neuron import h as nrn

class MorletSpec():
    def __init__(self, file_name, dfig, p_dict, key_types):

        # Split to find file prefix
        self.file_prefix = file_name.split('/')[-1].split('dpl')[0]
        self.fig_name = os.path.join(dfig, self.file_prefix+'spec.png')

        # Save p_dict, key_types as self dictionary
        self.p = p_dict
        self.key_types = key_types
        # print [string + ': %2.1f' %p_dict[string] for string in self.key_types['dynamic_keys']]


        # Import dipole data and remove extra dimensions from signal array. 
        data_raw = np.loadtxt(open(file_name, 'rb'))
        self.S = data_raw.squeeze()

        # Check that tstop is greater than 150 ms:
        if nrn.tstop > 150.:
            # Remove first 150ms of simulation
            self.S = self.S[150./nrn.dt:, 1]

            # Array of frequencies over which to sort
            self.freqvec = np.arange(1., p_dict['spec_max_freq'])

            # Number of cycles in wavelet (>5 advisable)
            self.width = 7.

            # Calculate sampling frequency
            self.fs = 1000./nrn.dt

            self.TFR = self.traces2TFR()
            self.plot()

        else:
            print "tstop not greater than 150ms. Skipping wavelet analysis."

    def traces2TFR(self):
        self.S_trans = self.S.transpose()
        # LNR50 = 1

        # range should probably be 0 to len(self.S_trans)
        self.timevec = 1000. * np.arange(1, len(self.S_trans))/self.fs

        B = np.zeros((len(self.freqvec), len(self.S_trans)))
 
        if self.S_trans.ndim == 1:
            for j in range(0, len(self.freqvec)):
                    s = sps.detrend(self.S_trans[:])
                    B[j,:] = B[j,:] + self.energyvec(self.freqvec[j], self.lnr50(s))

            return B

        else:
            for i in range(0, self.S_trans.shape[0]):
                for j in range(0, len(self.freqvec)):
                    s = sps.detrend(self.S_trans[i,:])
                    B[j,:] = B[j,:] + self.energyvec(self.freqvec[j], self.lnr50(s))

    def energyvec(self, f, s):
        # Return an array containing the energy as function of time for freq f
        # The energy is calculated using Morlet's wavelets
        # f: frequency 
        # s: signal

        dt = 1. / self.fs
        sf = f / self.width
        st = 1. / (2.*np.pi*sf)

        t = np.arange(-3.5*st,3.5*st,dt) 
        m = self.morlet(f, t)
        y = sps.fftconvolve(s, m)
        y = (2. * abs(y) / self.fs)**2
        y = y[np.ceil(len(m)/2.):len(y)-np.floor(len(m)/2.)+1]

        return y

    def morlet(self, f, t):
        # Morlet's wavelet for frequency f and time t
        # Wavelet normalized so total energy is 1
        # f: specific frequency
        # t: not entirely sure...

        sf = f / self.width
        st = 1. / (2. * np.pi * sf)
        A = 1. / (st * np.sqrt(2.*np.pi))

        y = A * np.exp(-t**2./(2.*st**2.)) * np.exp(1.j*2.*np.pi*f*t)

        return y

    def lnr50(self, s):
        # Line noise reduction (50 Hz) the amplitude and phase of the line notch is estimate.
        # A sinusoid with these characterisitics is then subtracted from the signal.
        # s: signal 

        fNoise = 50.
        tv = np.arange(0,len(s))/self.fs

        if np.ndim(s) == 1:
            Sc = np.zeros(s.shape)
            Sft = self.ft(s[:], fNoise)
            Sc[:] = s[:] - abs(Sft) * np.cos(2.*np.pi*fNoise*tv-np.angle(Sft))

            return Sc

        else:
            s = s.transpose()
            Sc = np.zeros(s.shape)

            for k in range(0, len(s)):
                Sft = ft(s[k,:], fNoise)
                Sc[k,:] = s[k,:] - abs(Sft) * np.cos(2.*np.pi*fNoise*tv-np.angle(Sft))
                
            return Sc.tranpose()

    def ft(self, s, f):
        tv = np.arange(0,len(s)) / self.fs
        tmp = np.exp(1.j*2. * np.pi * f * tv)
        S = 2 * sum(s * tmp) / len(s)

        return S

    def plot(self):
        plt.imshow(self.TFR, extent=[self.timevec[0], self.timevec[-1], self.freqvec[-1], self.freqvec[0]], aspect='auto', origin='upper')
        plt.colorbar()

        plt.xlabel('Time (ms)')
        plt.ylabel('Frequency (Hz)')

        title = [key + ': %2.1f' %self.p[key] for key in self.key_types['dynamic_keys']]
        plt.title(title)

        # plt.title('f_input_prox: %2.1f; f_input_dist: %2.1f' %(self.p['f_input_prox'], self.p['f_input_dist']))

        plt.savefig(self.fig_name)
        plt.close()
