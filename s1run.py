#!/usr/bin/env python
# s1run.py - primary run function for s1 project
#
# v 1.5.9
# rev 2012-12-20 (MS: execution of epscompress() is platform dependent)
# last major: (SL: cleaned up)

import os
import sys
import time
import shutil
import numpy as np
from mpi4py import MPI
from multiprocessing import Pool

try:
    import cPickle as pickle

except ImportError:
    import pickle

from neuron import h as nrn
nrn.load_file("stdrun.hoc")

# Cells are defined in './cells'
from class_net import Network
import fn.fileio as fio
import fn.paramrw as paramrw
import fn.plotfn as plotfn
import fn.spec as spec

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

def prng_in_a_pickle(filename_prng):
    pc = nrn.ParallelContext()
    for rank in range(int(pc.nhost())):
        pc.barrier()
        if rank == int(pc.id()):
            # package the rank (processor) and the rand state and dump into the thing
            data_prng = {
                'rank': rank,
                'prng_state': np.random.get_state(),
            }

            with open(filename_prng, 'ab') as f_prng:
                pickle.dump(data_prng, f_prng, protocol=pickle.HIGHEST_PROTOCOL)

    pc.barrier()

def prng_from_picklejar(filename_prng):
    pc = nrn.ParallelContext()

    l = []

    # open the prng file in read/binary mode
    with open(filename_prng, 'rb') as f_prng:
        # stop the loop when rank is the same as the id
        # while data_tmp['rank'] is not pc.id():
        while True:
            try:
                l.append(pickle.load(f_prng))
            except EOFError:
                # print "Rank not found among the saved data. Possible mismatch in number of procs used?"
                right_seed = [prng_state_data for prng_state_data in l if prng_state_data['rank'] is int(pc.id())]
                return right_seed[0]

# copies param file into root dsim directory
def copy_paramfile(dsim, f_psim):
    # assumes in this cwd, can use try/except in the future
    print os.path.join(os.getcwd(), f_psim)
    paramfile = f_psim.split("/")[-1]
    paramfile_orig = os.path.join(os.getcwd(), f_psim)
    paramfile_sim = os.path.join(dsim, paramfile)

    shutil.copyfile(paramfile_orig, paramfile_sim)

# All units for time: ms
def exec_runsim(f_psim):
    # clock start time
    t0 = time.time()

    # dealing with multiple params - there is a lot of overhead to this
    # read the ranges of params and make up all combinations
    # for loop that changes these params serially, with different file names and whatnot
    # serial execution of each param file, since we're already doing charity here
    # copy the param file and write the param dict to a file for that specific sim.

    pc = nrn.ParallelContext()
    rank = int(pc.id())

    # creates p_exp.sim_prefix and other param structures
    p_exp = paramrw.ExpParams(f_psim)

    # project directory
    dproj = '/repo/data/s1'

    # one directory for all experiments
    if rank == 0:
        ddir = fio.SimulationPaths()
        ddir.create_new_sim(dproj, p_exp.expmt_groups, p_exp.sim_prefix)
        # ddir = fio.OutputDataPaths(dproj, p_exp.expmt_groups, p_exp.sim_prefix)
        ddir.create_dirs()

        copy_paramfile(ddir.dsim, f_psim)

    # iterate through groups and through params in the group
    for expmt_group in p_exp.expmt_groups:
        if rank == 0:
            print "Experimental group: %s" % expmt_group

        for i in range(p_exp.N_sims):
            if rank == 0:
                run_start = time.time()
                # Tells run number, prints total runs
                print "Run %i of %i" % (i, p_exp.N_sims-1),

            # return the param dict for this simulation
            p = p_exp.return_pdict(expmt_group, i)

            # if N_trials is set to 0, run 1 anyway!
            if not p_exp.N_trials:
                N_trialruns = 1

            else:
                N_trialruns = p_exp.N_trials

            # iterate through trialruns
            for j in range(N_trialruns):
                # get all nodes to this place before continuing
                # tries to ensure we're all running the same params at the same time!
                pc.barrier()
                pc.gid_clear()

                # global variable bs, should be node-independent
                nrn("dp_total = 0.")

                # Seed pseudorandom number generator
                # always check to see if one was chosen first!
                if len(p_exp.prng_state):
                    # attempt to read this as a file!
                    test_data = prng_from_picklejar(p_exp.prng_state)
                    # print "%i, %i\n" % (int(pc.id()), test_data['rank'])
                    np.random.set_state(test_data['prng_state'])

                else:
                    if not p_exp.N_trials:
                        np.random.seed(rank)

                    else:
                        # if there are N_trials, then randomize the seed
                        np.random.seed()

                # Set tstop before instantiating any classes
                nrn.tstop = p['tstop']
                nrn.dt = p['dt']

                # create prefix for files everyone knows about
                exp_prefix = "%s-%03d-T%02d" % (p_exp.sim_prefix, i, j)

                # spike file needs to be known by all nodes
                file_spikes_tmp = fio.file_spike_tmp(dproj)
                file_prng_tmp = fio.file_prng_tmp(dproj)

                # write stupid prng states
                # should have happened after the seeds (which it does)
                prng_in_a_pickle(file_prng_tmp)

                # Create network from class_net's Network class
                # Network(gridpyr_x, gridpyr_y)
                net = Network(p)

                # create rotating data files and dirs on ONE central node
                if rank == 0:
                    # create file names
                    file_dpl = ddir.create_filename(expmt_group, 'rawdpl', exp_prefix)
                    file_param = ddir.create_filename(expmt_group, 'param', exp_prefix)
                    file_spikes = ddir.create_filename(expmt_group, 'rawspk', exp_prefix)
                    file_spec = ddir.create_filename(expmt_group, 'rawspec', exp_prefix)
                    file_prng = ddir.create_filename(expmt_group, 'prngstate', exp_prefix)

                    # move the prng file to the prng dir
                    shutil.move(file_prng_tmp, file_prng)

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

                pc.psolve(nrn.tstop)

                # combine dp_rec
                pc.allreduce(dp_rec, 1)

                # write time and calculated dipole to data file only if on the first proc
                # only execute this statement on one processor
                if rank == 0:
                    with open(file_dpl, 'a') as f:
                        for k in range(int(t_vec.size())):
                            f.write("%03.3f\t%5.4f\n" % (t_vec.x[k], dp_rec.x[k]))

                    # write the params, but add a trial number
                    p['Trial'] = j
                    p['exp_prefix'] = exp_prefix

                    paramrw.write(file_param, p, net.gid_dict)

                    if debug:
                        with open(filename_debug, 'w+') as file_debug:
                            for m in range(int(t_vec.size())):
                                file_debug.write("%03.3f\t%5.4f\n" % (t_vec.x[m], v_debug.x[m]))

                        # also create a debug plot
                        pdipole(filename_debug, os.getcwd())

                # write output spikes
                # spikes_write(net, file_spikes)
                spikes_write(net, file_spikes_tmp)

                # move the spike file to the spike dir
                if rank == 0:
                    shutil.move(file_spikes_tmp, file_spikes)
                    print "... finished in: %4.4f s" % (time.time() - run_start)

        # completely superficial
        if rank == 0:
            # this prints a newline without having to specify it.
            print ""

    # plot should probably be moved outside of this
    if pc.nhost > 1:
        pc.runworker()
        pc.done()

        t1 = time.time()
        if rank == 0:
            print "Simulation run time: %4.4f s" % (t1-t0)
            print "Simulation directory is: %s" % ddir.dsim
            print "Analysis ...",

            t_start_analysis = time.time()

            # run the spectral analysis and temporarily keep data in memory in spec_results
            spec_results = spec.analysis(ddir, p_exp)

            print "time: %4.4f s" % (time.time() - t_start_analysis)
            print "Plot ...",

            plot_start = time.time()

            # run plots and epscompress function
            plotfn.pall(ddir, p_exp, spec_results)

            # for each experimental group, do the relevant png/eps creation and optimization
            # for now, only perform this action on OS machines
            if sys.platform.startswith('darwin'):
                for expmt_group in ddir.expmt_groups:
                    dspk = ddir.dfig[expmt_group]['figspk']
                    dspec = ddir.dfig[expmt_group]['figspec']

                    fext_eps = '.eps'
                    fio.epscompress(dspk, fext_eps)
                    fio.epscompress(dspec, fext_eps)

            print "time: %4.4f s" % (time.time() - plot_start) 

        nrn.quit()

    else:
        # end clock time
        t1 = time.time()
        print "Simulation run time: %4.4f s" % (t1-t0)

if __name__ == "__main__":
    # reads the specified param file
    try:
        f_psim = sys.argv[1]

    except (IndexError):
        print "Usage: %s param_input" % sys.argv[0]
        sys.exit(1)

    exec_runsim(f_psim)
