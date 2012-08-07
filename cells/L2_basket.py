# L2_basket.py - establish class def for layer 2 basket cells
#
# v 0.2.25
# rev 2012-08-07 (SL: Added connect_to_L2Basket)
# last rev: (SL: created from Basket())

from neuron import h as nrn
from class_cell import Basket

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted

class L2Basket(Basket):
    def __init__(self, pos):
        # Pyr.__init__(self, pos, L, diam, Ra, cm)
        Basket.__init__(self, pos, 'L2Basket')

        # Create lists of connections FROM this cell TO target
        self.ncto_L2Basket = []
        self.ncto_L2Pyr_gabaa = []
        self.ncto_L2Pyr_gabab = []
        self.ncto_L5Pyr_apicaltuft_gabaa = []

    # connects both the GABAa and GABAb synapses to L2
    # this is purposefully redundant with above for now until differences are known
    def connect_to_L2Pyr(self, L2Pyr):
        # add ncs to list using sec_to_target() in Cell()
        self.ncto_L2Pyr_gabaa.append(self.sec_to_target(self.soma, 0.5, L2Pyr.soma_gabaa))
        self.ncto_L2Pyr_gabab.append(self.sec_to_target(self.soma, 0.5, L2Pyr.soma_gabab))

        # get distance and calculate weight
        d = self.distance(L2Pyr)
        tau = 50.

        # set the weights
        self.syn_weight(self.ncto_L2Pyr_gabaa[-1], 0.05, d, tau)
        self.syn_weight(self.ncto_L2Pyr_gabab[-1], 0.05, d, tau)

        # delay in ms
        self.syn_delay(self.ncto_L2Pyr_gabaa[-1], 1, d, tau)
        self.syn_delay(self.ncto_L2Pyr_gabab[-1], 1, d, tau)

    # connects L2Basket to L5Pyr
    def connect_to_L5Pyr(self, L5Pyr):
        # add ncs to list using sec_to_target() in Cell()
        self.ncto_L5Pyr_apicaltuft_gabaa.append(self.sec_to_target(self.soma, 0.5, L5Pyr.apicaltuft_gabaa))

        # get distance and calculate weight
        d = self.distance(L5Pyr)
        tau = 50.

        # set the weights
        self.syn_weight(self.ncto_L5Pyr_apicaltuft_gabaa[-1], 1e-3, d, tau)

        # delay in ms
        self.syn_delay(self.ncto_L5Pyr_apicaltuft_gabaa[-1], 1, d, tau)

    # connects L2Basket to other L2Baskets
    def connect_to_L2Basket(self, L2Basket_post):
        self.ncto_L2Basket.append(self.sec_to_target(self.soma, 0.5, L2Basket_post.soma_gabaa))

        d = self.distance(L2Basket_post)
        tau = 20.

        # set the weights
        self.syn_weight(self.ncto_L2Basket[-1], 0.02, d, tau)

        # delay in ms
        self.syn_delay(self.ncto_L2Basket[-1], 1, d, tau)
