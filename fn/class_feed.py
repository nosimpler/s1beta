# class_feed.py - establishes FeedExt(), FeedProximal() and FeedDistal()
#
# v 0.3.0
# rev 2012-08-08 (MS/SL: created)
# last major:

import numpy as np
import itertools as it

from neuron import h as nrn
from cells.L5_pyramidal import L5Pyr
from cells.L2_pyramidal import L2Pyr
from cells.L5_basket import L5Basket
from cells.L2_basket import L2Basket

# General class for creating VecStim()
class FeedExt():
    # 'origin' should be a tuple (x, y, z) that defines center of network
    def __init__(self, p_feed):
        # not happy with this necessarily, good enough for now (SL)
        self.origin = p_feed['origin']
        self.f_input = p_feed['f_input']
        self.tstop = p_feed['tstop']

        # create nrn vector for later use
        self.eventvec = nrn.Vector()

        # create VecStim object
        self.vs = nrn.VecStim()
    
        # create eventvec that contains times of all stimuli
        # writes self.eventvec
        self.create_eventvec()

        # load eventvec into VecStim object
        self.vs.play(self.eventvec)

    # Create nrn vector with ALL stimulus times for an input type (e.g. proximal or distal).  
    def create_eventvec(self):
        # array of mean stimulus times, starts at 150 ms
        array_isi = np.arange(150, self.tstop, 1000/self.f_input)

        # array of single stimulus times -- no doublets 
        array_times = np.random.normal(np.repeat(array_isi, 10), 20)

        # Two arrays store doublet times
        array_times_low = array_times - 5
        array_times_high = array_times + 5

        # Array with ALL stimulus times for input 
        # np.append concatenates two np arrays
        input_times = np.append(array_times_low, array_times_high)
        input_times.sort()

        # Convert array into nrn vector
        self.eventvec.from_python(input_times)

    # Connects instance of FeedExt() to postsynaptic target
    # very similar to sec_to_target() in class_cell
    def feed_to_target(self, postsyn):
        # netconobj = nrn.NetCon(VecStim object, postsynaptic cell)
        nc = nrn.NetCon(self.vs, postsyn)

        # from 2009 code. All thresholds set for ext stimuli are 0.
        # self.nc.threshold = 0

        # return nc object
        return nc

    # Effectively the same distance function found in Cell()
    def distance(self, cell_receiving):
        dx = abs(self.origin[0] - cell_receiving.pos[0])
        dy = abs(self.origin[1] - cell_receiving.pos[1])
        dz = abs(self.origin[2] - cell_receiving.pos[2])

        return np.sqrt(dx**2 + dy**2)

    # syn_weight() also found in Cell()
    def syn_weight(self, nc, A, d, lamtha):
        nc.weight[0] = A * np.exp(-(d**2) / (lamtha**2))

    # syn_delay() also found in Cell()
    def syn_delay(self, nc, A, d, lamtha):
        nc.delay = A / (np.exp(-(d**2) / (lamtha**2)))

# Defines input that might arise from L4 (origin may be thalamic)
class FeedProximal(FeedExt):
    def __init__(self, net, p_feed):
        # self.vs and self.eventvec
        FeedExt.__init__(self, p_feed)

        # Lists of connections FROM this feed TO target
        # Describes AMPA-ergic inputs to these sections on these cells!
        self.ncto_pyr_basal2_ampa = []
        self.ncto_pyr_basal3_ampa = []
        self.ncto_pyr_apicaloblique_ampa = []
        self.ncto_basket_ampa = []

        # Creates NetCon() objects and adds to master connect lists
        for L2Pyr in net.cells_L2Pyr:
            self.connect_to_pyr(L2Pyr, 0.)

        # Continues appending to the master connect lists
        for L5Pyr in net.cells_L5Pyr:
            self.connect_to_pyr(L5Pyr, 1.)

        # Connect feed to inhibitory cells
        for L2Basket in net.cells_L2Basket:
            self.connect_to_basket(L2Basket, 0.)

        # Continues appending
        for L5Basket in net.cells_L5Basket:
            self.connect_to_basket(L5Basket, 1.)

    # General function to L2 and L5 pyramidals
    # Note: functions depend on synapse naming being equivalent in each class!
    def connect_to_pyr(self, Pyr, delay):
        # AMPA connections
        self.ncto_pyr_basal2_ampa.append(self.feed_to_target(Pyr.basal2_ampa))
        self.ncto_pyr_basal3_ampa.append(self.feed_to_target(Pyr.basal3_ampa))
        self.ncto_pyr_apicaloblique_ampa.append(self.feed_to_target(Pyr.apicaloblique_ampa))

        # Calculate distance using distance from FeedExt()
        # Not sure if this works (but I have a hunch that it does)...
        d = self.distance(Pyr)
        weight  = 4e-5
        lamtha = 100.

        # Set weights using syn_weight() from FeedExt()
        self.syn_weight(self.ncto_pyr_basal2_ampa[-1], weight, d, lamtha)
        self.syn_weight(self.ncto_pyr_basal3_ampa[-1], weight, d, lamtha)
        self.syn_weight(self.ncto_pyr_apicaloblique_ampa[-1], weight, d, lamtha)

        # Set delays using syn_delay() from FeedExt()
        self.syn_delay(self.ncto_pyr_basal2_ampa[-1], delay, d, lamtha)
        self.syn_delay(self.ncto_pyr_basal2_ampa[-1], delay, d, lamtha)
        self.syn_delay(self.ncto_pyr_apicaloblique_ampa[-1], delay, d, lamtha)

    def connect_to_basket(self, Basket, delay):
        self.ncto_basket_ampa.append(self.feed_to_target(Basket.soma_ampa))

        # set distance using distance from FeedExt()
        d = self.distance(Basket)
        weight = 8e-5
        lamtha = 100.

        # Set weight using syn_weight() from FeedExt()
        self.syn_weight(self.ncto_basket_ampa[-1], weight, d, lamtha)

        # Set delay using syn_delay from FeedExt()
        self.syn_delay(self.ncto_basket_ampa[-1], delay, d, lamtha)

# Defines superficial input (possibly thalamic)
class FeedDistal(FeedExt):
    def __init__(self, net, p_feed):
        FeedExt.__init__(self, p_feed)

        # Lists of connections FROM this feed TO target
        self.ncto_pyr_apicaltuft_ampa = []
        self.ncto_basket_ampa = []

        # Connect_to_pyr() is defined uniquely in this class
        # Self.connect_to_pyr(CellObj, delay)
        # Connect feed to pyramidal cells
        for L2Pyr in net.cells_L2Pyr:
            self.connect_to_pyr(L2Pyr, 5.)

        for L5Pyr in net.cells_L5Pyr:
            self.connect_to_pyr(L5Pyr, 5.)

        # Connect feed to inhibitory cells
        for L2Basket in net.cells_L2Basket:
            self.connect_to_basket(L2Basket, 5.)

    # Distal connections are different than proximal!
    def connect_to_pyr(self, Pyr, delay):
        # AMPA connections
        self.ncto_pyr_apicaltuft_ampa.append(self.feed_to_target(Pyr.apicaltuft_ampa))

        # Calculate distance using distance from FeedExt()
        d = self.distance(Pyr)
        weight = 4e-5
        lamtha = 100.

        # Set weights using syn_weight from FeedExt()
        self.syn_weight(self.ncto_pyr_apicaltuft_ampa[-1], weight, d, lamtha)

        # Set delays using syn_delay from FeedExt()
        self.syn_delay(self.ncto_pyr_apicaltuft_ampa[-1], delay, d, lamtha)

    def connect_to_basket(self, Basket, delay):
        self.ncto_basket_ampa.append(self.feed_to_target(Basket.soma_ampa))

        # set distance using distance from FeedExt()
        d = self.distance(Basket)
        weight = 4e-5
        lamtha = 100

        # set weight using syn_weight from FeedExt()
        self.syn_weight(self.ncto_basket_ampa[-1], weight, d, lamtha)

        # set delay using syn_delay from FeedExt()
        self.syn_delay(self.ncto_basket_ampa[-1], delay, d, lamtha)

# if __name__ == '__main__':
#     p_input = {'f_input': 10,
#                'tstop': 100,
#                'origin': (4, 4, 0)
#     }
# 
#     feed_prox = FeedProximal(net, p_input)
#     feed_dist = FeedDistal(net, p_input)
