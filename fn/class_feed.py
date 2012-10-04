# class_feed.py - establishes FeedExt(), FeedProximal() and FeedDistal()
#
# v 1.2.11
# rev 2012-10-04 (SL: ParFeedExtGauss different mu, sigma vals)
# last major: (SL: fixed sort bug for VecStim())

import numpy as np
import itertools as it

from neuron import h as nrn

# this seems wasteful but necessary
class ParFeedExtGauss():
    def __init__(self, mu, sigma):
        self.eventvec = nrn.Vector()
        self.vs = nrn.VecStim()

        # mu and sigma values come from p
        # one single value from Gaussian dist.
        # values MUST be sorted for VecStim()!
        val_gauss = np.random.normal(mu, sigma, 50)
        # val_gauss = np.random.normal(p['mu'], p['sigma'], 50)
        val_gauss.sort()

        # Convert array into nrn vector
        self.eventvec.from_python(val_gauss)

        # load eventvec into VecStim object
        self.vs.play(self.eventvec)

    # for parallel, maybe be that postsyn for this is just nil (None)
    def connect_to_target(self):
        nc = nrn.NetCon(self.vs, None)
        nc.threshold = 0

        return nc

class ParFeedExt():
    def __init__(self, net_origin, p):
        # create eventvec and VecStim objects
        self.eventvec = nrn.Vector()
        self.vs = nrn.VecStim()

        # store f_input as self variable for later use if it exists in p
        # t0 is always defined
        self.t0 = p['t0']
        self.f_input = p['f_input']

        # # if f_input is 0, then this is a one-time feed
        # if 'stim' in p.keys():
        #     # check on this feed.
        #     if p['stim'] is 'gaussian':
        #         pass

        if not self.f_input:
            # use VecStim().play() in this case
            # should write to eventvec here
            self.t_evoked = nrn.Vector([self.t0])
            self.vs.play(self.t_evoked)

        else:
            # Use create_eventvec() to create based on the frequency otherwise
            self.__create_eventvec()

    # for parallel, maybe be that postsyn for this is just nil (None)
    def connect_to_target(self):
        nc = nrn.NetCon(self.vs, None)
        nc.threshold = 0

        return nc

    # Create nrn vector with ALL stimulus times for an input type (e.g. proximal or distal) 
    # and load vector into VecStim object
    # only used in feeds
    def __create_eventvec(self):
        # array of mean stimulus times, starts at t0
        array_isi = np.arange(self.t0, nrn.tstop, 1000./self.f_input)

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
