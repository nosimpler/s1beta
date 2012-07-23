# class_net.py - establishes the Network class and related methods
#
# v 0.2.10
# rev 2012-07-23 (SL: clean up)
# last major: (MS: import Basket from class_cell) 

# from neuron import h as nrn
from cells.L5_pyramidal import L5Pyr
from cells.L2_pyramidal import L2Pyr
from cells.class_cell import Basket

# create Network class
class Network():
    def __init__(self):
        # allocate namespace for lists containing all cells in network
        self.cells_L5Pyr = []
        self.cells_L5Basket = []
        self.cells_L2Pyr = []
        self.cells_L2Basket = []

        self.create_cells(1, 1)
        self.net_connect()

    # Creates cells
    def create_cells(self, N_L5Pyr, N_L5Basket):
        self.cells_L5Pyr = [L5Pyr() for i in range(0, N_L5Pyr)]
        self.cells_L5Basket = [Basket() for i in range(0, N_L5Basket)]

    # Creates synaptic connections
    def net_connect(self):
        # for now these loops ONLY work because n = 1 for both cells.
        # otherwise, list index changes as you iterate through the loop
        for L5Pyr in self.cells_L5Pyr:
            for L5Basket in self.cells_L5Basket:
                # from e to i
                L5Pyr.ncto_L5Basket.append(L5Pyr.soma_to_target(0.5, L5Basket.syn_ampa))

                # depends on synapse being connected to (mS)
                # only for this ExpSyn and Exp2Syn cases!
                # delay in ms
                L5Pyr.ncto_L5Basket[0].weight[0] = 0.01
                L5Pyr.ncto_L5Basket[0].delay = 1
                
                # from i to e
                L5Basket.ncto_L5Pyr.append(L5Basket.soma_to_target(0.5, L5Pyr.syn_gabaa))
                L5Basket.ncto_L5Pyr[0].weight[0] = 0
                L5Basket.ncto_L5Pyr[0].delay = 1
