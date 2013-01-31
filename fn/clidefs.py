# clidefs.py - these are all of the function defs for the cli
#
# v 1.7.12
# rev 2013-01-30 (SL: dipole_min_in_interval created)
# last major: (SL: Major changes to avg_over_trials)

# Standard modules
import fnmatch, os, re, sys
import itertools as it
import numpy as np
from multiprocessing import Pool
from subprocess import call
from glob import iglob
from time import time

# my runa1 module
import spikefn
import plotfn
import fileio as fio
import paramrw
import spec
import pdipole
import axes_create

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

# timer function wrapper returns WALL CLOCK time (more or less)
def timer(fn, args):
    t0 = time()
    x = eval(fn + args)
    t1 = time()

    print "%s took %4.4f s" % (fn, t1-t0)

    return x

# execute running a1_laminar
def exec_runa1(file_input):
    # runs the experiments, returns variables for data directory and exp list
    dir_data, expmts = timer('kainsim', '(\'%s\')'% file_input)

    # runs the psd function and saves the file
    # timer('pwr.psd', '(\'%s\')'% dir_data)

    # run the spike and rate stuff and saves the files
    # timer('spk.calc_rates', '(\'%s\')'% dir_data)

    # runs the plot function
    # timer('plotfn.auto', '(\'%s\')'% dir_data)

    return dir_data, expmts

def exec_pcompare(ddata, cli_args):
    vars = cli_args.split(" ")

    # find any expmt and just take the first one. (below)
    expmt = [arg.split("=")[1] for arg in vars if arg.startswith("expmt")]
    sim0  = int([arg.split("=")[1] for arg in vars if arg.startswith("sim0")][0])
    sim1  = int([arg.split("=")[1] for arg in vars if arg.startswith("sim1")][0])

    sims = [sim0, sim1]

    # print expmt, [sim0, sim1]

    labels = ['A. Control E$_g$-I$_s$', 'B. Increased E$_g$-I$_s$']

    if expmt:
        # print expmt
        psum.pcompare2(ddata, sims, labels, [expmt[0], expmt[0]])
    else:
        psum.pcompare2(ddata, sims, labels)
        # print "not found"

def exec_pcompare3(ddata, cli_args):
    # the args will be the 3 sim numbers.
    # these will be strings out of the split!
    # print cli_args
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

def exec_pwr(ddata):
    pwr.psd(ddata)

def exec_rates(ddata):
    spk.calc_rates(ddata)

# search for the min in a dipole over specified interval
def dipole_min_in_interval(ddata, expmt_group, n_sim, n_trial, t_interval):
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
def avg_over_trials(ddata, datatype):
    # create the relevant key for the data
    datakey = 'raw' + datatype
    datakey_avg = 'avg' + datatype

    # assumes N_Trials are the same in both
    p_exp = paramrw.ExpParams(ddata.fparam)
    sim_prefix = p_exp.sim_prefix
    N_trials = p_exp.N_trials

    # prefix strings
    exp_prefix_str = p_exp.exp_prefix_str
    trial_prefix_str = p_exp.trial_prefix_str

    # Averaging must be done per expmt
    for expmt_group in ddata.expmt_groups:
        ddatatype = ddata.dfig[expmt_group][datakey]

        param_list = ddata.file_match(expmt_group, 'param')
        rawdata_list = ddata.file_match(expmt_group, datakey)

        # if nothing in the raw data list, then generate it for spec
        if datakey == 'rawspec':
            if not len(rawdata_list):
                # generate the data!
                regenerate_spec_data(ddata)
                rawdata_list = ddata.file_match(expmt_group, datakey)

        # simple length check, but will proceed bluntly anyway.
        # this will result in truncated lists, per it.izip function
        if len(param_list) != len(rawdata_list):
            print "warning, some weirdness detected in list length in avg_over_trials. Check yo' lengths!"

        # number of unique simulations, per trial
        # this had better be equivalent as an integer or a float!
        N_unique = len(param_list) / N_trials

        # go through the unique simulations
        for i in range(N_unique):
            prefix_unique = exp_prefix_str % i
            fprefix_long = os.path.join(ddatatype, prefix_unique)

            # create the sublist of just these trials
            unique_list = [rawdatafile for rawdatafile in rawdata_list if rawdatafile.startswith(fprefix_long)]

            # one filename per unique
            # length of the unique list is the number of trials for this sim, should match N_trials
            fname_unique = ddata.create_filename(expmt_group, datakey_avg, prefix_unique)

            # Average data for each trial
            # average dipole data
            if datakey == 'rawdpl':
                for file in unique_list:
                    x_tmp = np.loadtxt(open(file, 'r'))

                    if file is unique_list[0]:
                        # assume time vec stays the same throughout
                        t_vec = x_tmp[:, 0]
                        x_dpl = x_tmp[:, 1]

                    else:
                        x_dpl += x_tmp[:, 1]

                # poor man's mean
                x_dpl /= len(unique_list)

                # write this data to the file
                # np.savetxt(fname_unique, avg_data, '%5.4f')
                with open(fname_unique, 'w') as f:
                    for t, x in it.izip(t_vec, x_dpl):
                        f.write("%03.3f\t%5.4f\n" % (t, x))

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

def regenerate_spec_data(ddata):
    # regenerates and saves spec data
    p_exp = paramrw.ExpParams(ddata.fparam)
    spec_results = spec.analysis(ddata, p_exp, save_data=1)

    return spec_results

def freqpwr_analysis(ddata, dsim, maxpwr):
    # Averages spec power over time and plots it

    # Prompt user for type of analysis (per exmpt or whole sim) 
    analysis_type = raw_input('Would you like analysis per exmpt or for whole sim? (expmt or sim): ')

    spec_results = fio.file_match(ddata.dsim, '-spec.npz')
    spec_results_avged = fio.file_match(ddata.dsim, '-avgspec.npz')
    fparam_list = fio.file_match(ddata.dsim, '-param.txt')

    p_exp = paramrw.ExpParams(ddata.fparam)
    key_types = p_exp.get_key_types()

    # If no save spec reslts exist, redo spec analysis
    if not spec_results:
        print "No saved spec data found. Performing spec analysis...",
        spec_results = regenerate_spec_data(ddata)

        print "now doing spec freq-pwr analysis"

    # perform freqpwr analysis
    freqpwr_results_list = [spec.freqpwr_analysis(dspec) for dspec in spec_results]

    # plot for whole simulation
    if analysis_type == 'sim':

        file_name = os.path.join(dsim, 'freqpwr.png')
        spec.pfreqpwr(file_name, freqpwr_results_list, fparam_list, key_types)

        # if maxpwr plot indicated
        if maxpwr:
            f_name = os.path.join(dsim, 'maxpwr.png')
            spec.pmaxpwr(f_name, freqpwr_results_list, fparam_list)

    # plot per exmpt
    if analysis_type == 'expmt':
        for expmt_group in ddata.expmt_groups:
            # create name for figure. Figure saved to exmpt directory
            file_name = os.path.join(dsim, expmt_group, 'freqpwr.png')
            # file_name = os.path.join(dsim, expmt_group, 'figfreqpwr', 'freqpwr.png')

            # compile list of freqpwr results and param pathways for exmpt
            partial_results_list = [result for result in freqpwr_results_list if result['expmt']==expmt_group]
            partial_fparam_list = [fparam for fparam in fparam_list if expmt_group in fparam]

            # plot results
            spec.pfreqpwr(file_name, partial_results_list, partial_fparam_list, key_types)

            # if maxpwr plot indicated
            if maxpwr:
                f_name = os.path.join(dsim, expmt_group, 'maxpwr.png')
                spec.pmaxpwr(f_name, partial_results_list, partial_fparam_list)

    if spec_results_avged:
        # perform freqpwr analysis
        freqpwr_results_list = [spec.freqpwr_analysis(dspec) for dspec in spec_results_avged]

        # create fparam list to match avg'ed data
        N_trials = p_exp.N_trials
        nums = np.arange(0, len(fparam_list), N_trials)
        fparam_list = [fparam_list[num] for num in nums]
 
        # plot for whole simulation
        if analysis_type == 'sim':

            file_name = os.path.join(dsim, 'freqpwr-avg.png')
            spec.pfreqpwr(file_name, freqpwr_results_list, fparam_list, key_types)

            # if maxpwr plot indicated
            if maxpwr:
                f_name = os.path.join(dsim, 'maxpwr-avg.png')
                spec.pmaxpwr(f_name, freqpwr_results_list, fparam_list)

        # plot per exmpt
        if analysis_type == 'expmt':
            for expmt_group in ddata.expmt_groups:
                # create name for figure. Figure saved to exmpt directory
                file_name = os.path.join(dsim, expmt_group, 'freqpwr-avg.png')
                # file_name = os.path.join(dsim, expmt_group, 'figfreqpwr', 'freqpwr.png')

                # compile list of freqpwr results and param pathways for exmpt
                partial_results_list = [result for result in freqpwr_results_list if result['expmt']==expmt_group]
                partial_fparam_list = [fparam for fparam in fparam_list if expmt_group in fparam]

                # plot results
                spec.pfreqpwr(file_name, partial_results_list, partial_fparam_list, key_types)

                # if maxpwr plot indicated
                if maxpwr:
                    f_name = os.path.join(dsim, expmt_group, 'maxpwr-avg.png')
                    spec.pmaxpwr(f_name, partial_results_list, partial_fparam_list)

def regenerate_plots(ddata):
    # need p_exp, spec_results, gid_dict, and tstop.
    # fparam = fio.file_match(ddata.dsim, '.param')[0]

    # recreate p_exp ... don't like this
    # ** should be guaranteed to be identical **
    p_exp = paramrw.ExpParams(ddata.fparam)

    spec_results = fio.file_match(ddata.dsim, '-spec.npz')

    # generate data if no spec exists here
    if not spec_results:
        print "No saved spec data found. Performing spec anaylsis ... ",
        spec_results = regenerate_spec_data(ddata)

        print "now plotting"

    plotfn.pall(ddata, p_exp, spec_results)

def add_alpha_feed_hist(ddata):
    p_exp = paramrw.ExpParams(ddata.fparam)

    spec_results = fio.file_match(ddata.dsim, '-spec.npz')

    # generate data if no spec exists here
    if not spec_results:
        print "No saved spec data found. Performing spec anaylsis ... ",
        spec_results = regenerate_spec_data(ddata)

        print "Now plotting"

    plotfn.pdpl_pspec_with_hist(ddata, p_exp, spec_results)

# plot data averaged over trials
def plot_avg_data(ddata):
    # avgdpl and avgspec data paths
    dpl_list = fio.file_match(ddata.dsim, '-avgdpl.txt')
    spec_list = fio.file_match(ddata.dsim, '-avgspec.npz')

    print dpl_list

    p_exp = paramrw.ExpParams(ddata.fparam)
    key_types = p_exp.get_key_types()

    # param list to match avg data lists
    fparam_list = fio.fparam_match_minimal(ddata.dsim, p_exp) 
    pdict_list = [paramrw.read(f_param)[1] for f_param in fparam_list]

    dfig_list = []

    # append as many copies of expmt dfig dicts as necessary
    for expmt_group in ddata.expmt_groups:
        dfig_list.extend([ddata.dfig[expmt_group] for path in dpl_list if expmt_group in path])

    # construct list of names fig dirs for each data type
    dfig_dpl_list = [os.path.join(dfig['figdpl'], 'avgdpl') for dfig in dfig_list]
    dfig_spec_list = [os.path.join(dfig['figspec'], 'avgspec') for dfig in dfig_list]

    # if avg dpl data exists
    if dpl_list:
        # directory creation
        for dfig_dpl in dfig_dpl_list:
            if not os.path.exists(dfig_dpl):
                os.makedirs(dfig_dpl)

        # plot avg dpl
        pl = Pool()
        for dfig_dpl, p_dict, f_dpl in it.izip(dfig_dpl_list, pdict_list, dpl_list):
            pl.apply_async(pdipole.pdipole, (f_dpl, dfig_dpl, p_dict, key_types))

        pl.close()
        pl.join()

    else:
        print "No averaged dpl data found. Cannot continue without it. Run avgtrials()."
        return 0

    # if avg spec data exists
    if spec_list:
        # directory creation
        for dfig_spec in dfig_spec_list:
            if not os.path.exists(dfig_spec):
                os.makedirs(dfig_spec)

        # plot avg spec
        pl = Pool()
        for dfig_spec, p_dict, f_spec, f_dpl in it.izip(dfig_spec_list, pdict_list, spec_list, dpl_list):
            pl.apply_async(spec.pspec, (f_spec, f_dpl, dfig_spec, p_dict, key_types))

        pl.close()
        pl.join()

    else:
        print "No averaged sped data found either. Run avgtrials()."

# rsync command with excludetype input
def sync_remote_data(droot, server_remote, dsubdir):
    # make up the local exclude file name
    f_exclude = os.path.join(droot, 'exclude_eps.txt')

    # create remote and local directories, they should look similar
    dremote = os.path.join(droot, dsubdir)
    dlocal = os.path.join(droot, 'from_remote')

    # creat the rsync command
    cmd_rsync = "rsync -ruv --exclude-from '%s' -e ssh %s:%s %s" % (f_exclude, server_remote, dremote, dlocal)

    call(cmd_rsync, shell=True)

# at the moment broken, i removed the data_root() function
def copy_to_pub(dsim):
    # check to see if sim dir exists
    # check to see if analogous dir in cppub exists
    # if doesn't exist, copy it. otherwise ... figure out later.
    dsub = dsim.split('/')[-1]
    dpub = os.path.join(data_root(), 'cppub', dsub)

    if os.path.exists(dpub):
        print "Directory already exists, will not overwrite."
        return 0
    else:
        cpcmd = 'cp -R ' + dsim + ' ' + dpub
        call(cpcmd, shell=True)

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
        # prettyprint(pdf_list)
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

# Commonly used plot commands, just really writing them down.
# def plotcmds():
    # geges
    # In cppub, load rho_eges-000
