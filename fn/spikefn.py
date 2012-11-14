# spikefn.py - dealing with spikes
#
# v 1.4.3
# rev 2012-11-14 (SL: manually changed the range of the bin checks ... )
# last major: (SL: Added a hist bin optimization function that is/isn't used)

import fileio as fio
import numpy as np
import itertools as it

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

    # plot psth
    def ppsth(self, a):
        # flatten list of spikes
        s_agg = np.array(list(it.chain.from_iterable(self.spike_list)))

        # plot histogram to axis 'a'
        a.hist(s_agg, bins, normed=True, facecolor='g', alpha=0.75)

# splits ext gauss by supplied cell type
# def split_extgauss(s, gid_dict, type):
#     gid_cell = gid_dict[type]
#     gid_extgauss_start = gid_dict['extgauss'][0]
#     gid_extgauss_cell = [gid + gid_extgauss_start for gid in gid_dict[type]]
#
#     return Spikes(s, gid_extgauss_cell)

# splits ext random feeds (of type exttype) by supplied cell type
def split_extrand(s, gid_dict, celltype, exttype):
    gid_cell = gid_dict[celltype]
    gid_exttype_start = gid_dict[exttype][0]
    gid_exttype_cell = [gid + gid_exttype_start for gid in gid_dict[celltype]]

    return Spikes(s, gid_exttype_cell)

# histogram bin optimization
# Shimazaki and Shinomoto, Neural Comput, 2007
def hist_bin_opt(x, N_trials):
    bin_checks = np.linspace(150, 300, 16)
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

# not "purely" from files
def spikes_from_file(gid_dict, fspikes):
    s = np.loadtxt(open(fspikes, 'rb'))

    # get the qnd dict keys from gid_dict
    s_dict = dict.fromkeys(gid_dict)

    # remove extgauss from keys, going to be replaced with a bunch for different types
    del s_dict['extgauss']
    del s_dict['extpois']

    # now iterate over remaining keys
    for key in s_dict.keys():
        # sort of a hack to separate extgauss
        s_dict[key] = Spikes(s, gid_dict[key])

        if key not in 'extinput':
            # figure out its extgauss feed
            newkey_gauss = 'extgauss_' + key
            s_dict[newkey_gauss] = split_extrand(s, gid_dict, key, 'extgauss')
            # s_dict[newkey_gauss] = split_extgauss(s, gid_dict, key)

            # figure out its extpois feed
            newkey_pois = 'extpois_' + key
            s_dict[newkey_pois] = split_extrand(s, gid_dict, key, 'extpois')
            # s_dict[newkey_pois] = split_extpois(s, gid_dict, key)

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
        markerstyle += 'k2'
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

    for key in s_dict.keys():
        # print key, s_dict[key].spike_list
        s_dict[key].tick_marks = y_ticks[tick_start:tick_start+s_dict[key].N_cells]
        tick_start += s_dict[key].N_cells

        markerstyle = get_markerstyle(key)

        # There must be congruency between lines in spike_list and the number of ticks
        i = 0
        for spk_cell in s_dict[key].spike_list:
            # a.plot(np.array([451.6]), e_ticks[i] * np.ones(1), 'k.', markersize=2.5)
            # print len(s_dict[key].tick_marks), len(spk_cell)
            a.plot(spk_cell, s_dict[key].tick_marks[i] * np.ones(len(spk_cell)), markerstyle, markeredgewidth=2, markersize=5)
            i += 1

    a.set_ylim([0, 1])
    a.grid()
