# spikes.py - dealing with spikes
#
# v 1.2.0
# 2012-09-27 (SL: created)
# last major:

import fileio as fio

def CellSpikes():
    def __init__(self):
        pass

def spikes_from_file(fspikes):
    s = fio.clean_lines(fspikes)
    print s

# save_png makes and saves the file name for the png file
def spike_png(a, s_e, s_i):
    # new spikepng function:
    # receive lists of cell spikes and the gid dict for now
    # parse spikes file by cell type
    # output all cell spikes

    # s_e and s_i are lists of spike lists
    # print "in spike_png, s_e is:", s_e, "and s_i is:", s_i

    # get the length of s - new way
    N_e = len(s_e)
    N_i = len(s_i)

    # 2 added to this in order to pad the y_ticks off the x axis and top
    # e_ticks starts at 1 for padding
    # i_ticks ends at -1 for padding
    y_ticks = np.linspace(0, 1, N_e + N_i + 2)
    e_ticks = y_ticks[1:N_e+1]
    i_ticks = y_ticks[-N_i-1:-1]

    # Turn the hold on
    a.hold(True)

    # There must be congruency between lines in spike_list and the number of ticks
    i = 0
    for cell in s_e:
        # print "cell is:", cell
        # a.plot(np.array([451.6]), e_ticks[i] * np.ones(1), 'k.', markersize=2.5)
        a.plot(cell, e_ticks[i] * np.ones(len(cell)), 'k.', markersize=2.5)
        i += 1

    j = 0
    for cell in s_i:
        a.plot(cell, i_ticks[j] * np.ones(len(cell)), 'r|', markeredgewidth=1.5)
        j += 1

    a.grid()
