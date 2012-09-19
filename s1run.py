# s1run.py - primary run function for s1 project
#
# v 1.0.0
# rev 2012-09-11 (SL: parallelized)
# last major: (SL: changes to feed and network size)

import numpy as np
from mpi4py import MPI

# Cells are defined in './cells'
from cells.L5_pyramidal import L5Pyr
from class_net import Network
from plot.ptest import ptest
from plot.pdipole import pdipole

# Import benchmarking function
from time import clock

from neuron import h as nrn
nrn.load_file("stdrun.hoc")

# All units for time: ms
# this will end up being a function that is called by main
if __name__ == "__main__":
    # clock start time
    t0 = clock()

    pc = nrn.ParallelContext()
    rank = int(pc.id())

    # estalish TOTAL aggregate dipole over ALL cells on ONE node
    # global variable bs, should be node-independent
    nrn("dp_total = 0.")

    # Seed pseudorandom number generator
    np.random.seed(0)

    # Set tstop before instantiating any classes
    nrn.tstop = 100.
    nrn.dt = 0.05
    # nrn.cvode_active(1)

    # Create network from class_net's Network class
    # Network(gridpyr_x, gridpyr_y)
    net = Network(5, 5)

    # open main data file only on one processor
    if rank == 0:
        file_name = 'testing.dat'
        data_file = nrn.File()
        data_file.wopen(file_name)

    # these are testing outputs
    dp_prefix = 'testing-%d' % (rank)
    dp_name = dp_prefix + '.dat'
    dp_test = nrn.File()
    dp_test.wopen(dp_name)

    # runtest
    t_vec = nrn.Vector()
    t_vec.record(nrn._ref_t)

    # initialize cells to -65 mV and compile code
    # after all the NetCon delays have been specified
    dp_rec = nrn.Vector()
    dp_rec.record(nrn._ref_dp_total)

    pc.set_maxstep(10)
    nrn.finitialize(-64.7)

    # set state variables if they have been changed since nrn.finitialize
    nrn.fcurrent()
    nrn.frecord_init()

    pc.psolve(nrn.tstop)

    for i in range(int(t_vec.size())):
        dp_test.printf("%03.3f\t%5.4f\n", t_vec.x[i], dp_rec.x[i])

    dp_test.close()
    pdipole(dp_prefix)

    pc.allreduce(dp_rec, 1)

    # write time and voltage to data file only if on the first proc
    # only execute this statement on one processor
    if rank == 0:
        for i in range(int(t_vec.size())):
            data_file.printf("%03.3f\t%5.4f\n", t_vec.x[i], dp_rec.x[i])


    # close data file that's only on proc 0
    if rank == 0:
        # close the file
        data_file.close()
        pdipole('testing')

    if pc.nhost > 1:
        pc.runworker()
        pc.done()
        t1 = clock()
        if rank == 0:
            print "Simulation run time: %4.4f s" % (t1-t0)
        nrn.quit()
        # MPI.Finalize()
    else:
        # end clock time
        t1 = clock()
        print "Simulation run time: %4.4f s" % (t1-t0)
