# class_net.py - establishes the Network class and related methods
#
# v 0.1.2
# rev 2012-07-13 (renamed cell_list_e and cell_list_i to cells_L5Pyr and 
# cells_L5Basket respectively. Added cells_L2Pyr and cells_L2Basket
# added an L2 PN to the network, but do not connect it to anything)
# last major: (Class Pyr change to L5Pyr. Calls changed appropriately)
#

from neuron import h
from cells.L5_pyramidal import L5Pyr
from cells.L2_pyramidal import L2Pyr
from cells.basket import Basket

# create Network class
class Network():
    def __init__(self):
        # allocate namespace for lists containing all cells in network
        self.cells_L5Pyr = []
        self.cells_L5Basket = []
        self.cells_L2Pyr = []
        self.cells_L2Basket = []

        # master connect list for all synapses
        self.nc_list = []

        self.create_cells()
        self.connect()

    def create_cells(self):
        self.cells_L5Pyr.append(L5Pyr())
        # for i in range(0, N_cells):
        #     self.cells_L5Pyr.append(L5Pyr())

        self.cells_L5Basket.append(Basket())
        # self.cells_L2Pyr.append(L2Pyr())
        # self.cells_L2Basket.append(Basket())

    def connect(self):
        # for now these loops ONLY work because n = 1 for both cells.
        # otherwise, list index changes as you iterate through the loop
        for cell_e in self.cells_L5Pyr:
            for cell_i in self.cells_L5Basket:
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
