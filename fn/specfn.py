# specfn.py - Average time-frequency energy representation using Morlet wavelet method
#
# v 1.8.5
# rev 2013-06-12 (MS: now adding one to maximum freq of spectral analysis so maximum frequency is included by default in anaylsis. Other minor)
# last major: (MS: renamed freqpwr_analysis as specpwr_stationary_avg(). Other minor)

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
import spikefn 
import axes_create as ac

# general spec write function
def write(fdata_spec, t_vec, f_vec, TFR):
    np.savez_compressed(fdata_spec, time=t_vec, freq=f_vec, TFR=TFR)

    # np.savetxt(file_write, self.TFR, fmt = "%5.4f")

# general spec read function
def read(fdata_spec, type='dpl'):
    if type == 'dpl':
        data_spec = np.load(fdata_spec)
        return data_spec

    elif type == 'current':
        # split this up into 2 spec types
        data_spec = np.load(fdata_spec)
        spec_L2 = {
            't': data_spec['t_L2'],
            'f': data_spec['f_L2'],
            'TFR': data_spec['TFR_L2'],
        }

        spec_L5 = {
            't': data_spec['t_L5'],
            'f': data_spec['f_L5'],
            'TFR': data_spec['TFR_L5'],
        }

        return spec_L2, spec_L5

# MorletSpec class based on a time vec tvec and a time series vec tsvec
class MorletSpecSingle():
    # fdata_spec will be created based on fparam and fdata, a general time series
    def __init__(self, fdata_spec, tvec, tsvec, fparam, f_max=None, save_data=None):
        # Save variable portion of fdata_spec as identifying attribute
        self.name = fdata_spec

        # Import dipole data and remove extra dimensions from signal array.
        self.tvec = tvec
        self.tsvec = tsvec

        # function is called this way because paramrw.read() returns 2 outputs
        self.p_dict = paramrw.read(fparam)[1]

        # maximum frequency of analysis
        # Add 1 to ensure analysis is inclusive of maximum frequency
        if not f_max:
            self.f_max = self.p_dict['f_max_spec'] + 1
        else:
            self.f_max = f_max + 1

        # cutoff time in ms
        self.tmin = 50.

        # truncate these vectors appropriately based on tmin
        if self.p_dict['tstop'] > self.tmin:
            # must be done in this order! timeseries first!
            self.tsvec = self.tsvec[self.tvec > self.tmin]
            self.tvec = self.tvec[self.tvec > self.tmin]

        # Check that tstop is greater than tmin
        if self.p_dict['tstop'] > self.tmin:
            # Array of frequencies over which to sort
            self.f = np.arange(1., self.f_max)

            # Number of cycles in wavelet (>5 advisable)
            self.width = 7.

            # Calculate sampling frequency
            self.fs = 1000. / self.p_dict['dt']

            # Generate Spec data
            self.TFR = self.__traces2TFR()

            # Add time vector as first row of TFR data
            # self.TFR = np.vstack([self.timevec, self.TFR])

            # Write data to file ONLY if save_data is ALSO true
            # eg. save_data is an overwriting mechanism
            # if self.p_dict['save_spec_data'] and save_data:
            if save_data == None:
                # if save_data is unspecified, check the p_dict
                if self.p_dict['save_spec_data']:
                    # write(fdata_spec, self.timevec, self.freqvec, self.TFR)
                    self.save(fdata_spec)

            elif save_data:
                # if save_data IS specified, and IF the value evaluates True, THEN write also
                self.save(fdata_spec)
                # write(fdata_spec, self.timevec, self.freqvec, self.TFR)

        else:
            print "tstop not greater than %4.2f ms. Skipping wavelet analysis." % self.tmin

    # externally callable save function
    def save(self, fdata_spec):
        write(fdata_spec, self.timevec, self.freqvec, self.TFR)

    def plot_to_ax(self, ax_spec, dt):
        # pc = ax.imshow(self.TFR, extent=[xmin, xmax, self.freqvec[-1], self.freqvec[0]], aspect='auto', origin='upper')
        pc = ax_spec.imshow(self.TFR, aspect='auto', origin='upper')

        return pc

    # also creates self.timevec
    def __traces2TFR(self):
        self.S_trans = self.tsvec.transpose()
        # self.S_trans = self.S.transpose()

        # range should probably be 0 to len(self.S_trans)
        # shift tvec to reflect change
        self.t = 1000. * np.arange(1, len(self.S_trans)+1)/self.fs + self.tmin - self.p_dict['dt']

        # preallocation
        B = np.zeros((len(self.f), len(self.S_trans)))

        if self.S_trans.ndim == 1:
            for j in range(0, len(self.f)):
                s = sps.detrend(self.S_trans[:])
                B[j, :] += self.__energyvec(self.f[j], s)
                # B[j,:] = B[j,:] + self.__energyvec(self.freqvec[j], self.__lnr50(s))

            return B

        else:
            for i in range(0, self.S_trans.shape[0]):
                for j in range(0, len(self.f)):
                    s = sps.detrend(self.S_trans[i,:])
                    B[j,:] += self.__energyvec(self.f[j], s)
                    # B[j,:] = B[j,:] + self.__energyvec(self.freqvec[j], self.__lnr50(s))

    def __energyvec(self, f, s):
        # Return an array containing the energy as function of time for freq f
        # The energy is calculated using Morlet's wavelets
        # f: frequency 
        # s: signal
        dt = 1. / self.fs
        sf = f / self.width
        st = 1. / (2. * np.pi * sf)

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

# MorletSpec class
class MorletSpec():
    # fdata_spec will be created based on fparam and fdata, a general time series
    def __init__(self, fparam, fdata, fdata_spec, f_max=None, save_data=None):
        # Save variable portion of fdata_spec as identifying attribute
        self.name = fdata_spec

        # function is called this way because paramrw.read() returns 2 outputs
        _, self.p_dict = paramrw.read(fparam)
        # self.p_dict = paramrw.read(fparam)[1]

        # Import dipole data and remove extra dimensions from signal array.
        # data_raw = np.loadtxt(open(fdata, 'rb'))
        dpl = dipolefn.Dipole(fdata)

        # use the Dipole() function convert_fAm_to_nAm() to convert ... from fAm to nAm
        dpl.convert_fAm_to_nAm()

        # using dpl.units to do spectral units, possibly units/Hz
        self.units = "(%s)^2" % dpl.units

        # time vec from the Dipole() object
        self.timevec = dpl.t

        self.S = dpl.dpl['agg']

        # maximum frequency of analysis
        if not f_max:
            f_max = self.p_dict['f_max_spec'] + 1

        # cutoff time in ms
        self.tmin = 50.

        # Check that tstop is greater than tmin
        if self.p_dict['tstop'] > self.tmin:
            # Remove first self.tmin ms of simulation
            self.S = self.S[self.timevec >= self.tmin]
            self.timevec = self.timevec[self.timevec >= self.tmin]
            # self.S = self.S[self.tmin / self.p_dict['dt']:, 1]

            # Array of frequencies over which to sort
            self.freqvec = np.arange(1., f_max)

            # Number of cycles in wavelet (>5 advisable)
            self.width = 7.

            # Calculate sampling frequency
            self.fs = 1000. / self.p_dict['dt']

            # Generate Spec data
            self.TFR = self.__traces2TFR()

            # Write data to file ONLY if save_data is ALSO true
            # eg. save_data is an overwriting mechanism
            # if self.p_dict['save_spec_data'] and save_data:
            if save_data == None:
                # if save_data is unspecified, check the p_dict
                if self.p_dict['save_spec_data']:
                    write(fdata_spec, self.timevec, self.freqvec, self.TFR)

            elif save_data:
                # if save_data IS specified, and IF the value evaluates True, THEN write also
                write(fdata_spec, self.timevec, self.freqvec, self.TFR)

        else:
            print "tstop not greater than %4.2f ms. Skipping wavelet analysis." % self.tmin

    def plot_to_ax(self, ax_spec, dt):
        # pc = ax.imshow(self.TFR, extent=[xmin, xmax, self.freqvec[-1], self.freqvec[0]], aspect='auto', origin='upper')
        pc = ax_spec.imshow(self.TFR, aspect='auto', origin='upper')

        return pc

    # also creates self.timevec
    def __traces2TFR(self):
        self.S_trans = self.S.transpose()

        # range should probably be 0 to len(self.S_trans)
        # shift tvec to reflect change
        # self.timevec = 1000. * np.arange(1, len(self.S_trans)+1)/self.fs + self.tmin - self.p_dict['dt']

        B = np.zeros((len(self.freqvec), len(self.S_trans)))

        if self.S_trans.ndim == 1:
            for j in range(0, len(self.freqvec)):
                s = sps.detrend(self.S_trans[:])
                B[j,:] += self.__energyvec(self.freqvec[j], s)
                # B[j,:] = B[j,:] + self.__energyvec(self.freqvec[j], self.__lnr50(s))

            return B

        else:
            for i in range(0, self.S_trans.shape[0]):
                for j in range(0, len(self.freqvec)):
                    s = sps.detrend(self.S_trans[i,:])
                    B[j,:] += self.__energyvec(self.freqvec[j], s)
                    # B[j,:] = B[j,:] + self.__energyvec(self.freqvec[j], self.__lnr50(s))

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

# spectral plotting kernel should be simpler and take just a file name and an axis handle
# Spectral plotting kernel for ONE simulation run
# ax_spec is the axis handle. fspec is the file name
def pspec_ax(ax_spec, fspec, xlim, layer=None):
    # read is a function in this file to read the fspec
    data_spec = read(fspec)

    if layer in (None, 'agg'):
        TFR = data_spec['TFR']

        if 'f' in data_spec.keys():
            f = data_spec['f']
        else:
            f = data_spec['freq']

    else:
        TFR_layer = 'TFR_%s' % layer
        f_layer = 'f_%s' % layer

        if TFR_layer in data_spec.keys():
            TFR = data_spec[TFR_layer]
            f = data_spec[f_layer]

    extent_xy = [xlim[0], xlim[1], f[-1], 0.]
    pc = ax_spec.imshow(TFR, extent=extent_xy, aspect='auto', origin='upper')
    [vmin, vmax] = pc.get_clim()
    # print np.min(TFR), np.max(TFR)
    # print vmin, vmax
    # ax_spec.colorbar(pc, ax=ax_spec)

    # return (vmin, vmax)
    return pc

# return the max spectral power (simple) for a series of files
def spec_max(ddata, expmt_group, layer='agg'):
    # grab the spec list, assumes it exists
    list_spec = ddata.file_match(expmt_group, 'rawspec')

    # really only perform these actions if there are items in the list
    if len(list_spec):
        # simple prealloc
        val_max = np.zeros(len(list_spec))

        # iterate through list_spec
        i = 0
        for fspec in list_spec:
            data_spec = read(fspec)

            # for now only do the TFR for the aggregate data
            val_max[i] = np.max(data_spec['TFR'])
            i += 1

        return spec_max

# common function to generate spec if it appears to be missing
def generate_missing_spec(ddata, f_max=40):
    # just check first expmt_group
    expmt_group = ddata.expmt_groups[0]

    # list of spec data
    l_spec = ddata.file_match(expmt_group, 'rawspec')

    # if this list is empty, assume it is everywhere and run the analysis function
    if not l_spec:
        spec = analysis(ddata, [], f_max, 1)
    else:
        # this is currently incorrect, it should actually return the data that has been referred to
        # as spec_results. such a function to properly get this without analysis (eg. reader to this data)
        # should exist
        spec = []

    # do the one for current, too. Might as well at this point
    l_speccurrent = ddata.file_match(expmt_group, 'rawspeccurrent')

    if not l_speccurrent:
        p_exp = paramrw.ExpParams(ddata.fparam)
        opts = {
            'type': 'current',
            'f_max': 90.,
            'save_data': 1,
            'runtype': 'debug',
        }
        spec_current = analysis_typespecific(ddata, p_exp, opts)
    else:
        spec_current = []

    return spec

# this must be globally available for callback function append_spec
spec_results = []

# callback function to aggregate spec results
def append_spec(spec_obj):
    spec_results.append(spec_obj)

# parallel kernel for returning the proper spec from the SynapticCurrent() object
# used in analysis_typespecific()
# def spec_current_par_kernel(fparam, fts, fspec, layer='L2'):
#     I_syn = currentfn.SynapticCurrent(fts)
#
#     if layer == 'L2':
#         return 'testing'
#         # return MorletSpecSingle(fspec, I_syn.t, I_syn.I_soma_L2Pyr, fparam, save_data=0)
#
#     elif layer == 'L5':
#         return MorletSpecSingle(fspec, I_syn.t, I_syn.I_soma_L5Pyr, fparam, save_data=0)

# Does spec analysis for all files in simulation directory
# ddata comes from fileio
def analysis_typespecific(ddata, p_exp, opts=None):
    # 'opts' input are the options in a dictionary
    # if opts is defined, then make it well formed
    # the valid keys of opts are in list_opts
    opts_run = {
        'type': 'dpl',
        'f_max': 100.,
        'save_data': 0,
        'runtype': 'parallel',
    }

    # check if opts is supplied
    if opts:
        # assume opts is a dict
        # iterate through provided opts and assign if the key is present
        # otherwise, ignore
        for key, val in opts.iteritems():
            if key in opts_run.keys():
                opts_run[key] = val

    # preallocate lists for use below
    list_param = []
    list_ts = []
    list_spec = []

    # aggregrate all file from individual expmts into lists
    for expmt_group in ddata.expmt_groups:
        # get the list of params
        # returns an alpha SORTED list
        # add to list of all param files
        param_tmp = ddata.file_match(expmt_group, 'param')
        list_param.extend(param_tmp)

        # get the list of dipoles
        if opts_run['type'] in ('dpl', 'dpl_laminar'):
            list_ts.extend(ddata.file_match(expmt_group, 'rawdpl'))

        elif opts_run['type'] == 'current':
            list_ts.extend(ddata.file_match(expmt_group, 'rawcurrent'))

        # create list of spec output names
        # this is sorted because of file_match
        exp_prefix_list = [fio.strip_extprefix(fparam) for fparam in param_tmp]

    # perform analysis on all runs from all exmpts at same time
    if opts_run['type'] == 'current':
        list_spec.extend([ddata.create_filename(expmt_group, 'rawspeccurrent', exp_prefix) for exp_prefix in exp_prefix_list])
        spec_results_L2 = []
        spec_results_L5 = []

        # spec_results_L2 and _L5 now defined locally
        for fparam, fts, fspec in it.izip(list_param, list_ts, list_spec):
            I_syn = currentfn.SynapticCurrent(fts)
            spec_results_L2.append(MorletSpecSingle(fspec, I_syn.t, I_syn.I_soma_L2Pyr, fparam, opts_run['f_max'], save_data=0))
            spec_results_L5.append(MorletSpecSingle(fspec, I_syn.t, I_syn.I_soma_L5Pyr, fparam, opts_run['f_max'], save_data=0))
            # pl.apply_async(spec_current_par_kernel, (fparam, fts, fspec, 'L2'), callback=append_spec_L2)
            # pl.apply_async(spec_current_par_kernel, (fparam, fts, fspec, 'L5'), callback=append_spec_L5)

        # spec_single_ are data from MorletSpecSingle
        for spec_L2, spec_L5, fspec in it.izip(spec_results_L2, spec_results_L5, list_spec):
            np.savez_compressed(fspec, t_L2=spec_L2.t, f_L2=spec_L2.f, TFR_L2=spec_L2.TFR, t_L5=spec_L5.t, f_L5=spec_L5.f, TFR_L5=spec_L5.TFR)

        return spec_results_L2, spec_results_L5

    elif opts_run['type'] == 'dpl_laminar':
        # these should be OUTPUT filenames that are being generated
        list_spec.extend([ddata.create_filename(expmt_group, 'rawspec', exp_prefix) for exp_prefix in exp_prefix_list])
        # also in this case, the original spec results will be overwritten
        # and replaced by laminar specific ones and aggregate ones
        # in this case, list_ts is a list of dipole
        spec_results = []
        spec_results_L2 = []
        spec_results_L5 = []

        # spec_results_L2 and _L5
        for fparam, fts, fspec in it.izip(list_param, list_ts, list_spec):
            dpl = dipolefn.Dipole(fts)

            # do the conversion prior to generating these spec
            dpl.convert_fAm_to_nAm()

            # append various spec results
            spec_results.append(MorletSpecSingle(fspec, dpl.t, dpl.dpl['agg'], fparam, opts_run['f_max'], save_data=0))
            spec_results_L2.append(MorletSpecSingle(fspec, dpl.t, dpl.dpl['L2'], fparam, opts_run['f_max'], save_data=0))
            spec_results_L5.append(MorletSpecSingle(fspec, dpl.t, dpl.dpl['L5'], fparam, opts_run['f_max'], save_data=0))

        # spec_single_ are data from MorletSpecSingle
        for spec_agg, spec_L2, spec_L5, fspec in it.izip(spec_results, spec_results_L2, spec_results_L5, list_spec):
            # the nomenclature "time" and "freq" are used here for backward compatibility only and
            # should be deprecated
            np.savez_compressed(fspec, time=spec_agg.t, freq=spec_agg.f, TFR=spec_agg.TFR, t_L2=spec_L2.t, f_L2=spec_L2.f, TFR_L2=spec_L2.TFR, t_L5=spec_L5.t, f_L5=spec_L5.f, TFR_L5=spec_L5.TFR)

        return spec_results_L2, spec_results_L5

    # probably not a real else.
    else:
        if opts_run['runtype'] == 'parallel':
            pl = mp.Pool()
            for fparam, fts, fspec in it.izip(list_param, list_ts, list_spec):
                pl.apply_async(MorletSpec, (fparam, fts, fspec, opts_run['f_max'], opts_run['save_data']), callback=append_spec)

            pl.close()
            pl.join()

            # sort the spec results by the spec object's name and return
            return sorted(spec_results, key=lambda spec_obj: spec_obj.name)

        elif opts_run['runtype'] == 'debug':
            for fparam, fts, fspec in it.izip(list_param, list_ts, list_spec):
                spec_results.append(MorletSpec(fparam, fts, fspec, opts_run['f_max'], opts_run['save_data']))

            return spec_results

# Does spec analysis for all files in simulation directory
# ddata is a SimulationPaths() object from fileio
def analysis(ddata, p_exp, f_max=None, save_data=None):
    runtype = 'debug'

    # preallocate lists for use below
    param_list = []
    dpl_list = []
    spec_list = []

    # aggregrate all file from individual expmts into lists
    for expmt_group in ddata.expmt_groups:
        # get the list of params
        # returns an alpha SORTED list
        # store expmt param list temporarily for use below
        param_tmp = ddata.file_match(expmt_group, 'param')

        # add param_tmp to list of all param files
        param_list.extend(param_tmp)

        # get the list of dipoles
        dpl_list.extend(ddata.file_match(expmt_group, 'rawdpl'))

        # create list of spec output names
        # this is sorted because of file_match
        exp_prefix_list = [fio.strip_extprefix(fparam) for fparam in param_tmp]
        spec_list.extend([ddata.create_filename(expmt_group, 'rawspec', exp_prefix) for exp_prefix in exp_prefix_list])

    # perform analysis on all runs from all exmpts at same time
    if runtype == 'parallel':
        pl = mp.Pool()
        for fparam, fdpl, fspec in it.izip(param_list, dpl_list, spec_list):
            pl.apply_async(MorletSpec, (fparam, fdpl, fspec, f_max, save_data), callback=append_spec)

        pl.close()
        pl.join()

        # sort the spec results by the spec object's name and return
        return sorted(spec_results, key=lambda spec_obj: spec_obj.name)

    if runtype == 'debug':
        for fparam, fdpl, fspec in it.izip(param_list, dpl_list, spec_list):
            spec_results.append(MorletSpec(fparam, fdpl, fspec, f_max, save_data))

        return spec_results

# returns spec results *only* for a given experimental group
def from_expmt(spec_result_list, expmt_group):
    return [spec_result for spec_result in spec_result_list if expmt_group in spec_result.name]

# Averages spec power over time, returning an array of average pwr per frequency 
def specpwr_stationary_avg(dspec):
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

    # axis = 1 sums over columns
    pwr_avg = TFR.sum(axis=1) / len(timevec)
    pwr_max = pwr_avg.max()
    f_at_max = freqvec[pwr_avg==pwr_max]

    return {
        'p_avg': pwr_avg,
        'p_max': pwr_max,
        'f_max': f_at_max,
        'freq': freqvec,
        'expmt': expmt,
    }

def specpwr_stationary(t, f, TFR):
    # aggregate sum of power of all calculated frequencies
    p = TFR.sum(axis=1)

    # calculate max power
    p_max = p.max()

    # calculate max f
    f_max = f[p==p_max]

    return {
        'p': p,
        'f': f,
        'p_max': p_max,
        'f_max': f_max,
    }

def calc_stderror(data_list):
    # np.std returns standard deviation
    # axis=0 performs standard deviation over rows
    error_vec = np.std(data_list, axis=0)

    return error_vec

# Moved to pspec.py
# def pfreqpwr(file_name, results_list, fparam_list, key_types):
#     f = ac.FigStd()
#     f.ax0.hold(True)
# 
#     legend_list = []
# 
#     for result, fparam in it.izip(results_list, fparam_list):
#         f.ax0.plot(result['freq'], result['avg_pwr'])
# 
#         p = paramrw.read(fparam)[1]
#         lgd_temp = [key + ': %2.1f' %p[key] for key in key_types['dynamic_keys']]
#         legend_list.append(reduce(lambda x, y: x+', '+y, lgd_temp[:]))
# 
#     f.ax0.legend(legend_list, loc = 'upper right')
# 
#     f.ax0.set_xlabel('Freq (Hz)')
#     f.ax0.set_ylabel('Avg_pwr')
# 
#     f.save(file_name)
#     f.close()

def pfreqpwr_with_hist(file_name, freqpwr_result, f_spk, gid_dict, p_dict, key_types):
    f = ac.FigFreqpwrWithHist()
    f.ax['hist'].hold(True)

    xmin = 50.
    xmax = p_dict['tstop']

    f.ax['freqpwr'].plot(freqpwr_result['freq'], freqpwr_result['avgpwr'])

    # grab alpha feed data. spikes_from_file() from spikefn.py
    s_dict = spikefn.spikes_from_file(gid_dict, f_spk)

    # check for existance of alpha feed keys in s_dict.
    s_dict = spikefn.alpha_feed_verify(s_dict, p_dict)

    # Account for possible delays
    s_dict = spikefn.add_delay_times(s_dict, p_dict)

    # set number of bins (150 bins/1000ms)
    bins = 150. * (xmax - xmin) / 1000.
    hist_data = []

    # Proximal feed
    hist_data.extend(f.ax['hist'].hist(s_dict['alpha_feed_prox'].spike_list, bins, range=[xmin, xmax], color='red', label='Proximal feed')[0])

    # Distal feed
    hist_data.extend(f.ax['hist'].hist(s_dict['alpha_feed_dist'].spike_list, bins, range=[xmin, xmax], color='green', label='Distal feed')[0])

    # set hist axis props
    f.set_hist_props(hist_data)

    # axis labels
    f.ax['freqpwr'].set_xlabel('freq (Hz)')
    f.ax['freqpwr'].set_ylabel('power')
    f.ax['hist'].set_xlabel('time (ms)')
    f.ax['hist'].set_ylabel('# spikes')

    # create title
    title_str = ac.create_title(p_dict, key_types)
    f.f.suptitle(title_str)
    # title_str = [key + ': %2.1f' % p_dict[key] for key in key_types['dynamic_keys']]

    f.savepng(file_name)
    f.close()

def aggregate_with_hist(f, ax, dspec, f_dpl, f_spk, p_dict, gid_dict):
    # if dspec is an instance of MorletSpec,  get data from object
    if isinstance(dspec, MorletSpec):
        timevec = dspec.timevec
        freqvec = dspec.freqvec
        TFR = dspec.TFR

    # otherwise dspec is path name and data must be loaded from file
    else:
        data_spec = np.load(dspec)

        timevec = data_spec['time']
        freqvec = data_spec['freq']
        TFR = data_spec['TFR']

    xmin = timevec[0]
    xmax = p_dict['tstop']
    x = (xmin, xmax)

    pc = ax['spec'].imshow(TFR, extent=[timevec[0], timevec[-1], freqvec[-1], freqvec[0]], aspect='auto', origin='upper')
    f.f.colorbar(pc, ax=ax['spec'])

    # grab the dipole data
    data_dipole = np.loadtxt(open(f_dpl, 'r'))

    t_dpl = data_dipole[xmin/p_dict['dt']:, 0]
    dp_total = data_dipole[xmin/p_dict['dt']:, 1]

    ax['dipole'].plot(t_dpl, dp_total)

    # grab alpha feed data. spikes_from_file() from spikefn.py
    s_dict = spikefn.spikes_from_file(gid_dict, f_spk)

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

def pmaxpwr(file_name, results_list, fparam_list):
    f = ac.FigStd()
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
