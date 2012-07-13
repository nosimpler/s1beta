# class_net.py - establishes the Network class and related methods
#
# v 0.1.3
# rev 2012-07-13 (SL: added new netconnect lists)
# last major: (MS: Renamed cell lists, added new cells but not connected)

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
        # more likely, there will be several of these lists ...
        # for now, list for each unique connection TYPE
        # maybe in the future, list for each connection target OR source (but not both -- probably)
        self.nc_list = []
        self.nc_L5pyr_L5basket = []
        self.nc_L5basket_L5pyr = []
        # self.nc_L5pyr_L2pyr = []
        # self.nc_L2pyr_L5pyr = []
        # self.nc_L2pyr_L5basket = []
        # etc. etc.?

        self.create_cells(1, 1)
        self.connect()

    def create_cells(self, N_L5Pyr, N_L5Basket):
        self.cells_L5Pyr = [L5Pyr() for i in range(0, N_L5Pyr)]
        self.cells_L5Basket = [Basket() for i in range(0, N_L5Basket)]

        # self.cells_L2Pyr.append(L2Pyr())
        # self.cells_L2Basket.append(Basket())

    def connect(self):
        # for now these loops ONLY work because n = 1 for both cells.
        # otherwise, list index changes as you iterate through the loop
        for cell_e in self.cells_L5Pyr:
            for cell_i in self.cells_L5Basket:
                # from e to i
                self.nc_L5pyr_L5basket.append(cell_e.connect_to_target(cell_i.syn))

                # depends on synapse being connected to (mS)
                # only for this ExpSyn and Exp2Syn cases!
                self.nc_L5pyr_L5basket[0].weight[0] = 0.01

                # delay in ms
                self.nc_L5pyr_L5basket[0].delay = 1
                
                # from i to e
                self.nc_L5basket_L5pyr.append(cell_i.connect_to_target(cell_e.syn))
                # nc = cell_i.connect_to_target(cell_e.syn)
                self.nc_L5basket_L5pyr[0].weight[0] = 0
                self.nc_L5basket_L5pyr[0].delay = 1
