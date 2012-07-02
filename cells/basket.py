from neuron import h
from class_cell import Cell

# Inhibitory cell class
class Inh(Cell):
    def __init__(self):
        # these lengths are not correct but place fillers
        Cell.__init__(self, 10, 10)

        # excitatory synapse onto this cell
        self.syn = h.ExpSyn(self.soma(0.5))
        self.syn.e = 0

        # tau2 is decay
        self.syn.tau = 2
