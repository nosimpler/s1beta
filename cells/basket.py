# Basket.py - est class def for inhibitory basket cell used in all layers
#
# v. 0.1.1
# rev 2012-07-12 (expicitly set Ra and cm)
# last rev: (created)
#

from neuron import h
from class_cell import Cell

# Inhibitory cell class
class Basket(Cell):
    def __init__(self):
        # Cell.__init__(self, L, diam, cm)
        Cell.__init__(self, 39, 20, 0.85)

        # excitatory synapse onto this cell
        self.syn = h.ExpSyn(self.soma(0.5))
        self.syn.e = 0

        # tau2 is decay
        self.syn.tau = 2

    def print_params(self):
        print "Basket cell params:"
        print "Basket length:", self.soma.L
        print "Basket diam:", self.soma.diam
        print "Basket Ra:", self.soma.Ra
        print "Basket cm:", self.soma.cm
