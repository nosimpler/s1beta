# class_net.py - establishes the Network class and related methods
#
# v 0.2.14
# rev 2012-07-26 (SL: synaptic connections in L5)
# last major: (SL: clean up)

import itertools as it
from cells.L5_pyramidal import L5Pyr
from cells.L2_pyramidal import L2Pyr
from cells.class_cell import Basket

# create Network class
class Network():
    def __init__(self):
        # allocate namespace for lists containing all cells in network
        self.cells_L2Pyr = []
        self.cells_L2Basket = []

        self.cells_L5Pyr = []
        self.cells_L5Basket = []

        self.create_cells(1, 1, 1, 1)
        self.net_connect()

    # Create cells
    def create_cells(self, N_L2Pyr, N_L2Basket, N_L5Pyr, N_L5Basket):
        self.cells_L2Pyr = [L2Pyr() for i in range(0, N_L2Pyr)]
        self.cells_L2Basket = [Basket() for i in range(0, N_L2Basket)]

        self.cells_L5Pyr = [L5Pyr() for i in range(0, N_L5Pyr)]
        self.cells_L5Basket = [Basket() for i in range(0, N_L5Basket)]

    # Create synaptic connections
    def net_connect(self):
        # 'product' returns an iterable list of tuples of all pairs of cells 
        # in these 2 lists
        # ONE LIST performs all connections between L5Pyr and L5Basket cells
        for L5Pyr, L5Basket in it.product(self.cells_L5Pyr, self.cells_L5Basket):
            # from L5Pyr to L5Basket
            L5Pyr.connect_to_L5Basket(L5Basket)
            # L5Pyr.ncto_L5Basket.append(L5Pyr.soma_to_target(0.5, L5Basket.soma_ampa))

            # from L5Basket to L5Pyr
            L5Basket.connect_to_L5Pyr(L5Pyr)
            # L5Basket.ncto_L5Pyr_gabaa.append(L5Basket.soma_to_target(0.5, L5Pyr.soma_gabaa))
            # L5Basket.ncto_L5Pyr_gabab.append(L5Basket.soma_to_target(0.5, L5Pyr.soma_gabab))

            # Properties are another story entirely! Oy.
            # depends on synapse being connected to (mS)
            # delay in ms
            # L5Pyr.ncto_L5Basket[0].weight[0] = 0.01
            # L5Pyr.ncto_L5Basket[0].delay = 1

            # L5Basket.ncto_L5Pyr_gabaa[0].weight[0] = 0.01
            # L5Basket.ncto_L5Pyr_gabaa[0].delay = 1

        # for L2Pyr, L2Basket in it.product(self.cells_L2Pyr, self.cells_L2Basket):
        # for L2Pyr, L5Basket in it.product(self.cells_L2Pyr, self.cells_L5Basket):
        # for L2Pyr, L5Pyr in it.product(self.cells_L2Pyr, self.cells_L5Pyr):
        # for L2Pyr, L2Basket in it.product(self.cells_L2Pyr, self.cells_L2Basket):
        # etc.
