# class_feed.py - establishes FeedExt(), ParFeedAll()
#
# v 1.7.6
# rev 2013-01-24 (SL: changed vars in _ParFeedExt_create_eventvec)
# last major: (SL: unique random seeds for each)

import numpy as np
import itertools as it

from neuron import h as nrn

class ParFeedAll():
    def __init__(self, type, celltype, p_ext, gid):
        # VecStim setup
        self.eventvec = nrn.Vector()
        self.vs = nrn.VecStim()

        # self.p_unique = p_unique[type]
        self.p_ext = p_ext
        self.celltype = celltype

        # random generator for this instance
        self.seed = self.p_ext['prng_seedcore'] + gid
        self.prng = np.random.RandomState(self.seed)

        # each of these methods creates self.eventvec for playback
        if type == 'extpois':
            self.__create_extpois()

        elif type.startswith(('evprox', 'evdist')):
            self.__create_evoked()

        elif type == 'extgauss':
            self.__create_extgauss()

        # load eventvec into VecStim object
        self.vs.play(self.eventvec)

    # based on cdf for exp wait time distribution from unif [0, 1)
    # returns in ms based on lamtha in Hz
    def __t_wait(self, lamtha):
        return -1000. * np.log(1. - self.prng.rand()) / lamtha

    # new external pois designation
    def __create_extpois(self):
        # check the t interval
        t0 = self.p_ext['t_interval'][0]
        T = self.p_ext['t_interval'][1]
        lamtha = self.p_ext[self.celltype][2]

        # mu and sigma values come from p
        # one single value from Gaussian dist.
        # values MUST be sorted for VecStim()!
        # start the initial value
        if lamtha > 0.:
            t_gen = t0 + self.__t_wait(lamtha)
            val_pois = np.array([])

            if t_gen < T:
                np.append(val_pois, t_gen)

            # vals are guaranteed to be monotonically increasing, no need to sort
            while t_gen < T:
                # so as to not clobber confusingly base off of t_gen ...
                t_gen += self.__t_wait(lamtha)
                if t_gen < T:
                    val_pois = np.append(val_pois, t_gen)

        else:
            val_pois = np.array([])

        # checks the distribution stats
        # if len(val_pois):
        #     xdiff = np.diff(val_pois/1000)
        #     print lamtha, np.mean(xdiff), np.var(xdiff), 1/lamtha**2

        # Convert array into nrn vector
        self.eventvec.from_python(val_pois)

    # mu and sigma vals come from p
    def __create_evoked(self):
        if self.celltype in self.p_ext.keys():
            # assign the params
            mu = self.p_ext['t0']
            sigma = self.p_ext[self.celltype][2]

            # if a non-zero sigma is specified
            if sigma:
                val_evoked = self.prng.normal(mu, sigma, 1)
                # val_evoked = np.random.normal(mu, sigma, 1)

            else:
                # if sigma is specified at 0
                val_evoked = np.array([mu])

            val_evoked = val_evoked[val_evoked > 0]

            # vals must be sorted
            val_evoked.sort()
            self.eventvec.from_python(val_evoked)

        else:
            # return an empty eventvec list
            self.eventvec.from_python([])

    def __create_extgauss(self):
        # assign the params
        mu = self.p_ext[self.celltype][2]
        sigma = self.p_ext[self.celltype][3]

        # mu and sigma values come from p
        # one single value from Gaussian dist.
        # values MUST be sorted for VecStim()!
        val_gauss = self.prng.normal(mu, sigma, 50)
        # val_gauss = np.random.normal(mu, sigma, 50)

        # remove non-zero values brute force-ly
        val_gauss = val_gauss[val_gauss > 0]

        # sort values - critical for nrn
        val_gauss.sort()

        # Convert array into nrn vector
        self.eventvec.from_python(val_gauss)

    # for parallel, maybe be that postsyn for this is just nil (None)
    def connect_to_target(self):
        nc = nrn.NetCon(self.vs, None)
        nc.threshold = 0

        return nc

class ParFeedExt():
    # the p here is actually p_ext elsewhere
    def __init__(self, net_origin, p, gid):
        # random generator for this instance
        self.seed = p['prng_seedcore'] + gid
        self.prng = np.random.RandomState(self.seed)

        # create eventvec and VecStim objects
        self.eventvec = nrn.Vector()
        self.vs = nrn.VecStim()

        # store f_input as self variable for later use if it exists in p
        # t0 is always defined
        self.t0 = p['t0']
        self.f_input = p['f_input']

        # Create vector of input times
        self.__create_eventvec(p)

    # for parallel, maybe be that postsyn for this is just nil (None)
    def connect_to_target(self):
        nc = nrn.NetCon(self.vs, None)
        nc.threshold = 0

        return nc

    # Create nrn vector with ALL stimulus times for an input type (e.g. proximal or distal) 
    # and load vector into VecStim object
    # only used in feeds
    def __create_eventvec(self, p):
        # If frequency is 0, create empty vector if input times
        if not self.f_input:
            t_input = []

        else:
            # array of mean stimulus times, starts at t0
            isi_array = np.arange(self.t0, p['tstop'], 1000./self.f_input)

            # array of single stimulus times -- no doublets 
            t_array = self.prng.normal(np.repeat(isi_array, 10), p['stdev'])

            # Two arrays store doublet times
            t_array_low = t_array - 5
            t_array_high = t_array + 5

            # Array with ALL stimulus times for input 
            # np.append concatenates two np arrays
            t_input = np.append(t_array_low, t_array_high)

            # brute force remove non-zero times. Might result in fewer vals than desired
            t_input = t_input[t_input > 0]
            t_input.sort()

        # Convert array into nrn vector
        self.eventvec.from_python(t_input)

        # load eventvec into VecStim object
        self.vs.play(self.eventvec)
