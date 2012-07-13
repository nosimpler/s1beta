# s1run.py - primary run function for s1 project
#
# v 0.1.2
# rev 2012-07-12: (MS: cell_list_e and cell_list_i renamed cells_L5Pyr and
# cells_L5Basket respectively. Added cells_L2Pry). 
# last major: (MS: Class Pyr renamed L5Pyr. Calls changed appropriately)

from neuron import h

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

h.load_file("stdrun.hoc")
# h.load_file("nrngui.hoc")
# from neuron import gui

# def run_ping(A_input):
if __name__ == "__main__":
    # Create network from class_net's Network class
    net = Network()

    # name compartments internally for this function
    seg_e = net.cells_L5Pyr[0].soma(0.5)
    seg_i = net.cells_L5Basket[0].soma(0.5)

    # seg_e = net.cell_list_e[0].soma(0.5)
    # seg_i = net.cell_list_i[0].soma(0.5)

    # Stimulation params
    stim = h.IClamp(seg_e)
    stim.delay = 1
    stim.dur = 100
    stim.amp = 5.
    h.tstop = 200

    v_e = h.Vector()
    v_e.record(seg_e._ref_v)

    # v_t = h.Vector()
    # v_t.record(seg_t._ref_v)

    v_i = h.Vector()
    v_i.record(seg_i._ref_v)

    t_vec = h.Vector()
    t_vec.record(h._ref_t)

    h.run()

    # attempt at pythonic-ly creating a file
    data_file = h.File()
    data_file.wopen("testing.dat")

    for tpoint, vval in zip(t_vec, v_e):
        # print item
        data_file.printf("%03.3f\t%5.4f\n", tpoint, vval)

    # v_e.printf(data_file)
    data_file.close()

    # h.cvode_active(1)

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
    # G = h.Graph()
    # v_e.line(G, t_vec)
    # v_i.line(G, t_vec)

    # h('objref p')
    # h('p = new PythonObject()')

# not doing this at the moment in order to see output at the post-run prompt
# if __name__ == "__main__":
#     run_ping(100)
