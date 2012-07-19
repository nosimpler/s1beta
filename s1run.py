# s1run.py - primary run function for s1 project
#
# v 0.2.5
# rev 2012-07-18 (SL: clean up)
# last major: (SL: replaced h calls with nrn calls)

from neuron import h as nrn

# change the backend for matplotlib
import matplotlib as mpl
# print mpl.get_backend()
mpl.use('Agg')

# import plt and fig_std
import matplotlib.pyplot as plt
from plottools.axes_create import fig_std

# Cells are defined in './cells'
from cells.basket import Basket
from cells.L5_pyramidal import L5Pyr

# Network is defined in 'class_net.py'
from class_net import Network

nrn.load_file("stdrun.hoc")
# nrn.load_file("nrngui.hoc")
# from neuron import gui

# this will end up being a function that is called by main
if __name__ == "__main__":
    # Create network from class_net's Network class
    net = Network()

    # name compartments internally for this function
    seg_e = net.cells_L5Pyr[0].soma(0.5)
    seg_i = net.cells_L5Basket[0].soma(0.5)

    # Stimulation params
    stim = nrn.IClamp(seg_e)
    stim.delay = 1
    stim.dur = 100
    stim.amp = 1.
    nrn.tstop = 200

    v_e = nrn.Vector()
    v_e.record(seg_e._ref_v)

    # v_t = nrn.Vector()
    # v_t.record(seg_t._ref_v)

    v_i = nrn.Vector()
    v_i.record(seg_i._ref_v)

    t_vec = nrn.Vector()
    t_vec.record(nrn._ref_t)

    nrn.run()

    # attempt at pythonic-ly creating a file
    data_file = nrn.File()
    data_file.wopen("testing.dat")

    for tpoint, vval in zip(t_vec, v_e):
        # print item
        data_file.printf("%03.3f\t%5.4f\n", tpoint, vval)

    # v_e.printf(data_file)
    data_file.close()

    # nrn.cvode_active(1)

    # plt.plot(v_e)
    # print v_e

    # create a figure
    testfig = fig_std()
    testfig.ax0.hold(True)

    # plot various bits of data
    testfig.ax0.plot(t_vec, v_e)
    testfig.ax0.plot(t_vec, v_i)

    # set some axes properties
    testfig.ax0.set_ylim(-80, 50)

    # save figure as 2 different formats
    # plt.savefig('outputspikes.eps')
    plt.savefig('outputspikes.png')
    testfig.close()

    # net.cells_L5Pyr[0].print_params()
    # print '\n'
    # net.cells_L2Pyr[0].print_params()
    # print '\n'
    # net.cells_L5Basket[0].print_params()
    
    # print "Soma length:", net.cells_L5Pyr[0].soma.L
    # print "Soma diam:", net.cells_L5Pyr[0].soma.diam

    # print "\ndendritic lengths:"
    # for i in range(0, 8):
    #     print net.cells_L5Pyr[0].list_dend[i].L

    # print "\ndendritic diameters:"
    # for i in range(0, 8):
    #     print net.cells_L5Pyr[0].list_dend[i].diam

    # return h

    # # way to graph in hoc/nrn
    # # for this we need nrngui above
    # G = nrn.Graph()
    # v_e.line(G, t_vec)
    # v_i.line(G, t_vec)

    # h('objref p')
    # h('p = new PythonObject()')
