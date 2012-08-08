# L5_basket.py - establish class def for layer 5 basket cells
#
# v 0.2.30
# rev 2012-08-08 (SL: changed variable name)
# last rev: (SL: Added connections to L5Basket)

from neuron import h as nrn
from class_cell import Basket

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted

class L5Basket(Basket):
    def __init__(self, pos):
        # Pyr.__init__(self, pos, L, diam, Ra, cm)
        Basket.__init__(self, pos, 'L5Basket')

        # Create lists of connections FROM this cell TO target
        self.ncto_L5Pyr_gabaa = []
        self.ncto_L5Pyr_gabab = []
        self.ncto_L5Basket = []

    # connects both the GABAa and GABAb synapses to L5
    def connect_to_L5Pyr(self, L5Pyr):
        # add ncs to list using sec_to_target() in Cell()
        self.ncto_L5Pyr_gabaa.append(self.sec_to_target(self.soma, 0.5, L5Pyr.soma_gabaa))
        self.ncto_L5Pyr_gabab.append(self.sec_to_target(self.soma, 0.5, L5Pyr.soma_gabab))

        # get distance and calculate weight
        d = self.distance(L5Pyr)
        lamtha = 70.

        # set the weights
        self.syn_weight(self.ncto_L5Pyr_gabaa[-1], 0.025, d, lamtha)
        self.syn_weight(self.ncto_L5Pyr_gabab[-1], 0.025, d, lamtha)

        # delay in ms
        self.syn_delay(self.ncto_L5Pyr_gabaa[-1], 1, d, lamtha)
        self.syn_delay(self.ncto_L5Pyr_gabab[-1], 1, d, lamtha)

    # connects L5Basket to other L5Baskets
    def connect_to_L5Basket(self, L5Basket_post):
        self.ncto_L5Basket.append(self.sec_to_target(self.soma, 0.5, L5Basket_post.soma_gabaa))

        d = self.distance(L5Basket_post)
        lamtha = 20.

        # set the weights
        self.syn_weight(self.ncto_L5Basket[-1], 0.02, d, lamtha)

        # delay in ms
        self.syn_delay(self.ncto_L5Basket[-1], 1, d, lamtha)
