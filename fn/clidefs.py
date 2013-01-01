# clidefs.py - these are all of the function defs for the cli
#
# v 1.5.10
# rev 2012-12-31 (MS: Regenerate spec data) 
# last major: (SL: Regenerate plots)

# Standard modules
import fnmatch, os, re, sys
from subprocess import call
from glob import iglob
from time import time

# my runa1 module
# import psdfn as pwr
# import plot.psummary as psum
# import pylib.psdfn as pwr
import spikefn
import plotfn
import fileio as fio
import paramrw
import spec

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
    # print N_sim, N_bins
    psum.pphase_hist(ddata, N_sim, N_bins)

def exec_pwr(ddata):
    pwr.psd(ddata)

def exec_rates(ddata):
    spk.calc_rates(ddata)

# Just run the autoplot function independently
# do_plot
def regenerate_spec_data(ddata):
    # regenerates and saves spec data

    p_exp = paramrw.ExpParams(ddata.fparam)
    spec_results = spec.analysis(ddata, p_exp, save_data=1)

    return spec_results

def regenerate_plots(ddata):
    # need p_exp, spec_results, gid_dict, and tstop.
    # fparam = fio.file_match(ddata.dsim, '.param')[0]

    # recreate p_exp ... don't like this.o
    # ** should be guaranteed to be identical **
    p_exp = paramrw.ExpParams(ddata.fparam)

    spec_results = fio.file_match(ddata.dsim, '-spec.npz')
    # prettyprint(spec_list_total)

    # generate data if no spec exists here
    if not spec_results:
        print "No saved spec data found. Preforming spec anaylsis...",
        spec_results = regenerate_spec_data(ddata)
        
        print "now plotting"

    # else:
    #     print "it's going to break ... now!"

    plotfn.pall(ddata, p_exp, spec_results)

# rsync command with excludetype input
def sync_remote_data(droot, server_remote, dsubdir):
    # make up the local exclude file name
    f_exclude = os.path.join(droot, 'exclude_eps.txt')

    # create remote and local directories, they should look similar
    dremote = os.path.join(droot, dsubdir)
    dlocal = os.path.join(droot, 'from_remote')

    # create the rsync command
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
