# paramrw.py - routines for reading the param files
#
# v 1.2.24a
# rev 2012-11-01 (MS: Fixed bug creating p_ext in exp_params())
# last major: (MS: Added get_key_types() in exp_params() to find keys whose values change over runs)

import re
import fileio as fio
from cartesian import cartesian
from params_default import params_default

# write the params to a filename
def write(fparam, p, p_ext, gid_list):
    with open(fparam, 'a') as f:
        pstring = '%22s: '

        for key in gid_list.keys():
            f.write(pstring % key)
            # f.write('%13s: ' % key)

            if len(gid_list[key]):
                f.write('[%4i, %4i] ' % (gid_list[key][0], gid_list[key][-1]))

            else:
                f.write('[]')

            # for gid in gid_list[key]:
            #     f.write('%4i ' % gid)
            f.write('\n')

        for key in p.keys():
            f.write(pstring % key)

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
    def __init__(self, p_all_input):
        self.__create_dict_from_default(p_all_input)

        # pop off the value for sim_prefix. then continue
        self.sim_prefix = self.p_all.pop('sim_prefix')
        self.list_params = self.__create_paramlist()
        self.N_sims = len(self.list_params[0][1])

    # create the dict based on the default param dict
    def __create_dict_from_default(self, p_all_input):
        # create a copy of params_default through which to iterate
        self.p_all = params_default

        # now find ONLY the values that are present in the supplied p_all_input
        # based on the default dict
        for key in self.p_all.keys():
            if key in p_all_input:
                # pop val off so the remaining items in p_all_input are extraneous
                self.p_all[key] = p_all_input.pop(key)
                # self.p_all[key] = p_all_input[key]
            else:
                print "Param struct missing %s, resorting to default val" % key

        # now display extraneous keys, if there were any
        if len(p_all_input):
            print "Keys were not found in in default params: %s" % str(p_all_input.keys())

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

    # return pdict based on that one value, PLUS append the p_ext here ... yes, hack-y
    def return_pdict(self, i):
        p_sim = dict.fromkeys(self.p_template)
        for param in self.list_params:
            p_sim[param[0]] = param[1][i]

        return p_sim

    # Find keys that change run to run (i.e. have more than one associated value)
    def get_key_types(self):
        key_dict = {
                    'dynamic_keys': [],
                    'static_keys': [],
                   }

        for key in self.p_all.keys():
            try:
                len(self.p_all[key])
                key_dict['dynamic_keys'].append(key)

            except TypeError:
                key_dict['static_keys'].append(key)
                # static_keys.append(key)

        return key_dict

# qnd function to just add feeds based on tstop
# could be properly made into a meaningful class.
def feed_validate(p_ext, d, tstop):
    if tstop > d['t0']:
        p_ext.append(d)

    return p_ext

# creates the external feed params based on individual simulation params p
def create_pext(p, tstop):
    # indexable py list of param dicts for parallel
    # turn off individual feeds by commenting out relevant line here.
    # always valid, no matter the length
    p_ext = []

    # default params
    feed_prox = {
        'f_input': p['f_input_prox'],
        't0': p['t0_input'],
        # 't0': 150.,
        'L2Pyr': (4e-5, 0.1),
        'L5Pyr': (4e-5, 1.),
        'L2Basket': (8e-5, 0.1),
        'L5Basket': (8e-5, 1.),
        'lamtha': 100.,
        'loc': 'proximal'
    }

    p_ext = feed_validate(p_ext, feed_prox, tstop)

    feed_dist = {
        'f_input': p['f_input_dist'],
        't0': p['t0_input'],
        # 't0': 150.,
        'L2Pyr': (4e-5, 5.),
        'L5Pyr': (4e-5, 5.),
        'L2Basket': (4e-5, 5.),
        'lamtha': 100.,
        'loc': 'distal'
    }

    p_ext = feed_validate(p_ext, feed_dist, tstop)

    # Create evoked response parameters
    # f_input needs to be defined as 0
    evoked_prox_early = {
        'f_input': 0.,
        't0': p['t_evoked_prox_early'],
        # 't0': 454.,
        'L2Pyr': (1e-3, 0.1),
        'L5Pyr': (5e-4, 1.),
        'L2Basket': (2e-3, 0.1),
        'L5Basket': (1e-3, 1.),
        'lamtha': 3.,
        'loc': 'proximal'
    }

    p_ext = feed_validate(p_ext, evoked_prox_early, tstop)

    evoked_prox_late = {
        'f_input': 0.,
        't0': p['t_evoked_prox_late'],
        # 't0': 564.,
        'L2Pyr': (6.89e-3, 0.1),
        'L5Pyr': (3.471e-3, 5.),
        'L2Basket': (6.89e-3, 0.1),
        'L5Basket': (3.471e-3, 5.),
        'lamtha': 3.,
        'loc': 'proximal'
    }

    p_ext = feed_validate(p_ext, evoked_prox_late, tstop)

    evoked_dist = {
        'f_input': 0.,
        't0': p['t_evoked_dist'],
        # 't0': 499.,
        'L2Pyr': (1.05e-3, 0.1),
        'L5Pyr': (1.05e-3, 0.1),
        'L2Basket': (5.02e-4, 0.1),
        'lamtha': 3.,
        'loc': 'distal'
    }

    p_ext = feed_validate(p_ext, evoked_dist, tstop)

    # this needs to create many feeds
    # (amplitude, delay, mu, sigma). ordered this way to preserve compatibility
    p_ext_gauss = {
        'stim': 'gaussian',
        'L2_basket': (p['L2Basket_Gauss_A'], 1., p['L2Basket_Gauss_mu'], p['L2Basket_Gauss_sigma']),
        'L2_pyramidal': (p['L2Pyr_Gauss_A'], 0.1, p['L2Pyr_Gauss_mu'], p['L2Pyr_Gauss_sigma']),
        'L5_basket': (p['L5Basket_Gauss_A'], 1., p['L5Basket_Gauss_mu'], p['L5Basket_Gauss_sigma']),
        'L5_pyramidal': (p['L5Pyr_Gauss_A'], 1., p['L5Pyr_Gauss_mu'], p['L5Pyr_Gauss_sigma']),
        'lamtha': 100.,
        'loc': 'proximal'
    }

    # indexable py list of param dicts for parallel
    # turn off individual feeds by commenting out relevant line here.
    # always valid, no matter the length
    # p_ext = [
    #     # feed_prox,
    #     # feed_dist,
    #     # evoked_prox_early,
    #     # evoked_prox_late,
    #     # evoked_dist
    # ]

    return p_ext, p_ext_gauss

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
