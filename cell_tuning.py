# cell_tuning.py - tune individual cell types
#
# v 0.1.0
# rev 2012-07-19: (created)
# last major: 

from neuron import h

# change the backend for matplotlib
import matplotlib as mpl 
# print mpl.get_backend()
mpl.use('Agg')

# import plt and fig_std
import matplotlib.pyplot as plt 
from plottools.axes_create import fig_std

from cells.L5_pyramidal import L5Pyr
from cells.L2_pyramidal import L2Pyr
from time import clock
h.load_file("stdrun.hoc")
# h.load_file("nrngui.hoc")
# from neuron import gui

def stimulus(seg, filename, figname):
        stim = h.IClamp(seg)
        stim.delay = 50
        stim.dur = 100
        stim.amp = 1.
        h.tstop = 200

        v_e = h.Vector()
        v_e.record(seg._ref_v)

        t_vec = h.Vector()
        t_vec.record(h._ref_t)

        h.run()

        data_file = h.File()
        data_file.wopen(filename)
        
        for tpoint, vval in zip(t_vec, v_e):
            data_file.printf("%03.3f\t%5.4f\n", tpoint, vval)

        data_file.close()
        # create a figure
        testfig = fig_std()
        testfig.ax0.hold(True)

        # plot various bits of data
        testfig.ax0.plot(t_vec, v_e)

        # set some axes properties
        testfig.ax0.set_ylim(-80, 50)

        # save figure as 2 different formats
        # plt.savefig('outputspikes.eps')
        plt.savefig(figname)
        testfig.close()

if __name__ == "__main__":
    # create instanced of L5Pyr and L2Pyr
    cell_L5 = L5Pyr()
    cell_L2 = L2Pyr()

    segL5 = cell_L5.soma(0.5)
    segL2 = cell_L2.soma(0.5)

    # give cells stimulus. Record time and voltage. Save to dat file. Plot.
    stimulus(segL5, "L5PN.dat", "L5PN_plot.png")
    stimulus(segL2, "L2PN.dat", "L2PN_plot.png")    
