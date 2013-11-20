# Example of accessing, saving, plotting state variables
#
# v 1.7.11a
# rev 2013-01-30 (SL: FigStd)
# last major:

import sys
sys.path.append("/Users/shane/sandbox/s1beta")

from neuron import h
# from neuron import gui

# change the backend for matplotlib
import matplotlib as mpl 
mpl.use('Agg')

# import plt and FigStd
import matplotlib.pyplot as plt 
from plottools.axes_create import FigStd

from L5_pyramidal import L5Pyr

h.load_file("stdrun.hoc")

def stimulus(seg, file_prefix):
    stim = h.IClamp(seg)
    stim.delay = 50
    stim.dur = 100
    stim.amp = 1.
    # h.steps_per_ms = 20
    h.dt = 0.05
    h.tstop = 200

    t_vec = h.Vector()
    t_vec.record(h._ref_t)

    # v_e = h.Vector()
    # v_e.record(seg._ref_v)

    # record hh gating variable n    
    hh_n_vec = h.Vector()
    hh_n_vec.record(seg._ref_n_hh)

    # record hh gating variable m    
    hh_m_vec = h.Vector()
    hh_m_vec.record(seg._ref_m_hh)

    # record hh gating variable h
    hh_h_vec = h.Vector()
    hh_h_vec.record(seg._ref_h_hh)

    h.wopen(file_prefix+'.dat')
    h.finitialize(-65)
    h.fcurrent()

    while(h.t<=h.tstop):
        # write to file as simulation is in progress
        h.fprint("%03.15f\t%5.4f\n", h.t, seg.v)
        h.fadvance()

    h.wopen()

    data_file = h.File()
    data_file.wopen(file_prefix+'_m_hh'+'.dat')
    
    # write to file after simulation has finished
    for tpoint, vval in zip(t_vec, hh_m_vec):
        data_file.printf("%03.3f\t%5.4f\n", tpoint, vval)

    data_file.close()

    # create a figure
    testfig = FigStd()
    testfig.ax0.hold(True)

    # plot various bits of data
    testfig.ax0.plot(t_vec, hh_n_vec)
    testfig.ax0.plot(t_vec, hh_m_vec)
    testfig.ax0.plot(t_vec, hh_h_vec)

    # set some axes properties
    # testfig.ax0.set_ylim(-80, 50)

    # save figure as 2 different formats
    plt.savefig(file_prefix+'.png')
    # plt.savefig(figname)
    testfig.close()

if __name__ == "__main__":
    # create instanced of L5Pyr 
    cell_L5 = L5Pyr()

    # give cells stimulus. Record time and voltage. Save to dat file. Plot.
    stimulus(cell_L5.soma(0.5), 'L5PN')
