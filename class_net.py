# class_net.py - establishes the Network class and related methods
#
# v 0.1
# rev 2012-07-06 (Adding netCon objects directly to the nc_list instead of creating intermed var)
# last major: (created)
#

from neuron import h
from cells.L5_pyramidal import Pyr
from cells.basket import Inh

# create Network class
class Network():
    def __init__(self):
        self.cell_list_e = []
        self.cell_list_i = []

        # master connect list for all synapses
        self.nc_list = []

        self.create_cells()
        self.connect()

    def create_cells(self):
        self.cell_list_e.append(Pyr())
        self.cell_list_i.append(Inh())

    def connect(self):
        # for now these loops ONLY work because n = 1 for both cells.
        # otherwise, list index changes as you iterate through the loop
        for cell_e in self.cell_list_e:
            for cell_i in self.cell_list_i:
                # from e to i
                self.nc_list.append(cell_e.connect_to_target(cell_i.syn))
                # nc = cell_e.connect_to_target(cell_i.syn)

                # depends on synapse being connected to (mS)
                # only for this ExpSyn and Exp2Syn cases!
                self.nc_list[0].weight[0] = 0.01
                # nc.weight[0] = 0.01

                # ms
                self.nc_list[0].delay = 1
                # nc.delay = 1
                
                # self.nc_list.append(nc)

                # from i to e
                self.nc_list.append(cell_i.connect_to_target(cell_e.syn))
                # nc = cell_i.connect_to_target(cell_e.syn)
                self.nc_list[1].weight[0] = 0
                self.nc_list[1].delay = 1

                # nc.weight[0] = 0
                # nc.weight[0] = 2e-5
                # nc.weight[0] = 0.001
                # nc.delay = 1
                # self.nc_list.append(nc)
