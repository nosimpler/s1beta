# cell_tuning.py - tune individual cell types
#
# v 1.7.11a
# rev 2012-11-26 (MS: Updated to work with present version of code)
# last major: (SL: some minor changes, untested)

# change the backend for matplotlib
import matplotlib as mpl 
# mpl.use('Agg')

# import plt and FigStd
import matplotlib.pyplot as plt 
from ..fn.axes_create import FigStd

from neuron import h as nrn
nrn.load_file("stdrun.hoc")

from ..fn.cells.L5_pyramidal import L5Pyr
from ..fn.cells.L2_pyramidal import L2Pyr

# All units for time: ms

def stimulus(seg, file_prefix):
    stim = nrn.IClamp(seg)
    stim.delay = 50.
    stim.dur = 100
    stim.amp = 1.
    nrn.tstop = 200.

    v_e = nrn.Vector()
    v_e.record(seg._ref_v)

    t_vec = nrn.Vector()
    t_vec.record(nrn._ref_t)

    nrn.run()

    data_file = nrn.File()
    data_file.wopen(file_prefix+'.dat')
    
    for tpoint, vval in zip(t_vec, v_e):
        data_file.printf("%03.3f\t%5.4f\n", tpoint, vval)

    data_file.close()

    # create a figure
    testfig = FigStd()
    testfig.ax0.hold(True)

    # plot various bits of data
    testfig.ax0.plot(t_vec, v_e)

    # set some axes properties
    testfig.ax0.set_ylim(-80, 50)

    # save figure as 2 different formats
    plt.savefig(file_prefix+'.png')
    testfig.close()

if __name__ == "__main__":
    nrn("dp_total = 0.")

    # create instanced of L5Pyr and L2Pyr
    cell_L5 = L5Pyr((0., 0., 0.))
    cell_L2 = L2Pyr((0., 0., 0.))

    # give cells stimulus. Record time and voltage. Save to dat file. Plot.
    stimulus(cell_L5.soma(0.5), 'L5PN')
    stimulus(cell_L2.soma(0.5), 'L2PN')
