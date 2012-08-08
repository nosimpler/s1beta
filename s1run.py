# s1run.py - primary run function for s1 project
#
# v 0.3.0
# rev 2012-08-08 (MS/SL: Now using external feeds from fn/class_feed.py)
# last major: (SL: basket cell grid in place)

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from plottools.axes_create import fig_std

# Cells are defined in './cells'
from cells.L5_pyramidal import L5Pyr
from class_net import Network
from fn.class_feed import FeedProximal, FeedDistal

# Import benchmarking function
from time import clock

from neuron import h as nrn
nrn.load_file("stdrun.hoc")

# All units for time: ms
# this will end up being a function that is called by main
if __name__ == "__main__":
    # Create network from class_net's Network class
    # Network(gridpyr_x, gridpyr_y)
    net = Network(1, 1)

    nrn.tstop = 600.

    # Create feed parameters
    p_feed = {'f_input': 10,
              'tstop': nrn.tstop,
              'origin': net.origin
    }

    # establish feeds
    feed_prox = FeedProximal(net, p_feed)
    feed_dist = FeedDistal(net, p_feed)

    # name compartments internally for this function
    seg_e = net.cells_L5Pyr[0].soma(0.5)
    seg_i = net.cells_L5Basket[0].soma(0.5)

    # Create new vecs
    v_e = nrn.Vector()
    v_i = nrn.Vector()
    t_vec = nrn.Vector()

    # Set to record
    v_e.record(seg_e._ref_v)
    v_i.record(seg_i._ref_v)
    t_vec.record(nrn._ref_t)

    # open data file
    data_file = nrn.File()
    data_file.wopen("testing.dat")
   
    # clock start time
    t0 = clock()

    # initialize cells to -65 mv and compile code
    nrn.finitialize(-65)

    # set state variables if they have been changed since nrn.finitialize
    nrn.fcurrent()

    # nrn.cvode_active(1)

    # run the simulation
    while (nrn.t < nrn.tstop):
        # write time and voltage to data file
        data_file.printf("%03.3f\t%5.4f\n", nrn.t, seg_e.v)

        # advance integration by one tstep
        nrn.fadvance()

    # end clock time
    t1 = clock()
    print "Simulation run time: %4.4f s" % (t1-t0)

    # # attempt at pythonic-ly creating a file
    # for tpoint, vval in zip(t_vec, v_e):
    #     # print item
    #     data_file.printf("%03.3f\t%5.4f\n", tpoint, vval)

    # v_e.printf(data_file)

    # close data file
    data_file.close()

    # create a figure
    testfig = fig_std()
    testfig.ax0.hold(True)

    # plot various bits of data
    testfig.ax0.plot(t_vec, v_e)
    testfig.ax0.plot(t_vec, v_i)
    # testfig.ax0.plot(t_vec, g_ampa)

    # set some axes properties
    # testfig.ax0.set_ylim(-80, 50)

    # save figure as 2 different formats
    # plt.savefig('outputspikes.eps')
    plt.savefig('outputspikes.png')
    testfig.close()

# OLD CODE

# Stimulation params
# stim = nrn.IClamp(seg_e)
# stim.delay = 1
# stim.dur = 100
# stim.amp = 1.
