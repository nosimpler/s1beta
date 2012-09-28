#!/usr/bin/env python
# s1run.py - primary run function for s1 project
#
# v 1.2.0
# rev 2012-09-27 (SL: Major reorganization started)
# last major: (SL: handles directories and file creation)

import os
import numpy as np
from mpi4py import MPI
from time import clock
from neuron import h as nrn
nrn.load_file("stdrun.hoc")

# Cells are defined in './cells'
from cells.L5_pyramidal import L5Pyr
from class_net import Network
import fn.fileio as fio
import fn.paramrw as paramrw
from plot.ptest import ptest
from plot.pdipole import pdipole

# spike write function
def spikes_write(net, filename_spikes):
    pc = nrn.ParallelContext()

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
def exec_runsim(p):
    # clock start time
    t0 = clock()

    pc = nrn.ParallelContext()
    rank = int(pc.id())

    # global variable bs, should be node-independent
    nrn("dp_total = 0.")

    # Seed pseudorandom number generator
    np.random.seed(0)

    # Set tstop before instantiating any classes
    nrn.tstop = p['tstop']
    nrn.dt = p['dt']
    # nrn.cvode_active(1)

    # Create network from class_net's Network class
    # Network(gridpyr_x, gridpyr_y)
    net = Network(p['N_pyr_x'], p['N_pyr_y'])

    # create temporary spike file that everyone knows about
    dproj = '/repo/data/s1'
    filename_spikes = fio.file_spike_tmp(dproj)

    # create rotating data files and dirs on ONE central node
    if rank == 0:
        sim_prefix = 'test'
        ddir = fio.OutputDataPaths(dproj, sim_prefix)
        ddir.create_dirs()

        # assign to param file
        p['dir'] = ddir.dsim

        # create file names
        file_dpl = ddir.create_filename('dipole', sim_prefix)
        file_param = ddir.create_filename('param', sim_prefix)

    # debug
    debug = 0
    if rank == 0:
        if debug:
            # net's method rec_debug(rank, gid)
            v_debug = net.rec_debug(0, 8)
            fileprefix_debug = 'debug'
            filename_debug = fileprefix_debug + '.dat'

    # set t vec to record
    t_vec = nrn.Vector()
    t_vec.record(nrn._ref_t)

    # initialize cells to -65 mV and compile code
    # after all the NetCon delays have been specified
    dp_rec = nrn.Vector()
    dp_rec.record(nrn._ref_dp_total)

    # sets the default max solver step in ms (purposefully large)
    pc.set_maxstep(10)

    # set state variables if they have been changed since nrn.finitialize
    # and run the solver
    nrn.finitialize(-64.7)
    nrn.fcurrent()
    nrn.frecord_init()
    pc.psolve(nrn.tstop)

    # combine dp_rec
    pc.allreduce(dp_rec, 1)

    # write time and calculated dipole to data file only if on the first proc
    # only execute this statement on one processor
    if rank == 0:
        with open(file_dpl, 'a') as f:
            for i in range(int(t_vec.size())):
                f.write("%03.3f\t%5.4f\n" % (t_vec.x[i], dp_rec.x[i]))

        # write the gid list ...
        paramrw.write(file_param, p, net.p_ext, net.gid_dict)

        # all fig stuff needs to be moved
        dfig = ddir.fileinfo['fig'][1]
        dpl_list = fio.file_match(ddir.fileinfo, 'dipole')
        for file_dpl in dpl_list:
            pdipole(file_dpl, dfig)

        if debug:
            with open(filename_debug, 'w+') as file_debug:
                for i in range(int(t_vec.size())):
                    file_debug.write("%03.3f\t%5.4f\n" % (t_vec.x[i], v_debug.x[i]))

            # also create a debug plot
            pdipole(filename_debug, os.getcwd())

    # write output spikes
    spikes_write(net, filename_spikes)

    # move the spike file to the spike dir
    if rank == 0:
        ddir.move_spk(filename_spikes)

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

if __name__ == "__main__":
    # starting to use params
    p = {
        'N_pyr_x': 2,
        'N_pyr_y': 2,
        'tstop': 100.,
        'dt': 0.025
    }

    exec_runsim(p)
