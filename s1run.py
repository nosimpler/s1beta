#!/usr/bin/env python
# s1run.py - primary run function for s1 project
#
# v 1.2.1
# rev 2012-09-27 (MS: dt set to 0.025ms)
# last major: (SL: writes spikes for all nodes along with gids, formalized debug)

import numpy as np
from mpi4py import MPI
from time import clock
from neuron import h as nrn
nrn.load_file("stdrun.hoc")

# Cells are defined in './cells'
from cells.L5_pyramidal import L5Pyr
from class_net import Network
from plot.ptest import ptest
from plot.pdipole import pdipole

# spike write function
def spikes_write(rank, net, filename_spikes):
    for rank in range(int(pc.nhost())):
        # guarantees node order and no competition
        pc.barrier()
        if rank == int(pc.id()):
            # net.spiketimes and net.spikegids are type nrn.Vector()
            L = int(net.spikegids.size())
            with open(filename_spikes, 'a') as file_spikes:
                for i in range(L):
                    file_spikes.write('%3.2f\t%d\n' % (net.spiketimes.x[i], net.spikegids.x[i]))

    # let all nodes iterate through loop in which only one rank writes
    pc.barrier()

# All units for time: ms
if __name__ == "__main__":
    # clock start time
    t0 = clock()

    pc = nrn.ParallelContext()
    rank = int(pc.id())

    # global variable bs, should be node-independent
    nrn("dp_total = 0.")

    # Seed pseudorandom number generator
    np.random.seed(0)

    # Set tstop before instantiating any classes
    nrn.tstop = 100.
    nrn.dt = 0.025
    # nrn.cvode_active(1)

    # Create network from class_net's Network class
    # Network(gridpyr_x, gridpyr_y)
    net = Network(1, 1)

    # file name for spikes, everyone needs to know
    filename_spikes = 'spikes.dat'

    # open main data file only on one processor
    if rank == 0:
        file_name = 'testing.dat'
        data_file = nrn.File()
        data_file.wopen(file_name)

    # runtest
    t_vec = nrn.Vector()
    t_vec.record(nrn._ref_t)

    # debug
    debug = 0
    if rank == 0:
        if debug:
            # net's method rec_debug(rank, gid)
            v_debug = net.rec_debug(0, 2)
            fileprefix_debug = 'debug'
            filename_debug = fileprefix_debug + '.dat'

    # initialize cells to -65 mV and compile code
    # after all the NetCon delays have been specified
    dp_rec = nrn.Vector()
    dp_rec.record(nrn._ref_dp_total)

    # record the spikes
    vec_spikes = nrn.Vector()
    vec_ids = nrn.Vector()

    pc.set_maxstep(10)
    nrn.finitialize(-64.7)

    # set state variables if they have been changed since nrn.finitialize
    nrn.fcurrent()
    nrn.frecord_init()

    # run the solver and combine dp_rec
    pc.psolve(nrn.tstop)
    pc.allreduce(dp_rec, 1)

    # write time and calculated dipole to data file only if on the first proc
    # only execute this statement on one processor
    if rank == 0:
        for i in range(int(t_vec.size())):
            data_file.printf("%03.3f\t%5.4f\n", t_vec.x[i], dp_rec.x[i])

        # close the file
        data_file.close()
        pdipole('testing')

        if debug:
            with open(filename_debug, 'w+') as file_debug:
                for i in range(int(t_vec.size())):
                    file_debug.write("%03.3f\t%5.4f\n" % (t_vec.x[i], v_debug.x[i]))

            # also create a debug plot
            pdipole(fileprefix_debug)

    # write output spikes
    spikes_write(rank, net, filename_spikes)

    if pc.nhost > 1:
        pc.runworker()
        pc.done()

        t1 = clock()
        if rank == 0:
            print "Simulation run time: %4.4f s" % (t1-t0)

        nrn.quit()

    else:
        # end clock time
        t1 = clock()
        print "Simulation run time: %4.4f s" % (t1-t0)
