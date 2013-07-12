# clidefs.py - these are all of the function defs for the cli
#
# v 1.8.15a
# rev 2013-07-12 (SL: removed exec_debug)
# last major: (SL: added a debug function here that is really specific)

# Standard modules
import fnmatch, os, re, sys
import itertools as it
import numpy as np
from multiprocessing import Pool
from subprocess import call
from glob import iglob
from time import time

# local modules
import spikefn
import plotfn
import fileio as fio
import paramrw
import specfn
import pspec
import dipolefn
import axes_create as ac
import pmanu_gamma as pgamma

# Returns length of any list
def number_of_sims(some_list):
    return len(some_list)

# Just a simple thing to print parts of a list
def prettyprint(lines):
    for line in lines:
        print line

# gets a subdir list
def get_subdir_list(dcheck):
    if os.path.exists(dcheck):
        return [name for name in os.listdir(dcheck) if os.path.isdir(os.path.join(dcheck, name))]

    else:
        return []

# throwaway save method for now
# trial is currently undefined
# function is broken for N_trials > 1
def exec_throwaway(ddata, i=0, j=0):
    # take the ith sim, jth trial, do some stuff to it, resave it
    # only uses first expmt_group
    expmt_group = ddata.expmt_groups[0]
    f_dpl = ddata.file_match(expmt_group, 'rawdpl')[i]
    f_param = ddata.file_match(expmt_group, 'param')[i]

    # print ddata.sim_prefix, ddata.dsim
    f_name_short = '%s-%03d-T%02d-dpltest.txt' % (ddata.sim_prefix, i, j)
    f_name = os.path.join(ddata.dsim, expmt_group, f_name_short)
    print f_name

    dpl = dipolefn.Dipole(f_dpl)
    dpl.baseline_renormalize(f_param)
    print "baseline renormalized"

    dpl.convert_fAm_to_nAm()
    print "converted to nAm"

    dpl.write(f_name)

# calculates the mean dipole over a specified range
def exec_calc_dpl_mean(ddata, opts={}):
    for expmt_group in ddata.expmt_groups:
        list_fdpl = ddata.file_match(expmt_group, 'rawdpl')

        # order of l_dpl is same as list_fdpl
        l_dpl = [dipolefn.Dipole(f) for f in list_fdpl]

        for dpl in l_dpl:
            print dpl.mean_stationary(opts)

# calculates the linear regression, shows values of slope (m) and int (b)
# and plots line to dipole fig (in place)
def exec_calc_dpl_regression(ddata, opts={}):
     for expmt_group in ddata.expmt_groups:
        list_fdpl = ddata.file_match(expmt_group, 'rawdpl')
        list_figdpl = ddata.file_match(expmt_group, 'figdpl')

        # this is to overwrite the fig
        for f, ffig in it.izip(list_fdpl, list_figdpl):
            dipolefn.plinear_regression(ffig, f)

def exec_pdipole_evoked(ddata, ylim=[]):
    # runtype = 'parallel'
    runtype = 'debug'

    expmt_group = ddata.expmt_groups[0]

    # grab just the first element of the dipole list
    dpl_list = ddata.file_match(expmt_group, 'rawdpl')
    param_list = ddata.file_match(expmt_group, 'param')
    spk_list = ddata.file_match(expmt_group, 'rawspk')

    # fig dir will be that of the original dipole
    dfig = ddata.dfig[expmt_group]['figdpl']

    # first file names
    f_dpl = dpl_list[0]
    f_spk = spk_list[0]
    f_param = param_list[0]

    if runtype == 'parallel':
        pl = Pool()
        for f_dpl, f_spk, f_param in it.izip(dpl_list, spk_list, param_list):
            pl.apply_async(dipolefn.pdipole_evoked, (dfig, f_dpl, f_spk, f_param, ylim))

        pl.close()
        pl.join()

    elif runtype == 'debug':
        for f_dpl, f_spk, f_param in it.izip(dpl_list, spk_list, param_list):
            dipolefn.pdipole_evoked(dfig, f_dpl, f_spk, f_param, ylim)

# timer function wrapper returns WALL CLOCK time (more or less)
def timer(fn, args):
    t0 = time()
    x = eval(fn + args)
    t1 = time()

    print "%s took %4.4f s" % (fn, t1-t0)

    return x

def exec_pcompare(ddata, cli_args):
    vars = cli_args.split(" ")

    # find any expmt and just take the first one. (below)
    expmt = [arg.split("=")[1] for arg in vars if arg.startswith("expmt")]
    sim0  = int([arg.split("=")[1] for arg in vars if arg.startswith("sim0")][0])
    sim1  = int([arg.split("=")[1] for arg in vars if arg.startswith("sim1")][0])

    sims = [sim0, sim1]

    labels = ['A. Control E$_g$-I$_s$', 'B. Increased E$_g$-I$_s$']

    if expmt:
        psum.pcompare2(ddata, sims, labels, [expmt[0], expmt[0]])
    else:
        psum.pcompare2(ddata, sims, labels)
        # print "not found"

def exec_pcompare3(ddata, cli_args):
    # the args will be the 3 sim numbers.
    # these will be strings out of the split!
    vars = cli_args.split(' ')
    sim_no = int(vars[0])
    # expmt_last = int(vars[1])

    psum.pcompare3(ddata, sim_no)

# executes the function plotvar in psummary
# At some point, replace 'vars' with a non-standard variable name
def exec_plotvars(cli_args, ddata):
    # split the cli args based on options
    vars = cli_args.split(' --')

    # first part is always the first 2 options (required, no checks)
    vars_to_plot = vars[0].split()

    # grab the experiment handle
    # vars_expmt = [arg.split()[1] for arg in vars if arg.startswith('expmt')]
    vars_opts = [arg.split()[1:] for arg in vars if arg.startswith('opts')]

    # just pass the first of these
    if vars_opts:
        psum.plotvars(ddata, vars_to_plot[0], vars_opts[0])
        # psum.plotvars(ddata, vars_to_plot[0], vars_to_plot[1], vars_opts[0])
    # else:
        # run the plotvar function with the cli args
        # psum.plotvars(ddata, vars_to_plot[0])
        # psum.plotvars(ddata, vars_to_plot[0], vars_to_plot[1])

def exec_pphase(ddata, args):
    args_split = args.split(" ")
    expmt = args_split[0]
    N_sim = int(args_split[1])

    N_bins = 20

    psum.pphase(ddata, expmt, N_sim, N_bins)

# do_phist
def exec_phist(ddata, args):
    # somehow create these plots
    args_split = args.split(" ")
    N_sim = args_split[0]
    N_bins = int(args_split[1])
    psum.pphase_hist(ddata, N_sim, N_bins)

# find the spectral max over an interval, for a particular sim
def exec_specmax(ddata, expmt_group, n_sim, n_trial, t_interval):
    p_exp = paramrw.ExpParams(ddata.fparam)
    trial_prefix = p_exp.trial_prefix_str % (n_sim, n_trial)

    # list of all the dipoles
    dpl_list = ddata.file_match(expmt_group, 'rawdpl')
    spec_list = ddata.file_match(expmt_group, 'rawspec')

    # load the associated dipole file
    # find the specific file
    # assume just the first file
    try:
        fdpl = [file for file in dpl_list if trial_prefix in file][0]
        fspec = [file for file in spec_list if trial_prefix in file][0]
    except IndexError:
        print "List index out of range."
        print trial_prefix

    data = specfn.read(fspec)
    # print data['freq']
    # print data['TFR'].shape
    pwr_max = data['TFR'].max()
    max_mask = data['TFR']==pwr_max

    # this is a shift of 50 ms because the spec analysis incorrectly shifts its zero
    t_at_max = data['time'][max_mask.sum(axis=0)==1]
    f_at_max = data['freq'][max_mask.sum(axis=1)==1]

    # friendly printout
    # fmt_t = '%4.3f'
    # fmt_f = '%4.2f'
    print "Max power of %4.2e at f of %4.2f Hz at %4.3f ms" % (pwr_max, f_at_max, t_at_max)

    pd_at_max = 1000./f_at_max
    t_start = t_at_max - pd_at_max/2.
    t_end = t_at_max + pd_at_max/2.

    print "Symmetric interval at %4.2f Hz (T=%4.3f ms) about %4.3f ms is (%4.3f, %4.3f)" % (f_at_max, pd_at_max, t_at_max, t_start, t_end)

    # output structure
    data_max = {
        'pwr': pwr_max,
        't': t_at_max,
        'f': f_at_max,
    }

    return data_max

# search for the min in a dipole over specified interval
def exec_dipolemin(ddata, expmt_group, n_sim, n_trial, t_interval):
    p_exp = paramrw.ExpParams(ddata.fparam)
    trial_prefix = p_exp.trial_prefix_str % (n_sim, n_trial)

    # list of all the dipoles
    dpl_list = ddata.file_match(expmt_group, 'rawdpl')

    # load the associated dipole file
    # find the specific file
    # assume just the first file
    fdpl = [file for file in dpl_list if trial_prefix in file][0]

    data = np.loadtxt(open(fdpl, 'r'))
    t_vec = data[:, 0]
    data_dpl = data[:, 1]

    data_dpl_range = data_dpl[(t_vec >= t_interval[0]) & (t_vec <= t_interval[1])]
    dpl_min_range = data_dpl_range.min()
    t_min_range = t_vec[data_dpl == dpl_min_range]

    print "Minimum value over t range %s was %4.4f at %4.4f." % (str(t_interval), dpl_min_range, t_min_range)

# averages raw dipole or raw spec over all trials
def exec_avgtrials(ddata, datatype):
    # create the relevant key for the data
    datakey = 'raw' + datatype
    datakey_avg = 'avg' + datatype

    # assumes N_Trials are the same in both
    p_exp = paramrw.ExpParams(ddata.fparam)
    sim_prefix = p_exp.sim_prefix
    N_trials = p_exp.N_trials

    # fix for N_trials=0
    if not N_trials:
        N_trials = 1

    # prefix strings
    exp_prefix_str = p_exp.exp_prefix_str
    trial_prefix_str = p_exp.trial_prefix_str

    # Averaging must be done per expmt
    for expmt_group in ddata.expmt_groups:
        ddatatype = ddata.dfig[expmt_group][datakey]
        dparam = ddata.dfig[expmt_group]['param']

        param_list = ddata.file_match(expmt_group, 'param')
        rawdata_list = ddata.file_match(expmt_group, datakey)

        # if nothing in the raw data list, then generate it for spec
        if datakey == 'rawspec':
            if not len(rawdata_list):
                # generate the data!
                exec_spec_regenerate(ddata)
                rawdata_list = ddata.file_match(expmt_group, datakey)

        # simple length check, but will proceed bluntly anyway.
        # this will result in truncated lists, per it.izip function
        if len(param_list) != len(rawdata_list):
            print "warning, some weirdness detected in list length in exec_avgtrials. Check yo' lengths!"

        # number of unique simulations, per trial
        # this had better be equivalent as an integer or a float!
        N_unique = len(param_list) / N_trials

        # go through the unique simulations
        for i in range(N_unique):
            # fills in the correct int for the experimental prefix string formatter 'exp_prefix_str'
            prefix_unique = exp_prefix_str % i
            fprefix_long = os.path.join(ddatatype, prefix_unique)
            fprefix_long_param = os.path.join(dparam, prefix_unique)

            # create the sublist of just these trials
            unique_list = [rawdatafile for rawdatafile in rawdata_list if rawdatafile.startswith(fprefix_long)]
            unique_param_list = [pfile for pfile in param_list if pfile.startswith(fprefix_long_param)]

            # one filename per unique
            # length of the unique list is the number of trials for this sim, should match N_trials
            fname_unique = ddata.create_filename(expmt_group, datakey_avg, prefix_unique)

            # Average data for each trial
            # average dipole data
            if datakey == 'rawdpl':
                for f_dpl, f_param in it.izip(unique_list, unique_param_list):
                    dpl = dipolefn.Dipole(f_dpl)
                    # dpl = dipolefn.Dipole(f_dpl, f_param)

                    # ah, this is required becaused the dpl *file* still contains the raw, un-normalized data
                    dpl.baseline_renormalize(f_param)

                    # initialize and use x_dpl
                    if f_dpl is unique_list[0]:
                        # assume time vec stays the same throughout
                        t_vec = dpl.t
                        x_dpl_agg = dpl.dpl['agg']
                        x_dpl_L2 = dpl.dpl['L2']
                        x_dpl_L5 = dpl.dpl['L5']

                    else:
                        x_dpl_agg += dpl.dpl['agg']
                        x_dpl_L2 += dpl.dpl['L2']
                        x_dpl_L5 += dpl.dpl['L5']

                # poor man's mean
                x_dpl_agg /= len(unique_list)
                x_dpl_L2 /= len(unique_list)
                x_dpl_L5 /= len(unique_list)

                # write this data to the file
                # np.savetxt(fname_unique, avg_data, '%5.4f')
                with open(fname_unique, 'w') as f:
                    for t, x_agg, x_L2, x_L5 in it.izip(t_vec, x_dpl_agg, x_dpl_L2, x_dpl_L5):
                        f.write("%03.3f\t%5.4f\t%5.4f\t%5.4f\n" % (t, x_agg, x_L2, x_L5))

            # average spec data
            elif datakey == 'rawspec':
                # load TFR data into np array and avg by summing and dividing by n_trials 
                data_for_avg = np.array([np.load(file)['TFR'] for file in unique_list])
                spec_avg = data_for_avg.sum(axis=0)/data_for_avg.shape[0]

                # load time and freq vectors from the first item on the list, assume all same
                timevec = np.load(unique_list[0])['time']
                freqvec = np.load(unique_list[0])['freq']

                # save the aggregate info
                np.savez_compressed(fname_unique, time=timevec, freq=freqvec, TFR=spec_avg)

# run the spectral analyses on the somatic current time series
def exec_spec_current(ddata, opts_in=None):
    p_exp = paramrw.ExpParams(ddata.fparam)
    if opts_in is None:
        opts = {
            'type': 'dpl_laminar',
            'f_max': 150.,
            'save_data': 1,
            'runtype': 'debug',
        }
    else:
        opts = opts_in

    spec_results = specfn.analysis_typespecific(ddata, p_exp, opts)
    return spec_results

# this function can now use specfn.generate_missing_spec(ddata, f_max)
def exec_spec_regenerate(ddata, f_max=None):
    # regenerates and saves spec data
    p_exp = paramrw.ExpParams(ddata.fparam)
    spec_results = specfn.analysis(ddata, p_exp, f_max, save_data=1)

    return spec_results

# Time-averaged stationarity analysis - averages spec power over time and plots it
def exec_spec_stationary_avg(ddata, dsim, maxpwr):

    # Prompt user for type of analysis (per expmt or whole sim)
    analysis_type = raw_input('Would you like analysis per expmt or for whole sim? (expmt or sim): ')

    spec_results = fio.file_match(ddata.dsim, '-spec.npz')
    fparam_list = fio.file_match(ddata.dsim, '-param.txt')

    p_exp = paramrw.ExpParams(ddata.fparam)
    key_types = p_exp.get_key_types()

    # If no saved spec results exist, redo spec analysis
    if not spec_results:
        print "No saved spec data found. Performing spec analysis...",
        spec_results = exec_spec_regenerate(ddata)

        print "now doing spec freq-pwr analysis"

    # perform time-averaged stationary analysis
    specpwr_results = [specfn.specpwr_stationary_avg(dspec) for dspec in spec_results]

    # plot for whole simulation
    if analysis_type == 'sim':

        file_name = os.path.join(dsim, 'specpwr.eps')
        pspec.pspecpwr(file_name, specpwr_results, fparam_list, key_types)

        # if maxpwr plot indicated
        if maxpwr:
            f_name = os.path.join(dsim, 'maxpwr.png')
            specfn.pmaxpwr(f_name, specpwr_results, fparam_list)

    # plot per expmt
    if analysis_type == 'expmt':
        for expmt_group in ddata.expmt_groups:
            # create name for figure. Figure saved to expmt directory
            file_name = os.path.join(dsim, expmt_group, 'specpwr.png')

            # compile list of freqpwr results and param pathways for expmt
            partial_results_list = [result for result in specpwr_results if result['expmt']==expmt_group]
            partial_fparam_list = [fparam for fparam in fparam_list if expmt_group in fparam]

            # plot results
            pspec.pspecpwr(file_name, partial_results_list, partial_fparam_list, key_types)

            # if maxpwr plot indicated
            if maxpwr:
                f_name = os.path.join(dsim, expmt_group, 'maxpwr.png')
                specfn.pmaxpwr(f_name, partial_results_list, partial_fparam_list)

# Time-averaged Spectral-power analysis/plotting of avg spec data
def exec_spec_avg_stationary_avg(ddata, dsim, opts): 

    # Prompt user for type of analysis (per expmt or whole sim)
    analysis_type = raw_input('Would you like analysis per expmt or for whole sim? (expmt or sim): ')

    spec_results_avged = fio.file_match(ddata.dsim, '-specavg.npz')
    fparam_list = fio.file_match(ddata.dsim, '-param.txt')

    p_exp = paramrw.ExpParams(ddata.fparam)
    key_types = p_exp.get_key_types()

    # If no avg spec data found, generate it.
    if not spec_results_avged:
        exec_avgtrials(ddata, 'spec')  

    # perform time-averaged stationarity analysis
    specpwr_results = [specfn.specpwr_stationary_avg(dspec) for dspec in spec_results_avged]

    # create fparam list to match avg'ed data
    N_trials = p_exp.N_trials
    nums = np.arange(0, len(fparam_list), N_trials)
    fparam_list = [fparam_list[num] for num in nums]

    # plot for whole simulation
    if analysis_type == 'sim':

        # if error bars indicated
        if opts['errorbars']:
            # get raw (non avg'ed) spec data
            raw_spec_data = fio.file_match(ddata.dsim, '-spec.npz')

            # perform freqpwr analysis on raw data
            raw_specpwr = [specfn.specpwr_stationary_avg(dspec)['p_avg'] for dspec in raw_spec_data]

            # calculate standard error
            error_vec = specfn.calc_stderror(raw_specpwr)

        else:
            error_vec = []

        file_name = os.path.join(dsim, 'specpwr-avg.eps')
        pspec.pspecpwr(file_name, specpwr_results, fparam_list, key_types, error_vec)

        # # if maxpwr plot indicated
        # if maxpwr:
        #     f_name = os.path.join(dsim, 'maxpwr-avg.png')
        #     specfn.pmaxpwr(f_name, freqpwr_results_list, fparam_list)

    # plot per expmt
    if analysis_type == 'expmt':
        for expmt_group in ddata.expmt_groups:
            # if error bars indicated
            if opts['errorbars']:
                # get exmpt group raw spec data
                raw_spec_data = ddata.file_match(expmt_group, 'rawspec')

                # perform stationary analysis on raw data
                raw_specpwr = [specfn.specpwr_stationary_avg(dspec)['p_avg'] for dspec in raw_spec_data]

                # calculate standard error
                error_vec = specfn.calc_stderror(raw_specpwr)

            else:
                error_vec = []

            # create name for figure. Figure saved to expmt directory
            file_name = os.path.join(dsim, expmt_group, 'specpwr-avg.png')

            # compile list of specpwr results and param pathways for expmt
            partial_results_list = [result for result in specpwr_results if result['expmt']==expmt_group]
            partial_fparam_list = [fparam for fparam in fparam_list if expmt_group in fparam]

            # plot results
            pspec.pspecpwr(file_name, partial_results_list, partial_fparam_list, key_types, error_vec)

            # # if maxpwr plot indicated
            # if maxpwr:
            #     f_name = os.path.join(dsim, expmt_group, 'maxpwr-avg.png')
            #     specfn.pmaxpwr(f_name, partial_results_list, partial_fparam_list)

# Averages spec pwr over time and plots it with histogram of alpha feeds per simulation
def freqpwr_with_hist(ddata, dsim):
    spec_results = fio.file_match(ddata.dsim, '-spec.npz')
    spk_list = fio.file_match(ddata.dsim, '-spk.txt')
    fparam_list = fio.file_match(ddata.dsim, '-param.txt')

    p_exp = paramrw.ExpParams(ddata.fparam)
    key_types = p_exp.get_key_types()

    # If no save spec reslts exist, redo spec analysis
    if not spec_results:
        print "No saved spec data found. Performing spec analysis...",
        spec_results = exec_spec_regenerate(ddata)

        print "now doing spec freq-pwr analysis"

    # perform freqpwr analysis
    freqpwr_results_list = [specfn.freqpwr_analysis(dspec) for dspec in spec_results]

    # Plot
    for freqpwr_result, f_spk, fparam in it.izip(freqpwr_results_list, spk_list, fparam_list):
        gid_dict, p_dict = paramrw.read(fparam)
        file_name = 'freqpwr.png'

        specfn.pfreqpwr_with_hist(file_name, freqpwr_result, f_spk, gid_dict, p_dict, key_types)

# runs plotfn.pall *but* checks to make sure there are spec data
def regenerate_plots(ddata, xlim=[0, 'tstop']):
    # need p_exp, spec_results, gid_dict, and tstop.
    # fparam = fio.file_match(ddata.dsim, '.param')[0]

    # recreate p_exp ... don't like this
    # ** should be guaranteed to be identical **
    p_exp = paramrw.ExpParams(ddata.fparam)

    # grab the list of spec results that exists
    # there is a method in SimulationPaths/ddata for this specifically, this should be deprecated
    spec_results = fio.file_match(ddata.dsim, '-spec.npz')

    # generate data if no spec exists here
    if not spec_results:
        print "No saved spec data found. Performing spec anaylsis ... "
        spec_results = exec_spec_regenerate(ddata)

    # run our core pall plot
    plotfn.pall(ddata, p_exp, spec_results, xlim)

# function to add alpha feed hists
def exec_addalphahist(ddata, xlim=[0, 'tstop']):
    p_exp = paramrw.ExpParams(ddata.fparam)

    spec_results = fio.file_match(ddata.dsim, '-spec.npz')

    # generate data if no spec exists here
    if not spec_results:
        print "No saved spec data found. Performing spec anaylsis ... "
        spec_results = exec_spec_regenerate(ddata)

    plotfn.pdpl_pspec_with_hist(ddata, p_exp, spec_results, xlim)

def exec_aggregatespec(ddata, labels):
    p_exp = paramrw.ExpParams(ddata.fparam)

    spec_results = fio.file_match(ddata.dsim, '-spec.npz')

    # generate data if no spec exists here
    if not spec_results:
        print "No saved spec data found. Performing spec anaylsis ... "
        spec_results = exec_spec_regenerate(ddata)

    plotfn.aggregate_spec_with_hist(ddata, p_exp, spec_results, labels)

# comparison of all layers and aggregate data
def exec_pgamma_laminar(ddata):
    pgamma.laminar(ddata)

# comparison between a PING (ddata0) and a weak PING (ddata1) data set
def exec_pgamma_compare_ping():
# def exec_pgamma_compare_ping(ddata0, ddata1, opts):
    pgamma.compare_ping()

# plot for gamma stdev on a given ddata
def exec_pgamma_stdev(ddata):
    pgamma.pgamma_stdev(ddata)

# plot for gamma distal phase on a given ddata
def exec_pgamma_distal_phase(ddata, opts):
    pgamma.pgamma_distal_phase(ddata, opts['spec0'], opts['spec1'], opts['spec2'])

# plot data averaged over trials
# dipole and spec should be split up at some point (soon)
# ylim specified here is ONLY for the dipole
def exec_plotaverages(ddata, ylim=[]):
    # runtype = 'parallel'
    runtype = 'debug'

    # this is a qnd check to create the fig dir if it doesn't already exist
    # backward compatibility check for sims that didn't auto-create these dirs
    for expmt_group in ddata.expmt_groups:
        dfig_avgdpl = ddata.dfig[expmt_group]['figavgdpl']
        dfig_avgspec = ddata.dfig[expmt_group]['figavgspec']

        # create them if they did not previously exist
        fio.dir_create(dfig_avgdpl)
        fio.dir_create(dfig_avgspec)

    # presumably globally true information
    p_exp = paramrw.ExpParams(ddata.fparam)
    key_types = p_exp.get_key_types()

    # empty lists to be used/appended
    dpl_list = []
    spec_list = []
    dfig_list = []
    dfig_dpl_list = []
    dfig_spec_list = []
    pdict_list = []

    # by doing all file operations sequentially by expmt_group in this iteration
    # trying to guarantee order better than before
    for expmt_group in ddata.expmt_groups:
        # print expmt_group, ddata.dfig[expmt_group]

        # avgdpl and avgspec data paths
        # fio.file_match() returns lists sorted
        # dpl_list_expmt is so i can iterate through them in a sec
        dpl_list_expmt = fio.file_match(ddata.dfig[expmt_group]['avgdpl'], '-dplavg.txt')
        dpl_list += dpl_list_expmt
        spec_list += fio.file_match(ddata.dfig[expmt_group]['avgspec'], '-specavg.npz')

        # create redundant list of avg dipole dirs and avg spec dirs
        # unique parts are expmt group names
        # create one entry for each in dpl_list
        dfig_list_expmt = [ddata.dfig[expmt_group] for path in dpl_list_expmt]
        dfig_list += dfig_list_expmt
        dfig_dpl_list += [dfig['figavgdpl'] for dfig in dfig_list_expmt]
        dfig_spec_list += [dfig['figavgspec'] for dfig in dfig_list_expmt]

        # param list to match avg data lists
        fparam_list = fio.fparam_match_minimal(ddata.dfig[expmt_group]['param'], p_exp) 
        pdict_list += [paramrw.read(f_param)[1] for f_param in fparam_list]

    if dpl_list:
        # new input to dipolefn
        pdipole_dict = {
            'xmin': 0.,
            'xmax': None,
            'ymin': None,
            'ymax': None,
        }

        # if there is a length, assume it's 2 (it should be!)
        if len(ylim):
            pdipole_dict['ymin'] = ylim[0]
            pdipole_dict['ymax'] = ylim[1]

        if runtype == 'debug':
            for f_dpl, f_param, dfig_dpl in it.izip(dpl_list, fparam_list, dfig_dpl_list):
                dipolefn.pdipole(f_dpl, f_param, dfig_dpl, key_types, pdipole_dict)

        elif runtype == 'parallel':
            pl = Pool()
            for f_dpl, f_param, dfig_dpl in it.izip(dpl_list, fparam_list, dfig_dpl_list):
                pl.apply_async(dipolefn.pdipole, (f_dpl, f_param, dfig_dpl, key_types, pdipole_dict))

            pl.close()
            pl.join()

    else:
        print "No avg dipole data found."
        return 0

    # if avg spec data exists
    if spec_list:
        if runtype == 'debug':
            for f_spec, f_dpl, dfig_spec, pdict in it.izip(spec_list, dpl_list, dfig_spec_list, pdict_list):
                pspec.pspec_dpl(f_spec, f_dpl, dfig_spec, pdict, key_types)

        elif runtype == 'parallel':
            pl = Pool()
            for f_spec, f_dpl, dfig_spec, pdict in it.izip(spec_list, dpl_list, dfig_spec_list, pdict_list):
                pl.apply_async(pspec.pspec_dpl, (f_spec, f_dpl, dfig_spec, pdict, key_types))

            pl.close()
            pl.join()

    else:
        print "No averaged spec data found. Run avgtrials()."
        return 0

# rsync command with excludetype input
def exec_sync(droot, server_remote, dsubdir, fshort_exclude='exclude_eps.txt'):
    # make up the local exclude file name
    # f_exclude = os.path.join(droot, 'exclude_eps.txt')
    f_exclude = os.path.join(droot, fshort_exclude)

    # create remote and local directories, they should look similar
    dremote = os.path.join(droot, dsubdir)
    dlocal = os.path.join(droot, 'from_remote')

    # creat the rsync command
    cmd_rsync = "rsync -ruv --exclude-from '%s' -e ssh %s:%s %s" % (f_exclude, server_remote, dremote, dlocal)

    call(cmd_rsync, shell=True)

# save to cppub
def exec_save(dproj, ddate, dsim):
    if fio.dir_check(dsim):
        dsave_root = os.path.join(dproj, 'pub')

        # check to see if this dir exists or not, and create it if not
        fio.dir_create(dsave_root)

        dsave_short = '%s_%s' % (ddate.split('/')[-1], dsim.split('/')[-1])
        dsave = os.path.join(dsave_root, dsave_short)

        # use fileio routine to non-destructively copy dir
        fio.dir_copy(dsim, dsave)

    else:
        print "Not sure I can find that directory."
        return 1

# Creates a pdf from a file list and saves it generically to ddata
def pdf_create(ddata, fprefix, flist):
    file_out = os.path.join(ddata, fprefix + '-summary.pdf')

    # create the beginning of the call to ghostscript
    gscmd = 'gs -dNumRenderingThreads=8 -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=' + file_out + ' -f '

    for file in flist:
        gscmd += file + ' '

    # print gscmd
    call(gscmd, shell=True)

    return file_out

# PDF Viewer
def view_pdf(pdffile):
    if sys.platform.startswith('darwin'):
        app_pdf = 'open -a skim '
    elif sys.platform.startswith('linux'):
        app_pdf = 'evince '

    call([app_pdf + pdffile + ' &'], shell=True)

# PDF finder ... (this is starting to get unwieldy)
def find_pdfs(ddata, expmt):
    if expmt == 'all':
        # This is recursive
        # find the ONE pdf in the root dir
        # all refers to the aggregated pdf file
        pdf_list = [f for f in iglob(os.path.join(ddata, '*.pdf'))]

    elif expmt == 'each':
        # get each and every one of these (syntax matches below)
        pdf_list = fio.file_match(ddata, '*.pdf')
    else:
        # do this non-recursively (i.e. just for this directory)
        dexpmt = os.path.join(ddata, expmt, '*.pdf')
        pdf_list = [f for f in iglob(dexpmt)]

    # Check the length of pdf_list
    if len(pdf_list) > 3:
        print "There are", len(pdf_list), "files here."
        str_open = raw_input("Do you want to open them all? ")
    else:
        # just set to open the files if fewer than 3
        str_open = 'y'

    # now check for a yes and go
    if str_open == 'y':
        for file in pdf_list:
            view_pdf(file)
    else:
        print "Okay, good call. Here's the consolation prize:\n"
        prettyprint(pdf_list)

# Cross-platform file viewing using eog or xee, cmd is pngv in cli.py
def view_img(dir_data, ext):
    # platform and extension specific opening
    if sys.platform.startswith('darwin'):
        ext_img = '/*' + ext
        app_img = 'open -a xee '
    elif sys.platform.startswith('linux'):
        if ext == 'png':
            app_img = 'eog '
        elif ext == 'eps':
            app_img = 'evince '
        ext_img = '/*' + ext + '&'

    call([app_img + os.path.join(dir_data, 'spec') + ext_img], shell=True)

# Cross platform file viewing over all expmts
def file_viewer(ddata, expmt):
    if expmt == 'all':
        # Find all of the png files in this directory
        files_png = fio.file_match(ddata, '*.png')

        # Create an empty file argument
        files_arg = ''
        for file in files_png:
            files_arg += file + ' '
        
        if sys.platform.startswith('darwin'):
            app_img = 'open -a xee '
            call([app_img + files_arg], shell=True)
        elif sys.platform.startswith('linux'):
            app_img = 'eog '
            call([app_img + files_arg + '&'], shell=True)
    else:
        dexpmt = os.path.join(ddata, expmt)
        view_img(dexpmt, 'png')

# a really simple image viewer, views images in dimg
def png_viewer_simple(dimg):
    list_fpng = fio.file_match(dimg, '*.png')

    # Create an empty file argument
    files_arg = ''
    for file in list_fpng:
        files_arg += file + ' '

    # uses xee
    if sys.platform.startswith('darwin'):
        app_img = 'open -a xee '
        call([app_img + files_arg], shell=True)

    # uses eye of gnome (eog)
    elif sys.platform.startswith('linux'):
        app_img = 'eog '
        call([app_img + files_arg + '&'], shell=True)
