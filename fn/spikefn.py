# spikefn.py - dealing with spikes
#
# v 1.2.25
# 2012-11-01 (SL: Calculating poisson events, too)
# last major: (SL: Minor)

import fileio as fio
import numpy as np

class Spikes():
    def __init__(self, s_all, ranges):
        self.r = ranges
        self.spike_list = self.filter(s_all)
        self.N_cells = len(self.r)
        self.N_spikingcells = len(self.spike_list)

        # this is set externally
        self.tick_marks = []

    def filter(self, s_all):
        spike_list = []

        if len(s_all):
            for ri in self.r:
                srange = s_all[s_all[:, 1] == ri][:, 0]

                srange[srange.argsort()]
                spike_list.append(srange)

        return spike_list

# splits ext gauss by supplied cell type
def split_extgauss(s, gid_dict, type):
    gid_cell = gid_dict[type]
    gid_extgauss_start = gid_dict['extgauss'][0]
    gid_extgauss_cell = [gid + gid_extgauss_start for gid in gid_dict[type]]

    return Spikes(s, gid_extgauss_cell)

# splits ext pois by supplied cell type
def split_extpois(s, gid_dict, type):
    gid_cell = gid_dict[type]
    gid_extpois_start = gid_dict['extpois'][0]
    gid_extpois_cell = [gid + gid_extpois_start for gid in gid_dict[type]]

    return Spikes(s, gid_extpois_cell)

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
            s_dict[newkey_gauss] = split_extgauss(s, gid_dict, key)

            # figure out its extpois feed
            newkey_pois = 'extpois_' + key
            s_dict[newkey_pois] = split_extpois(s, gid_dict, key)

    return s_dict

# from the supplied key name, return a marker style
def get_markerstyle(key):
    markerstyle = ''

    # ext now same color, not ideal yet
    if 'L2' in key:
        markerstyle += 'k'
    elif 'L5' in key:
        markerstyle += 'b'

    # short circuit this by putting extgauss first ... cheap.
    if 'extgauss' in key:
        markerstyle += '.'
    elif 'extpois' in key:
        markerstyle += '.'
    elif 'pyramidal' in key:
        markerstyle += '2'
    elif 'basket' in key:
        markerstyle += '|'

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
