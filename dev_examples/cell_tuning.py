# cell_tuning.py - tune individual cell types
#
# v 1.2.17
# rev 2012-10-25 (SL: some minor changes, untested)
# last major: (MS: Added units)

from neuron import h

# change the backend for matplotlib
import matplotlib as mpl 
mpl.use('Agg')

# import plt and fig_std
import matplotlib.pyplot as plt 
from ..plottools.axes_create import fig_std

from ..fn.cells.L5_pyramidal import L5Pyr
from ..fn.cells.L2_pyramidal import L2Pyr

h.load_file("stdrun.hoc")

# All units for time: ms

def stimulus(seg, file_prefix):
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
    data_file.wopen(file_prefix+'.dat')
    
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
    plt.savefig(file_prefix+'.png')
    testfig.close()

if __name__ == "__main__":
    # create instanced of L5Pyr and L2Pyr
    cell_L5 = L5Pyr()
    cell_L2 = L2Pyr()

    # give cells stimulus. Record time and voltage. Save to dat file. Plot.
    stimulus(cell_L5.soma(0.5), 'L5PN')
    stimulus(cell_L2.soma(0.5), 'L2PN')
