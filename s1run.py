#!/usr/bin/env python
# s1run.py - primary run function for s1 project
#
# v 1.2.24a
# rev 2012-10-30 (MS: prng seed set in exec_runsim() based on rank)
# last major: (MS: Added benchmarking to exec_runsim())

import os
import shutil
import numpy as np
from mpi4py import MPI
from time import clock, time
from neuron import h as nrn
nrn.load_file("stdrun.hoc")

# Cells are defined in './cells'
from class_net import Network
import fn.fileio as fio
import fn.paramrw as paramrw
import fn.plotfn as plotfn

# params
import p_sim

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

def copy_paramfile(dsim):
    # assumes in this cwd, can use try/except in the future
    paramfile = 'p_sim.py'
    paramfile_orig = os.path.join(os.getcwd(), paramfile)
    paramfile_sim = os.path.join(dsim, paramfile)

    shutil.copyfile(paramfile_orig, paramfile_sim)

# All units for time: ms
def exec_runsim(p_all):
    # clock start time
    t0 = clock()

    # dealing with multiple params - there is a lot of overhead to this
    # read the ranges of params and make up all combinations
    # for loop that changes these params serially, with different file names and whatnot
    # serial execution of each param file, since we're already doing charity here
    # copy the param file and write the param dict to a file for that specific sim.

    pc = nrn.ParallelContext()
    rank = int(pc.id())

    # creates p_exp.sim_prefix and other param structures
    p_exp = paramrw.exp_params(p_all)

    # project directory
    dproj = '/repo/data/s1'

    # one directory for all experiments
    if rank == 0:
        ddir = fio.OutputDataPaths(dproj, p_exp.sim_prefix)
        ddir.create_dirs()

        copy_paramfile(ddir.dsim)
        # assign to param file
        # p['dir'] = ddir.dsim

    # iterate through i
    for i in range(p_exp.N_sims):
        if rank == 0:
            t1 = time()
            print "Run number:", i

        p = p_exp.return_pdict(i)

        # get all nodes to this place before continuing
        # tries to ensure we're all running the same params at the same time!
        pc.barrier()

        # global variable bs, should be node-independent
        nrn("dp_total = 0.")

        # Seed pseudorandom number generator
        np.random.seed(rank)
        # np.random.seed(0)

        # Set tstop before instantiating any classes
        nrn.tstop = p['tstop']
        nrn.dt = p['dt']
        # nrn.cvode_active(1)

        # Create network from class_net's Network class
        # Network(gridpyr_x, gridpyr_y)
        net = Network(p)

        # create prefix for files everyone knows about
        exp_prefix = p_exp.sim_prefix + '-%03d' % i

        # spike file needs to be known by all nodes
        file_spikes_tmp = fio.file_spike_tmp(dproj)

        # create rotating data files and dirs on ONE central node
        if rank == 0:
            # create file names
            file_dpl = ddir.create_filename('dipole', exp_prefix)
            file_param = ddir.create_filename('param', exp_prefix)
            file_spikes = ddir.create_filename('spikes', exp_prefix)

        # debug
        debug = 0
        if rank == 0:
            if debug:
                # net's method rec_debug(rank, gid)
                v_debug = net.rec_debug(0, 8)
                filename_debug = 'debug.dat'

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

        if rank == 0: t2 = time()
        pc.psolve(nrn.tstop)
        if rank == 0: print "\tIntegration time:", time() - t2

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

            if debug:
                with open(filename_debug, 'w+') as file_debug:
                    for i in range(int(t_vec.size())):
                        file_debug.write("%03.3f\t%5.4f\n" % (t_vec.x[i], v_debug.x[i]))

                # also create a debug plot
                pdipole(filename_debug, os.getcwd())

        # write output spikes
        # spikes_write(net, file_spikes)
        spikes_write(net, file_spikes_tmp)

        # move the spike file to the spike dir
        if rank == 0:
            shutil.move(file_spikes_tmp, file_spikes)

            print "\tRun time:", time() - t1

    if pc.nhost > 1:
        pc.runworker()
        pc.done()

        t1 = clock()
        if rank == 0:
            print "Simulation run time: %4.4f s" % (t1-t0)
            print "Plotting..."

            t3 = time()

            # is there a reason to pass nrn.tstop?
            plotfn.pall(ddir, p_exp, net.gid_dict, nrn.tstop)

            print "\tPlot time:", time() - t3 

        nrn.quit()

    else:
        # end clock time
        t1 = clock()
        print "Simulation run time: %4.4f s" % (t1-t0)

if __name__ == "__main__":
    # starting to use params
    exec_runsim(p_sim.all)
