# paramrw.py - routines for reading the param files
#
# v 1.1.1
# rev 2012-09-26 (SL: created)
# last major:

import re
import fileio as fio

# write the params to a filename
def write(fparam, gid_list):
    with open(fparam, 'a') as f:
        for key in gid_list.keys():
            f.write('%13s ' % key)
            for gid in gid_list[key]:
                f.write('%4i ' % gid)
            f.write('\n')

# Searches f_param for any match of p
def find_param(fparam, p):
    lines = fio.clean_lines(fparam)
    param_list = [line for line in lines if line.split(': ')[0].startswith(p)]

    # return a list of tuples
    return [(param.split(': ')[0], float(param.split(': ')[1][1:-1])) for param in param_list]

def read_simgroup(fparam):
    lines = fio.clean_lines(fparam)
    param_list = [line for line in lines if line.split(': ')[0].startswith('simgroup')]

    # Assume we found something ...
    if param_list:
        return param_list[0].split(" ")[1]

    else:
        print "No simgroup found"
        return 0

# Finds the experiments list from the file
def gen_expmts(f_in):
    lines = fio.clean_lines(f_in)
    lines = [line for line in lines if line.split(': ')[0] == 'expmts']

    try:
        return lines[0].split(': ')[1][1:-1].split(', ')
    except:
        print "Couldn't get a handle on expmts"
        return 0

# Finds the changed variables
def changed_vars(sim_list):
    if len(sim_list) > 1:
        print "Have more params in here than expected. Just sayin'"

    # Strip empty lines and comments
    lines = fio.clean_lines(sim_list[0])
    lines = [line for line in lines if line[0] != '#']

    keyvals = list(line.split(": ") for line in lines)
    var_list = list(line for line in keyvals if re.match('[KL\(]', line[1][0]))
    return var_list
