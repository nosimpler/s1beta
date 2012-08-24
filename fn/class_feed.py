# class_feed.py - establishes FeedExt(), FeedProximal() and FeedDistal()
#
# v 0.4.6
# rev 2012-08-24 (SL: minor)
# last major: (MS: small optimizations)

import numpy as np
import itertools as it

from neuron import h as nrn

# General class for creating VecStim()
class FeedExt():
    # 'origin' should be a tuple (x, y, z) that defines center of network
    def __init__(self, net, p):
        # store net.orgin and net.tstop as self variables for later use
        self.origin = net.origin

        # store f_input as self variable for later use if it exists in p
        # if f_input does not exist, check for presence of tstart and store for later use
        if 'f_input' in p.keys():
            self.f_input = p['f_input']
        elif 'tstart' in p.keys():
            self.tstart = p['tstart']

        # create nrn vector for later use
        self.eventvec = nrn.Vector()

        # create VecStim object
        self.vs = nrn.VecStim()
    
    # Create nrn vector with ALL stimulus times for an input type (e.g. proximal or distal) 
    # and load vector into VecStim object
    def create_eventvec(self):
        # array of mean stimulus times, starts at 150 ms
        array_isi = np.arange(150, nrn.tstop, 1000/self.f_input)

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

        # load eventvec into VecStim object
        self.vs.play(self.eventvec)

    def load_eventtime(self):
        self.vs.play(self.tstart)

    # Connects instance of FeedExt() to postsynaptic target
    # very similar to sec_to_target() in class_cell
    def feed_to_target(self, postsyn):
        # netconobj = nrn.NetCon(VecStim object, postsynaptic cell)
        nc = nrn.NetCon(self.vs, postsyn)

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
        nc.weight[0] = A * np.exp(-(d**2.) / (lamtha**2.))

    # syn_delay() also found in Cell()
    def syn_delay(self, nc, A, d, lamtha):
        nc.delay = A / (np.exp(-(d**2.) / (lamtha**2.)))

# Defines input that might arise from L4 (origin may be thalamic)
class FeedProximal(FeedExt):
    def __init__(self, net, p):
        # self.vs and self.eventvec
        FeedExt.__init__(self, net, p)

        # Lists of connections FROM this feed TO target
        # Describes AMPA-ergic inputs to these sections on these cells!
        self.ncto_pyr_basal2_ampa = []
        self.ncto_pyr_basal3_ampa = []
        self.ncto_pyr_apicaloblique_ampa = []
        self.ncto_basket_ampa = []

        # Creates NetCon() objects and adds to master connect lists
        for L2Pyr in net.cells_L2Pyr:
            self.__connect_to_pyr(L2Pyr, p['synto_L2Pyr'][0], p['synto_L2Pyr'][1], p['lamtha'])

        # Continues appending to the master connect lists
        for L5Pyr in net.cells_L5Pyr:
            self.__connect_to_pyr(L5Pyr, p['synto_L5Pyr'][0], p['synto_L5Pyr'][1], p['lamtha'])

        # Connect feed to inhibitory cells
        for L2Basket in net.cells_L2Basket:
            self.__connect_to_basket(L2Basket, p['synto_L2Basket'][0], p['synto_L2Basket'][1], p['lamtha'])

        # Continues appending
        for L5Basket in net.cells_L5Basket:
            self.__connect_to_basket(L5Basket, p['synto_L5Basket'][0], p['synto_L5Basket'][1], p['lamtha'])

    # General function to L2 and L5 pyramidals
    # Note: functions depend on synapse naming being equivalent in each class!
    def __connect_to_pyr(self, Pyr, weight, delay, lamtha):
        # AMPA connections
        self.ncto_pyr_basal2_ampa.append(self.feed_to_target(Pyr.basal2_ampa))
        self.ncto_pyr_basal3_ampa.append(self.feed_to_target(Pyr.basal3_ampa))
        self.ncto_pyr_apicaloblique_ampa.append(self.feed_to_target(Pyr.apicaloblique_ampa))

        # Calculate distance using distance from FeedExt()
        d = self.distance(Pyr)

        # Set weights using syn_weight() from FeedExt()
        self.syn_weight(self.ncto_pyr_basal2_ampa[-1], weight, d, lamtha)
        self.syn_weight(self.ncto_pyr_basal3_ampa[-1], weight, d, lamtha)
        self.syn_weight(self.ncto_pyr_apicaloblique_ampa[-1], weight, d, lamtha)

        # Set delays using syn_delay() from FeedExt()
        self.syn_delay(self.ncto_pyr_basal2_ampa[-1], delay, d, lamtha)
        self.syn_delay(self.ncto_pyr_basal3_ampa[-1], delay, d, lamtha)
        self.syn_delay(self.ncto_pyr_apicaloblique_ampa[-1], delay, d, lamtha)

    # routine to connect to basket cell
    def __connect_to_basket(self, Basket, weight, delay, lamtha):
        self.ncto_basket_ampa.append(self.feed_to_target(Basket.soma_ampa))

        # set distance using distance from FeedExt()
        d = self.distance(Basket)

        # Set weight using syn_weight() from FeedExt()
        self.syn_weight(self.ncto_basket_ampa[-1], weight, d, lamtha)

        # Set delay using syn_delay from FeedExt()
        self.syn_delay(self.ncto_basket_ampa[-1], delay, d, lamtha)

# Defines superficial input (possibly thalamic)
class FeedDistal(FeedExt):
    def __init__(self, net, p):
        FeedExt.__init__(self, net, p)

        # Lists of connections FROM this feed TO target
        self.ncto_pyr_apicaltuft_ampa = []
        self.ncto_basket_ampa = []

        self.ncto_pyr_apicaltuft_nmda = []
        self.ncto_basket_nmda = []

        # Connect_to_pyr() is defined uniquely in this class
        # Self.connect_to_pyr(CellObj, delay)
        # Connect feed to pyramidal cells
        for L2Pyr in net.cells_L2Pyr:
            self.__connect_to_pyr_ampa(L2Pyr, p['synto_L2Pyr'][0], p['synto_L2Pyr'][1], p['lamtha'])

            if p['NMDA'] == 'yes':
                self.__connect_to_pyr_nmda(L2Pyr, p['synto_L2Pyr'][0], p['synto_L2Pyr'][1], p['lamtha'])

        for L5Pyr in net.cells_L5Pyr:
            self.__connect_to_pyr_ampa(L5Pyr, p['synto_L5Pyr'][0], p['synto_L5Pyr'][1], p['lamtha'])

            if p['NMDA'] == 'yes':
                self.__connect_to_pyr_nmda(L5Pyr, p['synto_L5Pyr'][0], p['synto_L5Pyr'][1], p['lamtha'])

        # Connect feed to inhibitory cells
        for L2Basket in net.cells_L2Basket:
            self.__connect_to_basket_ampa(L2Basket, p['synto_L2Basket'][0], p['synto_L2Basket'][1], p['lamtha'])

            if p['NMDA'] == 'yes':
                self.__connect_to_basket_nmda(L2Basket, p['synto_L2Basket'][0], p['synto_L2Basket'][1], p['lamtha'])

    # Distal connections are different than proximal!
    def __connect_to_pyr_ampa(self, Pyr, weight, delay, lamtha):
        # AMPA connections
        self.ncto_pyr_apicaltuft_ampa.append(self.feed_to_target(Pyr.apicaltuft_ampa))

        # Calculate distance using distance from FeedExt()
        d = self.distance(Pyr)

        # Set weights using syn_weight from FeedExt()
        self.syn_weight(self.ncto_pyr_apicaltuft_ampa[-1], weight, d, lamtha)

        # Set delays using syn_delay from FeedExt()
        self.syn_delay(self.ncto_pyr_apicaltuft_ampa[-1], delay, d, lamtha)

    def __connect_to_pyr_nmda(self, Pyr, weight, delay, lamtha):
        # AMPA connections
        self.ncto_pyr_apicaltuft_nmda.append(self.feed_to_target(Pyr.apicaltuft_nmda))

        # Calculate distance using distance from FeedExt()
        d = self.distance(Pyr)

        # Set weights using syn_weight from FeedExt()
        self.syn_weight(self.ncto_pyr_apicaltuft_nmda[-1], weight, d, lamtha)

        # Set delays using syn_delay from FeedExt()
        self.syn_delay(self.ncto_pyr_apicaltuft_nmda[-1], delay, d, lamtha)

    def __connect_to_basket_ampa(self, Basket, weight, delay, lamtha):
        self.ncto_basket_ampa.append(self.feed_to_target(Basket.soma_ampa))

        # set distance using distance from FeedExt()
        d = self.distance(Basket)

        # set weight using syn_weight from FeedExt()
        self.syn_weight(self.ncto_basket_ampa[-1], weight, d, lamtha)

        # set delay using syn_delay from FeedExt()
        self.syn_delay(self.ncto_basket_ampa[-1], delay, d, lamtha)

    def __connect_to_basket_nmda(self, Basket, weight, delay, lamtha):
        self.ncto_basket_nmda.append(self.feed_to_target(Basket.soma_nmda))

        # set distance using distance from FeedExt()
        d = self.distance(Basket)

        # set weight using syn_weight from FeedExt()
        self.syn_weight(self.ncto_basket_nmda[-1], weight, d, lamtha)

        # set delay using syn_delay from FeedExt()
        self.syn_delay(self.ncto_basket_nmda[-1], delay, d, lamtha)
