# fileio.py - general file input/output functions
#
# v 1.1.1
# rev 2012-09-24 (SL: created)
# last rev:

import datetime, fnmatch, os, shutil, sys

# Cleans input files
def clean_lines(file):
    with open(file) as f_in:
        lines = (line.rstrip() for line in f_in)
        lines = [line for line in lines if line]

    return lines

def file_spike_tmp(dproj):
    file_spikes = 'spikes_tmp.spk'
    filepath_spikes = os.path.join(dproj, file_spikes)
    return filepath_spikes

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
        self.__datatypes = {
            'spikes': '.spk',
            'dipole': '.dpl',
            'fig': '.png',
            'param': '.param'
        }

        # create date and sim directories if necessary
        self.ddate = self.datedir()
        self.dsim = self.simdir()

        # create dict and subdirs
        self.fileinfo = dict.fromkeys(self.__datatypes)
        self.__create_dict()
        print self.fileinfo

    def move_spk(self, filename_spk):
        dspikes = self.fileinfo['spikes'][1]
        if dir_check(dspikes):
            shutil.move(filename_spk, dspikes)

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
        sim_name = self.sim_prefix + '-%03d' % n
        dsim = os.path.join(self.ddate, sim_name)

        while dir_check(dsim):
            n += 1
            sim_name = self.sim_prefix + '-%03d' % n
            dsim = os.path.join(self.ddate, sim_name)

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
