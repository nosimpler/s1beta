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
        for cell_e in self.cell_list_e:
            for cell_i in self.cell_list_i:
                # from e to i
                nc = cell_e.connect_to_target(cell_i.syn)

                # depends on synapse being connected to (mS)
                # only for this ExpSyn and Exp2Syn cases!
                nc.weight[0] = 0.01

                # ms
                nc.delay = 1
                
                self.nc_list.append(nc)

                # from i to e
                nc = cell_i.connect_to_target(cell_e.syn)
                nc.weight[0] = 0
                # nc.weight[0] = 2e-5
                # nc.weight[0] = 0.001
                nc.delay = 1
                self.nc_list.append(nc)
