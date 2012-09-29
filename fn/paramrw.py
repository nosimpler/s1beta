# paramrw.py - routines for reading the param files
#
# v 1.2.3
# rev 2012-09-29 (SL: param creation)
# last major: (SL: writes more params)

import re
import fileio as fio
from cartesian import cartesian

# write the params to a filename
def write(fparam, p, p_ext, gid_list):
    with open(fparam, 'a') as f:
        for key in gid_list.keys():
            f.write('%13s: ' % key)
            for gid in gid_list[key]:
                f.write('%4i ' % gid)
            f.write('\n')

        for key in p.keys():
            f.write('%13s: ' % key)

            if key.startswith('N_'):
                f.write('%i\n' % p[key])
            else:
                f.write(str(p[key])+'\n')
                # f.write('%d\n' % p[key])

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

class exp_params():
    def __init__(self, p_all):
        self.p_all = p_all
        # pop off the value for sim_prefix. then continue
        self.sim_prefix = self.p_all.pop('sim_prefix')
        self.list_params = self.__create_paramlist()
        self.N_sims = len(self.list_params[0][1])

    def __create_paramlist(self):
        # p_all is the dict specifying all of the changing params
        plist = []

        # get all key/val pairs from the all dict
        list_sorted = [item for item in self.p_all.iteritems()]

        # sort the list by the key (alpha)
        list_sorted.sort(key=lambda x: x[0])

        # grab just the keys (but now in order)
        self.keys_sorted = [item[0] for item in list_sorted]
        self.p_template = dict.fromkeys(self.keys_sorted)

        # grab just the values (but now in order)
        for item in list_sorted:
            plist.append(item[1])

        vals_all = cartesian(plist)
        return zip(self.keys_sorted, vals_all.transpose())

    def return_pdict(self, i):
        p_sim = dict.fromkeys(self.p_template)
        for param in self.list_params:
            p_sim[param[0]] = param[1][i]

        return p_sim

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
