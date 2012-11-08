# fileio.py - general file input/output functions
#
# v 1.4.1
# rev 2012-11-07 (MS: For now, changed rawspec file type to .npz)
# last rev: (SL: strips prefixes, adds file_match to OutputDataPaths class)

import datetime, fnmatch, os, shutil, sys
import itertools as it
import subprocess

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
def strip_extprefix(filename):
    f_raw = filename.split("/")[-1]
    f = f_raw.split(".")[0].split("-")[:-1]
    ext_prefix = f.pop(0)

    for part in f:
        ext_prefix += "-%s" % part

    return ext_prefix

# Get the data files matching file_ext in this directory
def file_match(dsearch, file_ext):
    file_list = []

    if os.path.exists(dsearch):
        for root, dirnames, filenames in os.walk(dsearch):
            for fname in fnmatch.filter(filenames, '*'+file_ext):
                file_list.append(os.path.join(root, fname))

    # sort file list? untested
    file_list.sort()

    return file_list

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

# redundant with OutputDataPaths() for a little while
class SimulationPaths():
    def __init__(self, dsim):
        self.dsim = dsim

        # straight up copy from below
        self.datatypes = {
            'rawspk': '-spk.txt',
            'rawdpl': '-dpl.txt',
            'rawspec': '-spec.txt',
            'figspk': '-spk.eps',
            'figdpl': '-dpl.eps',
            'figspec': '-spec.eps',
            'param': '-param.txt'
        }
        self.filelists = self.__getfiles()
        self.dfigs = self.__dfigs_create()

    # grab lists of non-fig files
    def __getfiles(self):
        filelists = {}
        for key in self.datatypes:
            if not key.startswith('fig'):
                subdir = os.path.join(self.dsim, key)
                fext = self.datatypes[key]
                filelists[key] = file_match(subdir, fext)

        return filelists

    def __dfigs_create(self):
        return {
            'spikes': os.path.join(self.dsim, 'figspk'),
            'dipole': os.path.join(self.dsim, 'figdpl'),
            'spec': os.path.join(self.dsim, 'figspec'),
        }

# creates data dirs and a dictionary of useful types
class OutputDataPaths():
    def __init__(self, dproj, sim_prefix='test'):
        # this is the root directory of the project
        self.dproj = dproj

        # prefix for these simulations in both filenames and directory in ddate
        self.sim_prefix = sim_prefix

        # hard coded data types
        # fig extensions are not currently being used as well as they could be
        self.__datatypes = {
            'rawspk': '-spk.txt',
            'rawdpl': '-dpl.txt',
            'rawspec': '-spec.npz',
            'figspk': '-spk.eps',
            'figdpl': '-dpl.eps',
            'figspec': '-spec.eps',
            'param': '-param.txt',
        }

        # create date and sim directories if necessary
        self.ddate = self.datedir()
        self.dsim = self.simdir()

        # create dict and subdirs
        self.fileinfo = dict.fromkeys(self.__datatypes)
        self.__create_dict()

    # def move_spk(self, file_tmp_spk, file_target_spk):
    #     # dspikes = self.fileinfo['spikes'][1]
    #     if dir_check(dspikes):
    #         shutil.move(file_tmp_spk, file_target_spk)

    # Uses DirData class and returns date directory
    # this is NOT safe for midnight.
    def datedir(self):
        str_date = datetime.datetime.now().strftime("%Y-%m-%d")
        ddate = os.path.join(self.dproj, str_date)
        return ddate

    def create_dirs(self):
        for key in self.fileinfo.keys():
            dir_create(self.fileinfo[key][1])

    # simdir_create
    # creates subdirs too
    def simdir(self):
        n = 0
        self.sim_name = self.sim_prefix + '-%03d' % n
        dsim = os.path.join(self.ddate, self.sim_name)

        while dir_check(dsim):
            n += 1
            self.sim_name = self.sim_prefix + '-%03d' % n
            dsim = os.path.join(self.ddate, self.sim_name)

        return dsim

    # dictionary creation, subdir creation
    def __create_dict(self):
        for key in self.__datatypes.keys():
            # join directory name
            dtype = os.path.join(self.dsim, key)

            self.fileinfo[key] = (self.__datatypes[key], dtype)

    def create_filename(self, key, name_prefix):
        # some kind of if key in self.fileinfo.keys() catch
        file_name_raw = name_prefix + self.fileinfo[key][0]
        file_path_full = os.path.join(self.fileinfo[key][1], file_name_raw)

        return file_path_full

    # Get the data files matching file_ext in this directory
    # functionally the same as the previous function but with a local scope
    def file_match(self, key):
        fext, dsearch = self.fileinfo[key]

        file_list = []

        if os.path.exists(dsearch):
            for root, dirnames, filenames in os.walk(dsearch):
                for fname in fnmatch.filter(filenames, '*'+fext):
                    file_list.append(os.path.join(root, fname))

        # sort file list? untested
        file_list.sort()

        return file_list

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
    with open(os.devnull, 'w') as devnull:
        procs = [subprocess.Popen(cmd, stdout=devnull, stderr=devnull) for cmd in cmdlist]
        for proc in procs:
            proc.wait()

# list spike raster eps files and then rasterize them to HQ png files, lossless compress, 
# reencapsulate as eps, and remove backups when successful
def epscompress(dfig_spk, fext_figspk):
    cmds_gs = []
    cmds_opti = []
    cmds_encaps = []

    # lists of eps files and corresponding png files
    # fext_figspk, dfig_spk = fileinfo['figspk']
    epslist = file_match(dfig_spk, fext_figspk)
    pnglist = [f.replace('.eps', '.png') for f in epslist]
    epsbackuplist = [f.replace('.eps', '.bak.eps') for f in epslist]

    # create command lists for gs, optipng, and convert
    for pngfile, epsfile in it.izip(pnglist, epslist):
        cmds_gs.append(('gs -r300 -dEPSCrop -dTextAlphaBits=4 -sDEVICE=png16m -sOutputFile=%s -dBATCH -dNOPAUSE %s' % (pngfile, epsfile)))
        cmds_opti.append(('optipng', pngfile))
        cmds_encaps.append(('convert %s eps3:%s' % (pngfile, epsfile)))

    # create procs list and run
    procs_gs = [subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for cmd in cmds_gs]
    for proc in procs_gs:
        proc.wait()

    # create optipng procs list and run
    cmds_runmulti(cmds_opti)
    # procs_opti = [subprocess.Popen(cmd) for cmd in cmds_opti]
    # for proc in procs_opti:
    #     proc.wait()

    # backup original eps files temporarily
    for epsfile, epsbakfile in it.izip(epslist, epsbackuplist):
        shutil.move(epsfile, epsbakfile)

    # recreate original eps files, now encapsulated, optimized rasters
    # cmds_runmulti(cmds_encaps)
    procs_encaps = [subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) for cmd in cmds_encaps]
    for proc in procs_encaps:
        proc.wait()

    # remove all of the backup files
    for epsbakfile in epsbackuplist:
        os.remove(epsbakfile)
