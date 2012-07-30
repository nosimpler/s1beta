# class_net.py - establishes the Network class and related methods
#
# v 0.2.16
# rev 2012-07-30 (SL: automatic pos creation)
# last major: (SL: synaptic connections in L5)

import itertools as it
import numpy as np
from cells.L5_pyramidal import L5Pyr
from cells.L2_pyramidal import L2Pyr
from cells.class_cell import Basket

# create Network class
class Network():
    def __init__(self, gridpyr_x, gridpyr_y):
    # def __init__(self):
        # int variables for grid of pyramidal cells (for now in both L2 and L5)
        self.gridpyr = {'x': gridpyr_x, 'y': gridpyr_y}

        # allocate namespace for lists containing all cells in network
        self.cells_L2Pyr = []
        self.cells_L5Pyr = []

        self.N_Basket = 1
        self.cells_L2Basket = []
        self.cells_L5Basket = []

        self.create_cells()
        # self.create_cells(1, 1, 1, 1)
        self.net_connect()

    # Creates cells and grid
    def create_cells(self):
    # def create_cells(self, N_L2Pyr, N_L2Basket, N_L5Pyr, N_L5Basket):
        xrange = 100 * np.arange(self.gridpyr['x'])
        yrange = 100 * np.arange(self.gridpyr['y'])

        # create list of tuples/coords, (x, y, z)
        L5_pos = it.product(xrange, yrange, [0])
        L2_pos = it.product(xrange, yrange, [535])

        # create pyramidal cells and assign pos
        self.cells_L5Pyr = [L5Pyr(pos) for pos in L5_pos]
        self.cells_L2Pyr = [L2Pyr(pos) for pos in L2_pos]

        # create basket cells (and assign at origin for now ... )
        self.cells_L2Basket = [Basket((0,0,0)) for i in range(0, self.N_Basket)]
        self.cells_L5Basket = [Basket((0,0,0)) for i in range(0, self.N_Basket)]

        # self.cells_L2Pyr = [L2Pyr((0,0,0)) for i in range(0, N_L2Pyr)]
        # self.cells_L5Pyr = [L5Pyr((0,0,0)) for i in range(0, N_L5Pyr)]

    # Create synaptic connections
    def net_connect(self):
        # 'product' returns an iterable list of tuples of all pairs of cells 
        # in these 2 lists
        # ONE LIST performs all connections between L5Pyr and L5Basket cells
        for L5Pyr, L5Basket in it.product(self.cells_L5Pyr, self.cells_L5Basket):
            # from L5Pyr to L5Basket
            L5Pyr.connect_to_L5Basket(L5Basket)

            # from L5Basket to L5Pyr
            L5Basket.connect_to_L5Pyr(L5Pyr)

        # for L2Pyr, L2Basket in it.product(self.cells_L2Pyr, self.cells_L2Basket):
        # for L2Pyr, L5Basket in it.product(self.cells_L2Pyr, self.cells_L5Basket):
        # for L2Pyr, L5Pyr in it.product(self.cells_L2Pyr, self.cells_L5Pyr):
        # for L2Pyr, L2Basket in it.product(self.cells_L2Pyr, self.cells_L2Basket):
        # etc.
