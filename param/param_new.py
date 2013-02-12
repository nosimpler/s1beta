# param_new.py - simple function to make sure all param files 
# here contain all necessary keys
# should be self-contained
#
# v 1.7.13
# rev 2013-01-31 (SL: created)
# last major:

import os, fnmatch, shutil, sys

# get just the pure lines from the file
# possibly obsolete already
def purelines(f_param):
    with open(f_param) as f_in:
        lines = (line.rstrip() for line in f_in)
        lines = [line for line in lines]

    return lines

# create dict from a raw list, assumed to be from purelines or equivalent
def dict_from_lines(l):
    # create a param dict
    d = {}

    # remove empty lines and comments
    l = [line for line in l if line]
    l = [line for line in l if line[0] is not '#']

    # populate dict
    for line in l:
        param, val = line.split(": ")
        d[param] = val

    return d

# create a list of files by type
def create_file_list(ext_pattern, exclude_list=[]):
    flist = []

    # all the param filenames
    for root, dnames, fnames in os.walk('.'):
        for fname in fnmatch.filter(fnames, ext_pattern):
        # for fname in fnmatch.filter(fnames, '*.param'):
            flist.append(fname)

    flist = [f for f in flist if f not in exclude_list]
    
    return flist

# check to find missing params
def check_missing(write_mode='p'):
    # default file name
    f_default = 'default.param'

    flist = create_file_list('*.param', [f_default])

    # clean lines of f_default
    l_default = purelines(f_default)
    d_default = dict_from_lines(l_default)

    # now do similar for each other file in the set
    for f_param in flist:
        # create a backup file
        f_backup = f_param+'.bak'
        shutil.copyfile(f_param, f_backup)

        # get the pure lines (to be written back later)
        l_param = purelines(f_param)

        # make its own dict
        d_param = dict_from_lines(l_param)

        # find the missing params here
        params_missing = list(set(d_default) - set(d_param))

        if write_mode == 'a':
            if params_missing:
                # for param in params_missing:
                #     print '%s: %s' % (param, d_default[param])
                with open(f_param, 'a') as f:
                    f.write('\n# new params from default\n')
                    for param in params_missing:
                        f.write('%s: %s\n' % (param, d_default[param]))

        elif write_mode == 'p':
            print f_param
            prettyprint(params_missing)
            raw_input("Press <enter> to continue ...")

# prints from an iterable
def prettyprint(l):
    for item in l:
        print item

# restores bak files to original
# this is a destructive operation
def restore():
    baklist = create_file_list('*.bak', exclude_list=[])
    p_list = create_file_list('*.param', exclude_list=['default.param'])

    # no originals list
    bak_only = []

    # confirm!
    confirm_str = raw_input('Are you sure you want to try and restore bak files to param files [y/n]? ')

    if confirm_str == 'y':
        # restore the files
        if bak_list:
            for f_bak in baklist:
                # remove bak extension
                f_orig = f_bak[:-4]

                if f_orig in p_list:
                    shutil.move(f_bak, f_orig)
                else:
                    bak_only.append(f_bak)

    else:
        print "Yeah, didn't think so. Have a nice day."

    # show off the ones we didn't have
    if bak_only:
        print "Could not find these files:"
        prettyprint(bak_only)

# removes bak files
def remove_bak():
    baklist = create_file_list('*.bak', exclude_list=[])

    # confirm!
    confirm_str = raw_input('Are you sure you want to REMOVE bak files [y/n]? ')
    if confirm_str == 'y':
        if baklist:
            for f_bak in baklist:
                os.remove(f_bak)

    else:
        if baklist:
            print "You saved us:"
            prettyprint(baklist)
        print "Better to think twice than to make a fatal mistake once."

if __name__ == '__main__':
    try:
        operation_mode = sys.argv[1]
    except IndexError:
        operation_mode = 'check'

    if operation_mode == 'restore':
        restore()

    elif operation_mode == 'clean':
        remove_bak()

    elif operation_mode == 'check':
        check_missing('p')

    elif operation_mode == 'append':
        check_missing('a')

    else:
        print "Not a valid option"
