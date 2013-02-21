# fileio.py - general file input/output functions
#
# v 1.7.25
# rev 2013-02-20 (SL: Fixed a bug in N_trials=0, unrelated to the last bug of this sort ...)
# last rev: (SL: Added new avg data type directories)

import datetime, fnmatch, os, shutil, sys
import itertools as it
import subprocess, multiprocessing
import numpy as np
import paramrw

# Cleans input files
def clean_lines(file):
    with open(file) as f_in:
        lines = (line.rstrip() for line in f_in)
        lines = [line for line in lines if line]

    return lines

# create gid dict from a file
def gid_dict_from_file(fparam):
    l = ['L2_pyramidal', 'L5_pyramidal', 'L2_basket', 'L5_basket', 'extinput']
    d = dict.fromkeys(l)

    plist = clean_lines(fparam)
    for param in plist:
        print param

# create file name for temporary spike file
# that every processor is aware of
def file_spike_tmp(dproj):
    filename_spikes = 'spikes_tmp.spk'
    file_spikes = os.path.join(dproj, filename_spikes)
    return file_spikes

# this is ugly, potentially. sorry, future
# i.e will change when the file name format changes
def strip_extprefix(filename):
    f_raw = filename.split("/")[-1]
    f = f_raw.split(".")[0].split("-")[:-1]
    ext_prefix = f.pop(0)

    for part in f:
        ext_prefix += "-%s" % part

    return ext_prefix

# Get the data files matching file_ext in this directory
# this function traverses ALL directories
# local=1 makes the search local and not recursive
def file_match(dsearch, file_ext, local=0):
    file_list = []

    if not local:
        if os.path.exists(dsearch):
            for root, dirnames, filenames in os.walk(dsearch):
                for fname in fnmatch.filter(filenames, '*'+file_ext):
                    file_list.append(os.path.join(root, fname))
    else:
        file_list = [os.path.join(dsearch, file) for file in os.listdir(dsearch) if file.endswith(file_ext)]

    # sort file list? untested
    file_list.sort()

    return file_list

# Get minimum list of param dicts (i.e. excludes duplicates due to N_trials > 1)
def fparam_match_minimal(dsim, p_exp):
    # Complete list of all param dicts used in simulation
    fparam_list_complete = file_match(dsim, '-param.txt')

    # List of indices from which to pull param dicts from fparam_list_complete
    N_trials = p_exp.N_trials
    if not N_trials:
        N_trials = 1
    indexes = np.arange(0, len(fparam_list_complete), N_trials)

    # Pull unique param dicts from fparam_list_complete
    fparam_list_minimal = [fparam_list_complete[ind] for ind in indexes]

    return fparam_list_minimal

# check any directory
def dir_check(d):
    if not os.path.isdir(d):
        return 0

    else:
        return os.path.isdir(d)

# only create if check comes back 0
def dir_create(d):
    if not dir_check(d):
        os.makedirs(d)

# creates data dirs and a dictionary of useful types
# self.dfig is a dictionary of experiments, which is each a dictionary of data type
# keys and the specific directories that contain them.
class SimulationPaths():
    def __init__(self):
        # hard coded data types
        # fig extensions are not currently being used as well as they could be
        # add new directories here to be automatically created for every simulation
        self.__datatypes = {
            'rawspk': '-spk.txt',
            'rawdpl': '-dpl.txt',
            'rawspec': '-spec.npz',
            'avgdpl': '-dplavg.txt',
            'avgspec': '-specavg.npz',
            'figavgdpl': '-dplavg.eps',
            'figavgspec': '-specavg.eps',
            'figdpl': '-dpl.eps',
            'figspec': '-spec.eps',
            'figspk': '-spk.eps',
            'param': '-param.txt',
        }

    # reads sim information based on sim directory and param files
    def read_sim(self, dproj, dsim):
        self.dproj = dproj
        self.dsim = dsim

        # match the param from this sim
        self.fparam = file_match(dsim, '.param')[0]
        self.expmt_groups = paramrw.read_expmt_groups(self.fparam)
        self.sim_prefix = paramrw.read_sim_prefix(self.fparam)
        self.dexpmt_dict = self.__create_dexpmt(self.expmt_groups)

        # create dfig
        self.dfig = self.__read_dirs()

        return self.dsim

    # only run for the creation of a new simulation
    def create_new_sim(self, dproj, expmt_groups, sim_prefix='test'):
        self.dproj = dproj
        self.expmt_groups = expmt_groups

        # prefix for these simulations in both filenames and directory in ddate
        self.sim_prefix = sim_prefix

        # create date and sim directories if necessary
        self.ddate = self.__datedir()
        self.dsim = self.__simdir()
        self.dexpmt_dict = self.__create_dexpmt(self.expmt_groups)

        # dfig is just a record of all the fig directories, per experiment
        # will only be written to at time of creation, by create_dirs
        # dfig is a terrible variable name, sorry!
        self.dfig = self.__ddata_dict_template()

    # creates a dict of dicts for each experiment and all the datatype directories
    # this is the empty template that gets filled in later.
    def __ddata_dict_template(self):
        dfig = dict.fromkeys(self.expmt_groups)

        for key in dfig:
            dfig[key] = dict.fromkeys(self.__datatypes)

        return dfig

    # read directories for an already existing sim
    def __read_dirs(self):
        dfig = self.__ddata_dict_template()

        for expmt_group, dexpmt in self.dexpmt_dict.iteritems():
            for key in self.__datatypes.keys():
                ddatatype = os.path.join(dexpmt, key)
                dfig[expmt_group][key] = ddatatype

        return dfig

    # extern function to create directories
    def create_dirs(self):
        # create expmt directories
        for expmt_group, dexpmt in self.dexpmt_dict.iteritems():
            dir_create(dexpmt)

            for key in self.__datatypes.keys():
                ddatatype = os.path.join(dexpmt, key)
                self.dfig[expmt_group][key] = ddatatype
                dir_create(ddatatype)

    # Returns date directory
    # this is NOT safe for midnight
    def __datedir(self):
        str_date = datetime.datetime.now().strftime("%Y-%m-%d")
        ddate = os.path.join(self.dproj, str_date)
        return ddate

    # returns the directory for the sim
    def __simdir(self):
        n = 0
        self.sim_name = self.sim_prefix + '-%03d' % n
        dsim = os.path.join(self.ddate, self.sim_name)

        while dir_check(dsim):
            n += 1
            self.sim_name = self.sim_prefix + '-%03d' % n
            dsim = os.path.join(self.ddate, self.sim_name)

        return dsim

    # creates all the experimental directories based on dproj
    def __create_dexpmt(self, expmt_groups):
        d = dict.fromkeys(expmt_groups)
        for expmt_group in d:
            d[expmt_group] = os.path.join(self.dsim, expmt_group)

        return d

    # dictionary creation
    # this is specific to a expmt_group
    def create_dict(self, expmt_group):
        fileinfo = dict.fromkeys(self.__datatypes)

        for key in self.__datatypes.keys():
            # join directory name
            dtype = os.path.join(self.dexpmt_dict(expmt_group), key)
            fileinfo[key] = (self.__datatypes[key], dtype)

        return fileinfo

    # requires dict lookup
    def create_filename(self, expmt_group, key, name_prefix):
        # some kind of if key in self.fileinfo.keys() catch
        file_name_raw = name_prefix + self.__datatypes[key]

        # grab the whole experimental directory
        dexpmt = self.dexpmt_dict[expmt_group]

        # create the full path name for the file
        file_path_full = os.path.join(dexpmt, key, file_name_raw)

        return file_path_full

    # Get the data files matching file_ext in this directory
    # functionally the same as the previous function but with a local scope
    def file_match(self, expmt_group, key):

        # grab the relevant fext
        fext = self.__datatypes[key]

        file_list = []

        # dexpmt_group = self.dexpmt_dict[expmt_group]
        ddata = self.dfig[expmt_group][key]

        # search the sim directory for all relevant files
        if os.path.exists(ddata):
        # if os.path.exists(dexpmt_group):
            for root, dirnames, filenames in os.walk(ddata):
            # for root, dirnames, filenames in os.walk(dexpmt_group):
                for fname in fnmatch.filter(filenames, '*'+fext):
                    file_list.append(os.path.join(root, fname))

        # sort file list? untested
        file_list.sort()

        return file_list

    # *** OLD METHODS FROM OLD SIMULATIONPATHS ***
    # grab lists of non-fig files
    # def __getfiles(self):
    #     filelists = {}
    #     for key in self.datatypes:
    #         if not key.startswith('fig'):
    #             subdir = os.path.join(self.dsim, key)
    #             fext = self.datatypes[key]
    #             filelists[key] = file_match(subdir, fext)

    #     return filelists

    # # simple path creations for figures
    # def __dfigs_create(self):
    #     return {
    #         'spikes': os.path.join(self.dsim, 'figspk'),
    #         'dipole': os.path.join(self.dsim, 'figdpl'),
    #         'spec': os.path.join(self.dsim, 'figspec'),
    #     }

    # # these are the "experiment" names (versus individual trials)
    # def __get_exp_names(self):
    #     expnames = []
    #     # Reads the unique experiment names
    #     for file in self.filelists['param']:
    #         # get the parts of the name we care about
    #         parts = file.split('/')[-1].split('.')[0].split('-')[:2]
    #         name = parts[0] + '-' + parts[1]

    #         if name not in expnames:
    #             expnames.append(name)

    #     return expnames

    def exp_files_of_type(self, datatype):
        # create dict of experiments
        d = dict.fromkeys(self.expmt_groups)

        # create file lists that match the dict keys for only files for this experiment
        # this all would be nicer with a freaking folder
        for key in d:
            d[key] = [file for file in self.filelists[datatype] if key in file.split("/")[-1]]

        return d

# Finds and moves files to created subdirectories. 
def subdir_move(dir_out, name_dir, file_pattern):
    dir_name = os.path.join(dir_out, name_dir)

    # create directories that do not exist
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    for filename in glob.iglob(os.path.join(dir_out, file_pattern)):
        shutil.move(filename, dir_name)

# currently used only minimally in epscompress
# need to figure out how to change argument list in cmd as below
def cmds_runmulti(cmdlist):
    n_threads = multiprocessing.cpu_count()
    list_runs = [cmdlist[i:i+n_threads] for i in range(0, len(cmdlist), n_threads)]

    # open devnull for writing extraneous output
    with open(os.devnull, 'w') as devnull:
        for sublist in list_runs:
            procs = [subprocess.Popen(cmd, stdout=devnull, stderr=devnull) for cmd in sublist]

            for proc in procs:
                proc.wait()

# small kernel for png optimization based on fig directory
def pngoptimize(dfig):
    local = 0
    pnglist = file_match(dfig, '.png', local)
    cmds_opti = [('optipng', pngfile) for pngfile in pnglist]
    cmds_runmulti(cmds_opti)

# list spike raster eps files and then rasterize them to HQ png files, lossless compress, 
# reencapsulate as eps, and remove backups when successful
def epscompress(dfig_spk, fext_figspk, local=0):
    cmds_gs = []
    cmds_opti = []
    cmds_encaps = []

    n_threads = multiprocessing.cpu_count()

    # lists of eps files and corresponding png files
    # fext_figspk, dfig_spk = fileinfo['figspk']
    epslist = file_match(dfig_spk, fext_figspk, local)
    pnglist = [f.replace('.eps', '.png') for f in epslist]
    epsbackuplist = [f.replace('.eps', '.bak.eps') for f in epslist]

    # create command lists for gs, optipng, and convert
    for pngfile, epsfile in it.izip(pnglist, epslist):
        cmds_gs.append(('gs -r300 -dEPSCrop -dTextAlphaBits=4 -sDEVICE=png16m -sOutputFile=%s -dBATCH -dNOPAUSE %s' % (pngfile, epsfile)))
        cmds_opti.append(('optipng', pngfile))
        cmds_encaps.append(('convert %s eps3:%s' % (pngfile, epsfile)))

    # create procs list of manageable lists and run
    runs_gs = [cmds_gs[i:i+n_threads] for i in range(0, len(cmds_gs), n_threads)]

    # run each sublist differently
    for sublist in runs_gs:
        procs_gs = [subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for cmd in sublist]
        for proc in procs_gs:
            proc.wait()

    # create optipng procs list and run
    cmds_runmulti(cmds_opti)

    # backup original eps files temporarily
    for epsfile, epsbakfile in it.izip(epslist, epsbackuplist):
        shutil.move(epsfile, epsbakfile)

    # recreate original eps files, now encapsulated, optimized rasters
    # cmds_runmulti(cmds_encaps)
    runs_encaps = [cmds_encaps[i:i+n_threads] for i in range(0, len(cmds_encaps), n_threads)]
    for sublist in runs_encaps:
        procs_encaps = [subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) for cmd in sublist]

        for proc in procs_encaps:
            proc.wait()

    # remove all of the backup files
    for epsbakfile in epsbackuplist:
        os.remove(epsbakfile)
