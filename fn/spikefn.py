# spikefn.py - dealing with spikes
#
# v 1.9.2a
# rev 2015-12-15 (SL: only do a histogram if the external inputs existed)
# last major: (minor)

import fileio as fio
import numpy as np
import scipy.signal as sps
import matplotlib.pyplot as plt
import itertools as it
import os
import paramrw

# meant as a class for ONE cell type
class Spikes():
    def __init__(self, s_all, ranges):
        self.r = ranges
        self.spike_list = self.filter(s_all)
        self.N_cells = len(self.r)
        self.N_spikingcells = len(self.spike_list)

        # this is set externally
        self.tick_marks = []

    # returns spike_list, a list of lists of spikes.
    # Each list corresponds to a cell, counted by range
    def filter(self, s_all):
        spike_list = []

        if len(s_all):
            for ri in self.r:
                srange = s_all[s_all[:, 1] == ri][:, 0]

                srange[srange.argsort()]
                spike_list.append(srange)

        return spike_list

    # simple return of all spikes *or* each spike indexed i in every list
    def collapse_all(self, i=None):
        if i == None:
            spk_all = []
            for spk_list in self.spike_list:
                spk_all.extend(spk_list)

        else:
            spk_all = [spk_list[i] for spk_list in self.spike_list if spk_list]

        return spk_all

    # uses self.collapse_all() and returns unique spike times
    def unique_all(self, i=None):
        spk_all = self.collapse_all(i)
        return np.unique(spk_all)

    # plot psth
    def ppsth(self, a):
        # flatten list of spikes
        s_agg = np.array(list(it.chain.from_iterable(self.spike_list)))

        # plot histogram to axis 'a'
        bins = hist_bin_opt(s_agg, 1)
        a.hist(s_agg, bins, normed=True, facecolor='g', alpha=0.75)

# Class to handle extinput event times
class ExtInputs(Spikes):
    def __init__(self, fspk, fparam):
        # load gid and param dicts
        self.gid_dict, self.p_dict = paramrw.read(fparam)

        # parse prox and dist input gids from gid_dict
        self.gid_prox, self.gid_dist = self.__get_extinput_gids()

        # self.inputs is dict of input times with keys 'prox' and 'dist'
        self.inputs = self.__get_extinput_times(fspk)

    def __get_extinput_gids(self):
        # Determine if both feeds exist in this sim
        # If they do, self.gid_dict['extinput'] has length 2
        # If so, first gid is guaraneteed to be prox feed, second to be dist feed
        if len(self.gid_dict['extinput']) == 2:
            return self.gid_dict['extinput']

        # Otherwise, only one feed exists in this sim
        # Must use param file to figure out which one...
        elif self.p_dict['t0_input_prox'] <= self.p_dict['tstop']:
            return self.gid_dict['extinput'][0], None

        elif self.p_dict['t0_input_dist'] <= self.p_dict['tstop']:
            return None, self.gid_dict['extinput'][0]

        else:
            return None, None

    def __get_extinput_times(self, fspk):
        # load all spike times from file
        s_all = np.loadtxt(open(fspk, 'rb'))

        inputs = {}

        # If prox input exists, get spike times
        # self.filter() inherited from Spikes()
        # self.r weirdness is necessary to use self.filter()
        # i.e. self.r must exist and be a list to execute self.filter()
        if self.gid_prox:
            self.r = [self.gid_prox]
            inputs['prox'] = self.filter(s_all)[0]

        else:
            inputs['prox'] = np.array([])

        # If dist input exists, get spike times
        if self.gid_dist:
            self.r = [self.gid_dist]
            inputs['dist'] = self.filter(s_all)[0]

        else:
            inputs['dist'] = np.array([])

        return inputs

    def truncate_ext(self, dtype, t_int):
        if dtype == 'prox' or dtype == 'dist':
            tmask = (self.inputs[dtype] >= t_int[0]) & (self.inputs[dtype] <= t_int[1])
            return self.inputs[dtype][tmask]

        if dtype == 'env':
            tmask = (self.inputs['t'] >= t_int[0]) & (self.inputs['t'] <= t_int[1])
            return [self.inputs[dtype][tmask], self.inputs['t'][tmask]]

    def add_delay_times(self):
        # if prox delay to both layers is the same, add it to the prox input times
        if self.p_dict['input_prox_A_delay_L2'] == self.p_dict['input_prox_A_delay_L5']:
            self.inputs['prox'] += self.p_dict['input_prox_A_delay_L2']

        # if dist delay to both layers is the same, add it to the dist input times
        if self.p_dict['input_dist_A_delay_L2'] == self.p_dict['input_dist_A_delay_L5']:
            self.inputs['dist'] += self.p_dict['input_dist_A_delay_L2']

    def get_envelope(self, tvec, feed='dist', bins=150):
        h_range = (tvec[0], tvec[-1])
        hist, edges = np.histogram(self.inputs[feed], bins=bins, range=h_range)
        centers = edges[0:bins] + np.diff(edges) / 2.

        num = len(tvec)
        env, t = sps.resample(hist, num, t=centers)

        self.inputs['env'] = env
        self.inputs['t'] = t

    def plot_hist(self, ax, extinput, tvec, bins=150, xlim=None, color='green'):
        if not xlim:
            xlim = (0., p_dict['tstop'])

        if len(self.inputs[extinput]):
            hist = ax.hist(self.inputs[extinput], bins, range=xlim, color=color, label=extinput)

        else:
            hist = None

        return hist

# filters spike dict s_dict for keys that start with str_startswith
def filter_spike_dict(s_dict, str_startswith):
    """ easy enough to modify for future conditions
        just fix associated functions
    """
    s_filt = {}
    for key, val in s_dict.iteritems():
        if key.startswith(str_startswith):
            s_filt[key] = val

    return s_filt

# weird bin counting function
def bin_count(bins_per_second, tinterval):
    return bins_per_second * tinterval / 1000.

# splits ext random feeds (of type exttype) by supplied cell type
def split_extrand(s, gid_dict, celltype, exttype):
    gid_cell = gid_dict[celltype]
    gid_exttype_start = gid_dict[exttype][0]
    gid_exttype_cell = [gid + gid_exttype_start for gid in gid_dict[celltype]]

    return Spikes(s, gid_exttype_cell)

# histogram bin optimization
def hist_bin_opt(x, N_trials):
    """ Shimazaki and Shinomoto, Neural Comput, 2007
    """
    bin_checks = np.arange(80, 300, 10)
    # bin_checks = np.linspace(150, 300, 16)

    costs = np.zeros(len(bin_checks))

    i = 0
    # this might be vectorizable in np
    for n_bins in bin_checks:
        # use np.histogram to do the numerical minimization
        pdf, bin_edges = np.histogram(x, n_bins)

        # calculate bin width
        # some discrepancy here but should be fine
        w_bin = np.unique(np.diff(bin_edges))
        if len(w_bin) > 1:
            w_bin = w_bin[0]

        # calc mean and var
        kbar = np.mean(pdf)
        kvar = np.var(pdf)

        # calc cost
        costs[i] = (2*kbar - kvar) / (N_trials * w_bin)**2
        i += 1

    # find the bin size corresponding to a minimization of the costs
    bin_opt_list = bin_checks[costs.min() == costs]
    bin_opt = bin_opt_list[0]

    print bin_opt
    return bin_opt

# "purely" from files, this is the new way to replace the old way
def spikes_from_file(fparam, fspikes):
    gid_dict, _ = paramrw.read(fparam)

    # cell list - requires cell to start with L2/L5
    src_list = []
    src_extinput_list = []
    src_unique_list = []

    # fill in 2 lists from the keys
    for key in gid_dict.keys():
        if key.startswith('L2_') or key.startswith('L5_'):
            src_list.append(key)

        elif key == 'extinput':
            src_extinput_list.append(key)

        else:
            src_unique_list.append(key)

    # check to see if there are spikes in here, otherwise return an empty array
    if os.stat(fspikes).st_size:
        s = np.loadtxt(open(fspikes, 'rb'))

    else:
        s = np.array([], dtype='float64')

    # get the skeleton s_dict from the cell_list
    s_dict = dict.fromkeys(src_list)

    # iterate through just the src keys
    for key in s_dict.keys():
        # sort of a hack to separate extgauss
        s_dict[key] = Spikes(s, gid_dict[key])

        # figure out its extgauss feed
        newkey_gauss = 'extgauss_' + key
        s_dict[newkey_gauss] = split_extrand(s, gid_dict, key, 'extgauss')

        # figure out its extpois feed
        newkey_pois = 'extpois_' + key
        s_dict[newkey_pois] = split_extrand(s, gid_dict, key, 'extpois')

    # do the keys in unique list
    for key in src_unique_list:
        s_dict[key] = Spikes(s, gid_dict[key])

    # Deal with alpha feeds (extinputs)
    # order guaranteed by order of inputs in p_ext in paramrw
    # and by details of gid creation in class_net
    # A little kludgy to deal with the fact that one might not exist
    if len(gid_dict['extinput']) > 1:
        s_dict['alpha_feed_prox'] = Spikes(s, [gid_dict['extinput'][0]])
        s_dict['alpha_feed_dist'] = Spikes(s, [gid_dict['extinput'][1]])

    else:
        # not sure why this is done here
        # handle the extinput: this is a LIST!
        s_dict['extinput'] = [Spikes(s, [gid]) for gid in gid_dict['extinput']]

    return s_dict

# from the supplied key name, return a marker style
def get_markerstyle(key):
    markerstyle = ''

    # ext now same color, not ideal yet
    # if 'L2' in key:
    #     markerstyle += 'k'
    # elif 'L5' in key:
    #     markerstyle += 'b'

    # short circuit this by putting extgauss first ... cheap.
    if 'extgauss' in key:
        markerstyle += 'k.'
    elif 'extpois' in key:
        markerstyle += 'k.'
    elif 'pyramidal' in key:
        markerstyle += 'k.'
    elif 'basket' in key:
        markerstyle += 'r|'

    return markerstyle

# spike_png plots spikes based on input dict
def spike_png(a, s_dict):
    # new spikepng function:
    # receive lists of cell spikes and the gid dict for now
    # parse spikes file by cell type
    # output all cell spikes

    # get the length of s - new way
    N_total = 0
    for key in s_dict.keys():
        N_total += s_dict[key].N_cells

    # 2 added to this in order to pad the y_ticks off the x axis and top
    # e_ticks starts at 1 for padding
    # i_ticks ends at -1 for padding
    y_ticks = np.linspace(0, 1, N_total + 2)

    # Turn the hold on
    a.hold(True)

    # define start point
    tick_start = 1

    # sort the keys by alpha: consistency in names will lead to consistent behavior here
    # reverse=True because _basket comes before _pyramidal, and the spikes plot bottom up
    key_list = [key for key in s_dict.keys()]
    key_list.sort(reverse=True)

    # for key in s_dict.keys():
    for key in key_list:
        # print key, s_dict[key].spike_list
        s_dict[key].tick_marks = y_ticks[tick_start:tick_start+s_dict[key].N_cells]
        tick_start += s_dict[key].N_cells

        markerstyle = get_markerstyle(key)

        # There must be congruency between lines in spike_list and the number of ticks
        i = 0
        print key
        print s_dict[key].spike_list
        for spk_cell in s_dict[key].spike_list:
            # a.plot(np.array([451.6]), e_ticks[i] * np.ones(1), 'k.', markersize=2.5)
            # print len(s_dict[key].tick_marks), len(spk_cell)
            a.plot(spk_cell, s_dict[key].tick_marks[i] * np.ones(len(spk_cell)), markerstyle, markeredgewidth=1, markersize=2.5)
            i += 1

    a.set_ylim([0, 1])
    #a.grid()

# Add synaptic delays to alpha input times if applicable:
def add_delay_times(s_dict, p_dict):
    # Only add delays if delay is same for L2 and L5
    # Proximal feed
    # if L5 delay is -1, has same delays as L2
    # if p_dict['input_prox_A_delay_L5'] == -1:
    #     s_dict['alpha_feed_prox'].spike_list = [num+p_dict['input_prox_A_delay_L2'] for num in s_dict['alpha_feed_prox'].spike_list]

    # else, check to see if delays are the same anyway
    # else:
    if s_dict['alpha_feed_prox'].spike_list and p_dict['input_prox_A_delay_L2'] == p_dict['input_prox_A_delay_L5']:
        s_dict['alpha_feed_prox'].spike_list = [num+p_dict['input_prox_A_delay_L2'] for num in s_dict['alpha_feed_prox'].spike_list]

    # Distal
    # if L5 delay is -1, has same delays as L2
    # if p_dict['input_dist_A_delay_L5'] == -1:
    #     s_dict['alpha_feed_dist'].spike_list = [num+p_dict['input_dist_A_delay_L2'] for num in s_dict['alpha_feed_dist'].spike_list]

    # else, check to see if delays are the same anyway
    # else:
    if s_dict['alpha_feed_dist'].spike_list and p_dict['input_dist_A_delay_L2'] == p_dict['input_dist_A_delay_L5']:
        s_dict['alpha_feed_dist'].spike_list = [num+p_dict['input_dist_A_delay_L2'] for num in s_dict['alpha_feed_dist'].spike_list]

    return s_dict

# Checks for existance of alpha feed keys in s_dict.
def alpha_feed_verify(s_dict, p_dict):
    """ If they do not exist, then simulation used one or no feeds. Creates keys accordingly
    """
    # check for existance of keys. If exist, do nothing
    if 'alpha_feed_prox' and 'alpha_feed_dist' in s_dict.keys():
        pass

    # if they do not exist, create them and add proper data
    else:
        # if proximal feed's t0 < tstop, it exists and data is stored in s_dict['extinputs'].
        # distal feed does not exist and gets empty list
        if p_dict['t0_input_prox'] < p_dict['tstop']:
            s_dict['alpha_feed_prox'] = s_dict['extinput']

            # make object on the fly with attribute 'spike_list'
            # A little hack-y
            s_dict['alpha_feed_dist'] = type('emptyspike', (object,), {'spike_list': np.array([])})

        # if distal feed's t0 < tstop, it exists and data is stored in s_dict['extinputs'].
        # Proximal feed does not exist and gets empty list
        elif p_dict['t0_input_dist'] < p_dict['tstop']:
            s_dict['alpha_feed_prox'] = type('emptyspike', (object,), {'spike_list': np.array([])})
            s_dict['alpha_feed_dist'] = s_dict['extinput']

        # if neither had t0 < tstop, neither exists and both get empty list
        else:
            s_dict['alpha_feed_prox'] = type('emptyspike', (object,), {'spike_list': np.array([])})
            s_dict['alpha_feed_dist'] = type('emptyspike', (object,), {'spike_list': np.array([])})

    return s_dict

# input histogram on 2 axes
def pinput_hist(a0, a1, s_list0, s_list1, n_bins, xlim):
    hists = {
        'prox': a0.hist(s_list0, n_bins, color='red', label='Proximal input', alpha=0.75),
        'dist': a1.hist(s_list1, n_bins, color='green', label='Distal input', alpha=0.75),
    }

    # assumes these axes are inverted and figure it out
    ylim_max = 2*np.max([a0.get_ylim()[1], a1.get_ylim()[1]]) + 1

    # set the ylims here
    a0.set_ylim((0, ylim_max))
    a1.set_ylim((0, ylim_max))

    a0.set_xlim(xlim)
    a1.set_xlim(xlim)

    a1.invert_yaxis()

    return hists

def pinput_hist_onesided(a0, s_list, n_bins):
    hists = {
        'prox': a0.hist(s_list, n_bins, color='k', label='Proximal input', alpha=0.75),
    }

    return hists

if __name__ == '__main__':
    pass
