# spikefn.py - dealing with spikes
#
# v 1.2.5
# 2012-10-01 (SL: created)
# last major:

import fileio as fio
import numpy as np

class Spikes():
    def __init__(self, s_all, ranges):
        self.r = ranges
        self.spike_list = self.filter(s_all)
        self.N_cells = len(self.spike_list)

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

# not "purely" from files
def spikes_from_file(gid_dict, fspikes):
    s = np.loadtxt(open(fspikes, 'rb'))

    s_dict = dict.fromkeys(gid_dict)
    for key in s_dict.keys():
        s_dict[key] = Spikes(s, gid_dict[key])
        # s_dict[key] = s_type.spike_list

    return s_dict

# from the supplied key name, return a marker style
def get_markerstyle(key):
    markerstyle = ''
    if 'L2' in key:
        markerstyle += 'k'
    elif 'L5' in key:
        markerstyle += 'r'
    elif 'ext' in key:
        markerstyle += 'b'

    if 'pyramidal' in key:
        markerstyle += '2'
    elif 'basket' in key:
        markerstyle += '|'
    else:
        markerstyle += '.'

    return markerstyle

# save_png makes and saves the file name for the png file
def spike_png(a, s_dict):
    # new spikepng function:
    # receive lists of cell spikes and the gid dict for now
    # parse spikes file by cell type
    # output all cell spikes

    # s_e and s_i are lists of spike lists
    # print "in spike_png, s_e is:", s_e, "and s_i is:", s_i

    # get the length of s - new way
    N_total = 0
    for key in s_dict.keys():
        N_total += s_dict[key].N_cells

    # 2 added to this in order to pad the y_ticks off the x axis and top
    # e_ticks starts at 1 for padding
    # i_ticks ends at -1 for padding
    y_ticks = np.linspace(0, 1, N_total + 2)
    # y_ticks = np.linspace(0, 1, N_e + N_i + 2)

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
            a.plot(spk_cell, s_dict[key].tick_marks[i] * np.ones(len(spk_cell)), markerstyle, markeredgewidth=2, markersize=10)
            i += 1

    a.grid()
