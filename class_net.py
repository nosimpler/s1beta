# class_net.py - establishes the Network class and related methods
#
# v 0.2.17
# rev 2012-07-30 (SL: basket cell grid in place)
# last major: (SL: automatic pos creation)

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

        # zdiff is expressed as a positive DEPTH of L5 relative to L2
        # this is a deviation from the original, where L5 was defined at 0
        # this should not change interlaminar weight/delay calculations
        self.zdiff = 535

        # allocate namespace for lists containing all cells in network
        self.cells_L2Pyr = []
        self.cells_L5Pyr = []

        # self.N_Basket = 1
        self.cells_L2Basket = []
        self.cells_L5Basket = []

        # create cells
        self.create_cells_pyr()
        self.create_cells_basket()
        # self.create_cells(1, 1, 1, 1)

        self.net_connect()

    # Creates cells and grid
    def create_cells_pyr(self):
    # def create_cells(self, N_L2Pyr, N_L2Basket, N_L5Pyr, N_L5Basket):
        xrange = 100 * np.arange(self.gridpyr['x'])
        yrange = 100 * np.arange(self.gridpyr['y'])

        # create list of tuples/coords, (x, y, z)
        L2_pyr_pos = it.product(xrange, yrange, [0])
        L5_pyr_pos = it.product(xrange, yrange, [self.zdiff])

        # create pyramidal cells and assign pos
        self.cells_L2Pyr = [L2Pyr(pos) for pos in L2_pyr_pos]
        self.cells_L5Pyr = [L5Pyr(pos) for pos in L5_pyr_pos]

    def create_cells_basket(self):
        # define relevant x spacings for basket cells
        xzero = 100 * np.arange(0, self.gridpyr['x'], 3)
        xone = 100 * np.arange(1, self.gridpyr['x'], 3)

        # split even and odd y vals
        yeven = 100 * np.arange(0, self.gridpyr['y'], 2)
        yodd = 100 * np.arange(1, self.gridpyr['y'], 2)

        # create general list of x,y coords and sort it
        coords = [pos for pos in it.product(xzero, yeven)] + [pos for pos in it.product(xone, yodd)]
        coords_sorted = sorted(coords, key=lambda pos: pos[1])

        # append the z value for position for L2 and L5
        L2_basket_pos = [pos_xy + (self.zdiff,) for pos_xy in coords_sorted]
        L5_basket_pos = [pos_xy + (0,) for pos_xy in coords_sorted]

        # create basket cells (and assign at origin for now ... )
        self.cells_L2Basket = [Basket(pos) for pos in L2_basket_pos]
        self.cells_L5Basket = [Basket(pos) for pos in L5_basket_pos]

        # self.cells_L2Basket = [Basket((0,0,0)) for i in range(0, self.N_Basket)]
        # self.cells_L5Basket = [Basket((0,0,0)) for i in range(0, self.N_Basket)]

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
