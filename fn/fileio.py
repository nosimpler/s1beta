# fileio.py - general file input/output functions
#
# v 1.2.27
# rev 2012-11-03 (SL: makes better eps and png files in spikes, but not separated yet)
# last rev: (SL: png to eps in the unused fig filename extensions)

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

# Get the data files matching file_ext in this directory
def file_match(dict_fileinfo, key):
    dsearch = dict_fileinfo[key][1]
    file_ext = '*'+dict_fileinfo[key][0]

    file_list = []
    if os.path.exists(dsearch):
        for root, dirnames, filenames in os.walk(dsearch):
            for fname in fnmatch.filter(filenames, file_ext):
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
            'spikes': '-spk.txt',
            'dipole': '-dpl.txt',
            'figspk': '-spk.eps',
            'figdpl': '-dpl.eps',
            'figspec': '-spec.eps',
            'param': '-param.txt'
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
def epscompress(fileinfo):
    cmds_gs = []
    cmds_opti = []
    cmds_encaps = []

    # lists of eps files and corresponding png files
    epslist = file_match(fileinfo, 'figspk')
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
