# class_net.py - establishes the Network class and related methods
#
# v 0.4.3
# rev 2012-08-23 (MS: remove self.tstop)
# last major: (MS/SL: set origin for feed)

import itertools as it
import numpy as np

from neuron import h as nrn
from cells.L5_pyramidal import L5Pyr
from cells.L2_pyramidal import L2Pyr
from cells.L2_basket import L2Basket
from cells.L5_basket import L5Basket

# create Network class
class Network():
    def __init__(self, gridpyr_x, gridpyr_y):
    # def __init__(self):
        # Store nrn.tstop as variable in Network()
        # Assumes nrn.tstop set in s1run.py prior to instantiation of Network()
        # self.tstop = nrn.tstop

        # int variables for grid of pyramidal cells (for now in both L2 and L5)
        self.gridpyr = {'x': gridpyr_x, 'y': gridpyr_y}

        # zdiff is expressed as a positive DEPTH of L5 relative to L2
        # this is a deviation from the original, where L5 was defined at 0
        # this should not change interlaminar weight/delay calculations
        self.zdiff = 1307.4 

        # allocate namespace for lists containing all cells in network
        self.cells_L2Pyr = []
        self.cells_L5Pyr = []

        # self.N_Basket = 1
        self.cells_L2Basket = []
        self.cells_L5Basket = []

        # create cells (and create self.origin in create_cells_pyr())
        self.create_cells_pyr()
        self.create_cells_basket()

        # Connect the network
        self.net_connect()

    # Creates cells and grid
    # pyr grid is the immutable grid, so we will also calculate origin here
    def create_cells_pyr(self):
        xrange = np.arange(self.gridpyr['x'])
        yrange = np.arange(self.gridpyr['y'])

        # create list of tuples/coords, (x, y, z)
        L2_pyr_pos = it.product(xrange, yrange, [0])
        L5_pyr_pos = it.product(xrange, yrange, [self.zdiff])

        # create pyramidal cells and assign pos
        self.cells_L2Pyr = [L2Pyr(pos) for pos in L2_pyr_pos]
        self.cells_L5Pyr = [L5Pyr(pos) for pos in L5_pyr_pos]

        # these must be ints!
        origin_x = xrange[(len(xrange)-1)/2]
        origin_y = yrange[(len(yrange)-1)/2]
        origin_z = np.floor(self.zdiff/2)
        self.origin = (origin_x, origin_y, origin_z)

    def create_cells_basket(self):
        # define relevant x spacings for basket cells
        xzero = np.arange(0, self.gridpyr['x'], 3)
        xone = np.arange(1, self.gridpyr['x'], 3)

        # split even and odd y vals
        yeven = np.arange(0, self.gridpyr['y'], 2)
        yodd = np.arange(1, self.gridpyr['y'], 2)

        # create general list of x,y coords and sort it
        coords = [pos for pos in it.product(xzero, yeven)] + [pos for pos in it.product(xone, yodd)]
        coords_sorted = sorted(coords, key=lambda pos: pos[1])

        # append the z value for position for L2 and L5
        L2_basket_pos = [pos_xy + (0,) for pos_xy in coords_sorted]
        L5_basket_pos = [pos_xy + (self.zdiff,) for pos_xy in coords_sorted]

        # create basket cells
        self.cells_L2Basket = [L2Basket(pos) for pos in L2_basket_pos]
        self.cells_L5Basket = [L5Basket(pos) for pos in L5_basket_pos]

    # Create synaptic connections
    def net_connect(self):
        # 'product' returns an iterable list of tuples of all pairs of cells 
        # in these 2 lists
        # ONE LIST performs all connections between L5Pyr and L5Basket cells
        # FROM object cell TO connect_to cell
        for L5Pyr, L5Basket in it.product(self.cells_L5Pyr, self.cells_L5Basket):
            L5Pyr.connect_to_L5Basket(L5Basket)
            L5Basket.connect_to_L5Pyr(L5Pyr)

        for L2Pyr, L2Basket in it.product(self.cells_L2Pyr, self.cells_L2Basket):
            L2Pyr.connect_to_L2Basket(L2Basket)
            L2Basket.connect_to_L2Pyr(L2Pyr)

        for L2Pyr, L5Basket in it.product(self.cells_L2Pyr, self.cells_L5Basket):
            L2Pyr.connect_to_L5Basket(L5Basket)

        for L5Pyr, L2Basket in it.product(self.cells_L5Pyr, self.cells_L2Basket):
            L2Basket.connect_to_L5Pyr(L5Pyr)

        for L2Pyr, L5Pyr in it.product(self.cells_L2Pyr, self.cells_L5Pyr):
            L2Pyr.connect_to_L5Pyr(L5Pyr)

        for L2Basket_pre, L2Basket_post in it.product(self.cells_L2Basket, self.cells_L2Basket):
            L2Basket_pre.connect_to_L2Basket(L2Basket_post)

        for L5Basket_pre, L5Basket_post in it.product(self.cells_L5Basket, self.cells_L5Basket):
            L5Basket_pre.connect_to_L5Basket(L5Basket_post)

        for L5Pyr_pre, L5Pyr_post in it.product(self.cells_L5Pyr, self.cells_L5Pyr):
            L5Pyr_pre.connect_to_L5Pyr(L5Pyr_post)

        for L2Pyr_pre, L2Pyr_post in it.product(self.cells_L2Pyr, self.cells_L2Pyr):
            L2Pyr_pre.connect_to_L2Pyr(L2Pyr_post)
