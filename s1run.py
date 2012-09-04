# s1run.py - primary run function for s1 project
#
# v 0.4.7
# rev 2012-08-24 (SL: changes to feed and network size)
# last major: (SL: Changed plottools to plot)

import numpy as np
from mpi4py import MPI

# Cells are defined in './cells'
from cells.L5_pyramidal import L5Pyr
from class_net import Network
from fn.class_feed import FeedProximal, FeedDistal
from plot.ptest import ptest
from plot.pdipole import pdipole

# Import benchmarking function
from time import clock

from neuron import h as nrn
nrn.load_file("stdrun.hoc")

# All units for time: ms
# this will end up being a function that is called by main
if __name__ == "__main__":
    # Seed pseudorandom number generator
    np.random.seed(0)

    # Set tstop before instantiating any classes
    nrn.tstop = 800.
    nrn.dt = 0.025

    # Create network from class_net's Network class
    # Network(gridpyr_x, gridpyr_y)
    net = Network(10, 10)

    # Create feed parameters
    # p['synto_cellobj'] is a tuple of (weight, delay)
    p_feed_prox = {
        'f_input': 10.,
        'synto_L2Pyr': (4e-5, 0.),
        'synto_L5Pyr': (4e-5, 1.),
        'synto_L2Basket': (8e-5, 0.),
        'synto_L5Basket': (8e-5, 1.),
        'lamtha': 100.
    }

    # NMDA key states if distal feed synapses on NMDA receptors
    p_feed_dist = {
        'f_input': 10.,
        'synto_L2Pyr': (4e-5, 5.),
        'synto_L5Pyr': (4e-5, 5.),
        'synto_L2Basket': (4e-5, 5.),
        'lamtha': 100.,
        'NMDA': 'no'
    }

    # Create evoked response parameters
    p_evoked_prox_early = {
        'tstart': nrn.Vector([454.]),
        'synto_L2Pyr': (1e-3, 0.),
        'synto_L5Pyr': (5e-4, 1.),
        'synto_L2Basket': (2e-3, 0.),
        'synto_L5Basket': (1e-3, 1.),
        'lamtha': 3.
    }

    p_evoked_prox_late = {
        'tstart': nrn.Vector([564.]),
        'synto_L2Pyr': (6.89e-3, 0.),
        'synto_L5Pyr': (3.471e-3, 5.),
        'synto_L2Basket': (6.89e-3, 0.),
        'synto_L5Basket': (3.471e-3, 5.),
        'lamtha': 3.
    }

    p_evoked_dist = {
        'tstart': nrn.Vector([499.]),
        'synto_L2Pyr': (1.05e-3, 0.),
        'synto_L5Pyr': (1.05e-3, 0.),
        'synto_L2Basket': (5.02e-4, 0.),
        'lamtha': 3.,
        'NMDA': 'yes'
    }

    # Establish feeds
    feed_prox = FeedProximal(net, p_feed_prox)
    feed_prox.create_eventvec()

    feed_dist = FeedDistal(net, p_feed_dist)
    feed_dist.create_eventvec()

    # Establish evoked response
    # evoked_prox_early = FeedProximal(net, p_evoked_prox_early)
    # evoked_prox_early.load_eventtime()

    # evoked_dist = FeedDistal(net, p_evoked_dist)
    # evoked_dist.load_eventtime()

    # evoked_prox_late = FeedProximal(net, p_evoked_prox_late)
    # evoked_prox_late.load_eventtime()

    # name compartments internally for this function
    seg_e = net.cells_L5Pyr[0].soma(0.5)
    seg_i = net.cells_L5Basket[0].soma(0.5)

    # Create new vecs
    v_e = nrn.Vector()
    v_i = nrn.Vector()
    t_vec = nrn.Vector()

    # Set to record
    v_e.record(seg_e._ref_v)
    v_i.record(seg_i._ref_v)
    t_vec.record(nrn._ref_t)

    v_e.record(seg_e._ref_v)
    v_i.record(seg_i._ref_v)

    # open data file
    file_name = 'testing.dat'
    data_file = nrn.File()
    data_file.wopen(file_name)

    # initialize cells to -65 mV and compile code
    nrn.finitialize(-65)

    # set state variables if they have been changed since nrn.finitialize
    nrn.fcurrent()

    # nrn.cvode_active(1)

    # clock start time
    t0 = clock()

    # run the simulation
    while (nrn.t < nrn.tstop):
        # calculate dipole
        dp_total = net.dipole_net_calc()

        # write time and voltage to data file
        data_file.printf("%03.3f\t%5.4f\t%5.4f\n", nrn.t, seg_e.v, dp_total)

        # advance integration by one tstep
        nrn.fadvance()

    # end clock time
    t1 = clock()
    print "Simulation run time: %4.4f s" % (t1-t0)

    # close data file
    data_file.close()

    # create a couple of test figs
    # two ways of doing plots here
    ptest(t_vec, v_e, v_i)
    pdipole(file_name)
