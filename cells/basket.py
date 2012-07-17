# Basket.py - est class def for inhibitory basket cell used in all layers
#
# v. 0.2.2
# rev 2012-07-17 (SL: using nrn instead of h)
# last rev: (SL: Changed synapse functions)

# from neuron import h as nrn
from class_cell import Cell

# Inhibitory cell class
class Basket(Cell):
    def __init__(self):
        # Cell.__init__(self, L, diam, cm)
        Cell.__init__(self, 39, 20, 0.85)

        # excitatory synapse onto this cell
        self.syn_ampa_create(self.soma(0.5))
        # # or something in the future like syn_ampa, etc.
        # self.syn_L5pyr = h.ExpSyn(self.soma(0.5))
        # self.syn_L5pyr.e = 0

        # # tau is decay
        # self.syn_L5pyr.tau = 2

    def print_params(self):
        print "Basket cell params:"
        print "Basket length:", self.soma.L
        print "Basket diam:", self.soma.diam
        print "Basket Ra:", self.soma.Ra
        print "Basket cm:", self.soma.cm
