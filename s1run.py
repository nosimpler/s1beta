from neuron import h

# change the backend for matplotlib
import matplotlib as mpl
# print mpl.get_backend()
mpl.use('Agg')

# import plt and fig_std
import matplotlib.pyplot as plt
from plottools.axes_create import fig_std

# Cells are defined in './cells'
from cells.basket import Inh
from cells.L5_pyramidal import Pyr

# Network is defined in 'class_net.py'
from class_net import Network

# h.load_file("nrngui.hoc")
# from neuron import gui
h.load_file("stdrun.hoc")

# def run_ping(A_input):
if __name__ == "__main__":
    # Create network from class_net's Network class
    net = Network()

    # name compartments
    seg_e = net.cell_list_e[0].soma(0.5)
    # seg_t = net.cell_list_e[0].list_dend[0](0.5)
    seg_i = net.cell_list_i[0].soma(0.5)

    # Stimulation params
    stim = h.IClamp(seg_e)
    stim.delay = 1
    stim.dur = 100
    stim.amp = 100
    # stim.amp = A_input
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

    testfig.ax0.plot(t_vec, v_e)
    # testfig.ax0.plot(t_vec, v_t)
    testfig.ax0.plot(t_vec, v_i)
    testfig.ax0.set_ylim(-80, 50)
    plt.savefig('test_ping.eps')
    # plt.savefig('test_ping.png')
    testfig.close()

    # return h

    # # way to graph in hoc/nrn
    # # for this we need nrngui above
    # G = h.Graph()
    # v_e.line(G, t_vec)
    # v_i.line(G, t_vec)

    # h('objref p')
    # h('p = new PythonObject()')

# if __name__ == "__main__":
#     run_ping(100)
