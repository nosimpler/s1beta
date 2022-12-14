# proc_beta_event.py: preprocessing for plotting
# Author: Rob Law

import dipolefn
import currentfn
import fileio
import numpy as np
import paramrw
from matplotlib import pyplot as plt
from collections import defaultdict
import spikefn
from scipy.signal import boxcar, cheby1, filtfilt, lfilter, hilbert
from numpy import hamming, blackman, convolve, ones
import pickle

#def to_matlab(data):
#    pass


# shift window to look at poststimulus period
def time_lock_to_stimulus(pfile):
    #if event:
    #return (0., 0., 0., 0., 710.)
    #else:    
    t0 = paramrw.find_param(pfile, 't_evprox_early')
    t0 -= 25.
    T = t0 + 167.
    return (t0, t0+25., t0+70., t0+135., T)


# average currents for evoked responses    
def mean_currents_over_expmt(dproj, dsim, expmt):
    files, pfiles, _ = get_var_paths(dproj, dsim)
    means = defaultdict(dict)
    for e in files.iterkeys():
        if e == expmt:
            #n_trials = len(files[expmt])
            n_trials = 2
            for file_idx, filename in enumerate(files[expmt][0:1]):
                time, current_dict = get_currents(filename)
                m, c, s = get_stats(current_dict, 1)
                del c, s
                t = time_lock_to_stimulus(pfiles[expmt][file_idx])
                t_interval = [t[0], t[4]]
                print file_idx
                for seg in m.iterkeys():
                    print m[seg].keys()
                    for I in m[seg].iterkeys():
                         
                        m_array = m[seg][I]
                        print m_array.shape
                        interval_idx = time > np.array(t[0])
                        interval_idx2 = time < np.array(t[4])
                        interval_idx = interval_idx*interval_idx2
                        print interval_idx.shape
                        if file_idx == 0:
                            means[seg][I] = m_array[interval_idx][0:7198]/n_trials
                        else:
                            means[seg][I] = means[seg][I] + m_array[interval_idx][0:7198]/n_trials
    return means


# load currents from file
def get_currents(filename):
    current_dict = {}
    f = open(filename, 'rb')
    vars_dict = pickle.load(f)
    f.close()        
    t = vars_dict['cell'].pop('t', None)
    #print t
    if t == None:
        t = vars_dict.pop('t', None)
    # insert line for new t reading here
    current_dict = make_current_dict(vars_dict)
    return t, current_dict

# load voltages from file
def get_voltages(filename):
    voltage_dict = {}
    f = open(filename, 'rb')
    vars_dict = pickle.load(f)
    f.close()        
    t = vars_dict['cell'].pop('t', None)
    #print t
    if t == None:
        t = vars_dict.pop('t', None)
    # insert line for new t reading here
    voltage_dict = make_voltage_dict(vars_dict)
    return t, voltage_dict

# lump spikes together for histogramming
def combine_spikes(spikes_list, t0, expmt):
    celltypes = [
            'L2_pyramidal',
            'L2_basket',
            'L5_pyramidal',
            'L5_basket'
            ]
    spikes = []
    agg_spikes = {}
    bins = {}
    for celltype in celltypes:
        agg_spikes[celltype] = []
        for t, spike_dict in zip(t0, spikes_list):
            spks = spikefn.filter_spike_dict(
                    spike_dict, celltype)[celltype].collapse_all()
            print t
            t = t[0]

            for spk in spks:
                agg_spikes[celltype].append(spk-t)
            
        #flatten = lambda l: [item for sublist in l for item in sublist]
        #agg_spikes[celltype] = flatten(
        #print agg_spikes[celltype]
        bins[celltype] = spikefn.hist_bin_opt(agg_spikes[celltype], 1)
    return agg_spikes, bins
    
# synaptic variables are already currents, but some variables are conductances
# read params to get reversals and convert conductance to current density
# also aggregate into one dictionary
def make_current_dict(var_dict):
    current_dict = var_dict['syn']
    n = len(var_dict['cell'].keys())
    
    for cell in var_dict['cell'].iterkeys():
        for segment in var_dict['cell'][cell].iterkeys():
            for var in var_dict['cell'][cell][segment].iterkeys():
                if var[0] == 'i':
                    current_dict[cell][segment][var] = var_dict['cell'][cell][segment][var]
    return current_dict

# pull voltages from all recorded variables
def make_voltage_dict(var_dict):

    voltage_dict = defaultdict(dict)
    n = len(var_dict['cell'].keys())
    
    for cell in var_dict['cell'].iterkeys():
        for segment in var_dict['cell'][cell].iterkeys():
            voltage_dict[cell][segment] = var_dict['cell'][cell][segment]['v']
    return voltage_dict

# used to get mean values
# currently conf_dict is empty
# requires make_current_dict to be run first
def get_stats(current_dict, n_samples):
    mean_dict = defaultdict(dict)
    conf_dict = {}
    sample_list = []
    n_cells = len(current_dict.keys())
    # will change once variable dictionary written by s1run is fixed
    #print current_dict
    #print current_dict[0].keys()
    t = len(current_dict[0]['apical_1']['i_k'])
    # assumes all cells have the same variables
    for segment in current_dict[0].iterkeys():
        for var in current_dict[0][segment].iterkeys():
            mean_dict[segment][var] = np.zeros((t,))
    for cell in current_dict.iterkeys():
        if cell != 't':
            for segment in current_dict[cell].iterkeys():
                for var in current_dict[cell][segment].iterkeys():
                    mean_dict[segment][var] += np.array(current_dict[cell][segment][var])/n_cells



        if cell in np.random.choice(n_cells, n_samples):
            sample_list.append(current_dict[cell])
    
    return mean_dict, conf_dict, sample_list

# takes the two-level synapse dictionary generated by s1run and returns a 
# three-level dictionary dict[cell][section][syn_var]
def parse_synapses(synapse_dict):

    return new_synapse_dict


# find files associated with a simulation run
def get_var_paths(dproj, dsim, spikes = False):
    simpaths = fileio.SimulationPaths()
    print dproj, dsim
    simpaths.read_sim(dproj, dsim)
    filedict = {}
    pdict = {}
    if spikes:
        spike_dict = {}
    else:
        spike_dict = None
    for expmt in simpaths.expmt_groups:
        print expmt
        filedict[expmt] = simpaths.file_match(expmt, 'vars')
        pdict[expmt] = simpaths.file_match(expmt, 'param')
        if spikes:
            spike_dict[expmt] = simpaths.file_match(expmt, 'rawspk')
    return filedict, pdict, spike_dict

# poorly named: return data and means
# warning: need to specify layer by hand
def compare_time_locked_average(dproj, dsim, WINDOW = False):
    
    simpaths = fileio.SimulationPaths()
    simpaths.read_sim(dproj, dsim)
    print dir(simpaths)
    print simpaths.expmt_groups
    print simpaths.dexpmt_dict
    dplavg = {}
    dpls = defaultdict(dict)
    for expmt in simpaths.expmt_groups:
        files = simpaths.file_match(expmt, 'rawdpl')
        pfiles = simpaths.file_match(expmt, 'param')
        N = float(len(files))
        print N
        dpl0 = dipolefn.Dipole(files[0])
        # was length 7201 for some reason
        t, d = dpl0.truncate_ext(0.,167.)
        #t, d = dpl0.truncate_ext(0., 450.)
        print dir(dpl0)
        dplavg[expmt] = np.zeros(len(d['L2'])) 
        for f_idx, f in enumerate(files):
            dpl = dipolefn.Dipole(f)
            dpl.baseline_renormalize(pfiles[f_idx])
            t0 = paramrw.find_param(pfiles[f_idx], 't_evprox_early')
            
            t0 -= 25.
            T = t0 + 167.
            # hard-code for looking at events
            #t0 = 0
            #T = 450
            #dpl.dpl['agg'] = _cheby(dpl.dpl['agg'])
            print(t0,t)
            t, d = dpl.truncate_ext(t0, T)
            t = t - t0
            window = hamming(333./0.025)
            # replace with L2 or L5 if looking at layer-specific activity.
            dpls[expmt][f_idx] = d['agg']
            if WINDOW:
                dpls[expmt][f_idx] = window_dipole(dpls[expmt][f_idx], 0.025*1e-3)
            dplavg[expmt] += dpls[expmt][f_idx]/N
            
        
        #dplavg[expmt] = window_dipole(dplavg[expmt], 0.025*1e-3)
    return t, dpls, dplavg

# gets spikes time-locked to stimulus
def get_time_locked_spikes(dproj, dsim):

    simpaths = fileio.SimulationPaths()
    simpaths.read_sim(dproj, dsim)
    #print dir(simpaths)
    #print simpaths.expmt_groups
    #print simpaths.dexpmt_dict
    
    spk = defaultdict(dict)
    t_interval = defaultdict(dict)
    for expmt in simpaths.expmt_groups:
        files = simpaths.file_match(expmt, 'rawspk')
        pfiles = simpaths.file_match(expmt, 'param')
        N = float(len(files))
        #spk = spikefn.Spikes(files[0], pfiles[0])
        for f_idx, f in enumerate(files):
            
            spk[expmt][f_idx] = spikefn.spikes_from_file(pfiles[f_idx], f)
            #dpl.baseline_renormalize(pfiles[f_idx])
            t0 = paramrw.find_param(pfiles[f_idx], 't_evprox_early')
            t0 -= 25.
            T = t0 + 167.
            #t0 = 0
            #T = 450.
            t_interval[expmt][f_idx] = [t0, T]
    #print t_interval        
    return t_interval, spk

# compares average currents (not used in paper)
def compare_time_locked_average_current(dproj, dsim):
    simpaths = fileio.SimulationPaths()
    simpaths.read_sim(dproj, dsim)
    print dir(simpaths)
    print simpaths.expmt_groups
    print simpaths.dexpmt_dict
    currentavgL2 = {}
    currentavgL5 = {}
    currentsL2 = defaultdict(dict)
    currentsL5 = defaultdict(dict)
    for expmt in simpaths.expmt_groups:
        files = simpaths.file_match(expmt, 'soma_ina')
        pfiles = simpaths.file_match(expmt, 'param')
        N = float(len(files))
        c0 = currentfn.SynapticCurrent(files[0])
        currentavgL2[expmt] = np.zeros(12001)
        currentavgL5[expmt] = np.zeros(12001)
        for f_idx, f in enumerate(files):
            
            I = currentfn.SynapticCurrent(f)
            #dpl.baseline_renormalize(pfiles[f_idx])
            t0 = paramrw.find_param(pfiles[f_idx], 't_evprox_early')
            t0 -= 25.
            T = t0 + 167.
            t, current = I.truncate_ext(t0, T)
            t = t - t0
            currentavgL2[expmt] += current['L2_Pyr']/N
            currentavgL5[expmt] += current['L5_Pyr']/N
            currentsL2[expmt][f_idx] = current['L2_Pyr']
            currentsL5[expmt][f_idx] = current['L5_Pyr']
    return t, currentsL2, currentsL5, currentavgL2, currentavgL5

# get amplitude distribution for |m50-m70|
# (not used in paper)
def M50_M70(dproj, dsim):
    WINDOW = True 
    #files, pfiles, sp = get_var_paths(dproj, dsim)
    simpaths = fileio.SimulationPaths()
    simpaths.read_sim(dproj,dsim)
    
    m50 = {}
    for expmt in simpaths.expmt_groups:
        #files = simpaths.file_match(expmt, 'rawdpl')
        files = simpaths.file_match(expmt, 'rawdpl')
        pfiles = simpaths.file_match(expmt, 'param')
        m50[expmt] = []
        for f_idx, f in enumerate(files):
            print f_idx
            d = dipolefn.Dipole(f)
             
            t0 = paramrw.find_param(pfiles[f_idx], 't_evprox_early')
            t, d50 = d.truncate_ext(t0+25, t0+75)
            t, d70 = d.truncate_ext(t0+75, t0+125)
            if WINDOW: 
                m50[expmt].append(max(window_dipole(d50['agg']))-min(window_dipole(d70['agg'])))
            else:
                m50[expmt].append(max(d50['agg'])-min(d70['agg']))
    return m50            
        
#just plot one dipole per expmt from file - doesn't work when more than one in dir
def compare_event(dproj, dsim, t_interval):
    simpaths = fileio.SimulationPaths()
    print dproj, dsim
    simpaths.read_sim(dproj,dsim)
    fig = plt.figure()
    fig.hold(True)
    dpl = {}
    for expmt in simpaths.expmt_groups:
        print expmt
        files = simpaths.file_match(expmt, 'rawdpl')
        d = dipolefn.Dipole(files[0])
        d.truncate(t_interval[0], t_interval[-1])
        dpl[expmt] = d.dpl['agg']
        #window = hamming(333./0.025)
        #dpl[expmt] = convolve(dpl[expmt],window)
        t = d.t
    return t, dpl

# compare synaptic currents with and without events
# (not used in paper)
def compare_event_current(dproj, dsim, t_interval, layer = 'L5_Pyr'):
    simpaths = fileio.SimulationPaths()
    simpaths.read_sim(dproj,dsim)
    fig = plt.figure()
    fig.hold(True)
    dpl = {}
    for expmt in simpaths.expmt_groups:
        files = simpaths.file_match(expmt, 'soma_ina')
        d = currentfn.SynapticCurrent(files[0])
        t, I = d.truncate_ext(t_interval[0], t_interval[-1])
        dpl[expmt] = I[layer]
    return t, dpl

#def load_dataset(matfile):
#    pass

# filter
def filter_dipole(dpl, dt):
    from scipy.signal import butter, filtfilt
    fs = 1./dt
    [b,a] = butter(3, [0.3*2./fs, 80.*2./fs], btype='bandpass')
    dpl_filt = filtfilt(b, a, dpl)
    return dpl_filt

# window
def window_dipole(dpl, dt=2.5e-5):
    window = hamming(45e-3/dt)
    # scale factor for putting raw and smoothed on same axis
    dpl_windowed = convolve(window, dpl, mode='same')/(len(window))
    return dpl_windowed

# differentiation
def _diff(dpl):
    d = np.diff(dpl).tolist()
    d.append(d[-1])
    return d

# hilbert transform (some simulation params hardcoded)
def _hilb(dpl):
    b, a = cheby1(3, 10, 2.*np.array([90.,110.])/40000., 'bandpass')
    filtered = filtfilt(b, a, dpl)
    hilb = hilbert(filtered)
    r = np.real(hilb)
    return r

# windowed time-derivative
def _window_diff(dpl):
    return window_dipole(_diff(dpl))


if __name__ == '__main__':
    dproj = '/repo/data/s1'
    dsim = '/repo/data/s1/2016-08-20/beta-005'
    #compare_time_locked_average(dproj, dsim)
    #compare_event(dproj,dsim)
    compute_pseudo_CSD(dproj,dsim)
