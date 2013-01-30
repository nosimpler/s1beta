# paramrw.py - routines for reading the param files
#
# v 1.7.10
# rev 2013-01-30 (MS: Alpha feed weights now scale if stdev is zero)
# last major: (SL: checks for tstop inconsistencies in feeds)

import re
import fileio as fio
import numpy as np
import itertools as it
from cartesian import cartesian
from params_default import get_params_default

# reads params from a generated file and returns gid dict and p dict
def read(fparam):
    lines = fio.clean_lines(fparam)
    p = {}
    gid_dict = {}

    for line in lines:
        keystring, val = line.split(": ")
        key = keystring.strip()

        if val[0] is '[':
            val_range = val[1:-1].split(', ')

            if len(val_range) is 2:
                ind_start = int(val_range[0])
                ind_end = int(val_range[1]) + 1
                gid_dict[key] = np.arange(ind_start, ind_end)

            else:
                gid_dict[key] = np.array([])

        else:
            try:
                p[key] = float(val)
            except ValueError:
                p[key] = str(val)

    return gid_dict, p

# write the params to a filename
# now sorting
def write(fparam, p, gid_list):
    # sort the items in the dict by key
    p_sorted = [key for key in p.iteritems()]
    p_sorted.sort(key=lambda x: x[0])

    # open the file for appending
    with open(fparam, 'a') as f:
        pstring = '%26s: '

        # write the gid info first
        for key in gid_list.keys():
            f.write(pstring % key)

            if len(gid_list[key]):
                f.write('[%4i, %4i] ' % (gid_list[key][0], gid_list[key][-1]))

            else:
                f.write('[]')

            f.write('\n')

        # do the params in p_sorted
        for param in p_sorted:
            key, val = param

            f.write(pstring % key)

            if key.startswith('N_'):
                f.write('%i\n' % val)
            else:
                f.write(str(val)+'\n')

# Searches f_param for any match of p
def find_param(fparam, p):
    lines = fio.clean_lines(fparam)
    param_list = [line for line in lines if line.split(': ')[0].startswith(p)]

    # return a list of tuples
    return [(param.split(': ')[0], float(param.split(': ')[1])) for param in param_list]

# reads the simgroup name from fparam
def read_sim_prefix(fparam):
    lines = fio.clean_lines(fparam)
    param_list = [line for line in lines if line.split(': ')[0].startswith('sim_prefix')]

    # Assume we found something ...
    if param_list:
        return param_list[0].split(" ")[1]

    else:
        print "No sim_prefix found"
        return 0

# Finds the experiments list from the simulation param file (.param)
def read_expmt_groups(fparam):
    lines = fio.clean_lines(fparam)
    lines = [line for line in lines if line.split(': ')[0] == 'expmt_groups']

    try:
        return lines[0].split(': ')[1][1:-1].split(', ')

    except:
        print "Couldn't get a handle on expmts"
        return 0

# class controlling multiple simulation files (.param)
class ExpParams():
    def __init__(self, f_psim):
        self.expmt_group_params = []

        # self.prng_seedcore = {}
        # this list is simply to access these easily
        self.prng_seed_list = []

        # read in params from a file
        p_all_input = self.__read_sim(f_psim)
        self.p_template = dict.fromkeys(self.expmt_group_params)

        # create non-exp params dict from default dict
        self.__create_dict_from_default(p_all_input)

        # pop off fixed known vals
        self.sim_prefix = self.p_all.pop('sim_prefix')
        self.N_trials = int(self.p_all.pop('N_trials'))
        # self.prng_state = self.p_all.pop('prng_state')[1:-1]

        # create the list of iterated params
        self.list_params = self.__create_paramlist()
        self.N_sims = len(self.list_params[0][1])

    # reads .param file and returns p_all_input dict
    def __read_sim(self, f_psim):
        lines = fio.clean_lines(f_psim)

        # ignore comments
        lines = [line for line in lines if line[0] is not '#']
        p = {}

        for line in lines:
            # splits line by ':'
            param, val = line.split(": ")

            # sim_prefix is not a rotated variable
            # not sure why `if param is 'sim_prefix':` does not work here
            if param == 'sim_prefix':
                p[param] = str(val)

            # expmt_groups must be listed before other vals
            elif param == 'expmt_groups':
                # this list will be the preservation of the original order
                self.expmt_groups = [expmt_group for expmt_group in val[1:-1].split(', ')]

                # this dict here for easy access
                # p_group saves each of the changed params per group
                self.p_group = dict.fromkeys(self.expmt_groups)

                # create empty dicts in each
                for group in self.p_group:
                    self.p_group[group] = {}

            elif param.startswith('prng_seedcore_'):
                p[param] = int(val)
                # key = param.split('prng_seedcore_')[-1]
                # self.prng_seedcore[key] = val

                # only add values that will change
                if p[param] == -1:
                    self.prng_seed_list.append(param)

            else:
                # assign group params first
                if val[0] is '{':
                    # check for a linspace as a param!
                    if val[1] is 'L':
                        # in this case, val_range must be as long as the correct expmt_group length
                        # everything beyond that will be truncated by the izip operation below
                        # param passed will strip away the curly braces and just pass the linspace
                        val_range = self.__expand_linspace(val[1:-1])
                    else:
                        val_range = self.__expand_array(val)

                    # add the expmt_group param to the list if it's not already present
                    if param not in self.expmt_group_params:
                        self.expmt_group_params.append(param)

                    # parcel out vals to exp groups with assigned param names
                    for expmt_group, val in it.izip(self.expmt_groups, val_range):
                        self.p_group[expmt_group][param] = val

                # interpret this as a list of vals
                # type floats to a np array
                elif val[0] is '[':
                    p[param] = self.__expand_array(val)

                # interpret as a linspace
                elif val[0] is 'L':
                    p[param] = self.__expand_linspace(val)

                else:
                    try:
                        p[param] = float(val)
                    except ValueError:
                        p[param] = str(val)

        # hack-y. sorry, future
        # tstop_* = 0 is valid now, resets to the actual tstop
        # with the added bonus of saving this time to the indiv params
        for param, val in p.iteritems():
            if param.startswith('tstop_'):
                if isinstance(val, float):
                    if val == 0:
                        p[param] = p['tstop']

                elif isinstance(val, np.ndarray):
                    p[param][p[param] == 0] = p['tstop']

        return p

    # general function to expand a list of values
    def __expand_array(self, str_val):
        val_list = str_val[1:-1].split(', ')
        val_range = np.array([float(item) for item in val_list])

        return val_range

    # general function to expand the linspace
    def __expand_linspace(self, str_val):
        # strip away the leading character along with the brackets and split the csv values
        val_list = str_val[2:-1].split(', ')

        # use the values in val_list as params for np.linspace
        val_range = np.linspace(float(val_list[0]), float(val_list[1]), int(val_list[2]))

        # return the final linspace expanded
        return val_range

    # create the dict based on the default param dict
    def __create_dict_from_default(self, p_all_input):
        # create a copy of params_default through which to iterate
        self.p_all = get_params_default()

        # now find ONLY the values that are present in the supplied p_all_input
        # based on the default dict
        for key in self.p_all.keys():
            if key in p_all_input:
                # pop val off so the remaining items in p_all_input are extraneous
                self.p_all[key] = p_all_input.pop(key)

            else:
                if key not in self.expmt_group_params:
                    print "Param struct missing %s, resorting to default val" % key

        # now display extraneous keys, if there were any
        if len(p_all_input):
            print "Keys were not found in in default params: %s" % str(p_all_input.keys())

    # creates all combination of non-exp params
    def __create_paramlist(self):
        # p_all is the dict specifying all of the changing params
        plist = []

        # get all key/val pairs from the all dict
        list_sorted = [item for item in self.p_all.iteritems()]

        # sort the list by the key (alpha)
        list_sorted.sort(key=lambda x: x[0])

        # grab just the keys (but now in order)
        self.keys_sorted = [item[0] for item in list_sorted]
        self.p_template.update(dict.fromkeys(self.keys_sorted))

        # grab just the values (but now in order)
        # plist = [item[1] for item in list_sorted]
        for item in list_sorted:
            plist.append(item[1])

        vals_all = cartesian(plist)
        return zip(self.keys_sorted, vals_all.transpose())

    # return pdict based on that one value, PLUS append the p_ext here ... yes, hack-y
    def return_pdict(self, expmt_group, i):
        # p_template was always updated to include the ones from exp and others
        p_sim = dict.fromkeys(self.p_template)

        # go through params in list_params
        for param, val_list in self.list_params:
            if param.startswith('prng_seedcore_'):
                p_sim[param] = int(val_list[i])
            else:
                p_sim[param] = val_list[i]

        # go through the expmt group-based params
        for param, val in self.p_group[expmt_group].iteritems():
            p_sim[param] = val

        return p_sim

    # Find keys that change anytime during simulation
    # (i.e. have more than one associated value)
    def get_key_types(self):
        key_dict = {
            'dynamic_keys': [],
            'static_keys': [],
        }

        # Save expmt keys as dynamic keys
        key_dict['dynamic_keys'] = self.expmt_group_params

        # Find keys that change run to run within experiments
        for key in self.p_all.keys():
            # if key has length associated with it, must change run to run
            try:
                len(self.p_all[key])

                # Before storing key, check to make sure it has not already been stored
                if key not in key_dict['dynamic_keys']:
                    key_dict['dynamic_keys'].append(key)

            except TypeError:
                key_dict['static_keys'].append(key)

        return key_dict

# qnd function to add feeds if they are sensible
# whips into shape ones that are not
# could be properly made into a meaningful class.
def feed_validate(p_ext, d, tstop):
    # only append if t0 is less than simulation tstop
    if tstop > d['t0']:
        # # reset tstop if the specified tstop exceeds the
        # # simulation runtime
        # if d['tstop'] == 0:
        #     d['tstop'] = tstop

        if d['tstop'] > tstop:
            # print "Warning: input parameter tstop exceeds value of simulation run. Resetting."
            d['tstop'] = tstop

        # if stdev is zero, increase synaptic weights 10 fold to make single input equivalent to 10 simultaneous inputs
        if not d['stdev']:
            for key in d.keys():
                if key.endswith('Pyr'):
                    d[key] = (d[key][0] * 5., d[key][1])

                elif key.endswith('Basket'):
                    d[key] = (d[key][0] * 5., d[key][1])

        p_ext.append(d)

    return p_ext

# creates the external feed params based on individual simulation params p
def create_pext(p, tstop):
    # indexable py list of param dicts for parallel
    # turn off individual feeds by commenting out relevant line here.
    # always valid, no matter the length
    p_ext = []

    # p_unique is a dict of input param types that end up going to each cell uniquely
    p_unique = {}

    # default params
    feed_prox = {
        'f_input': p['f_input_prox'],
        't0': p['t0_input_prox'],
        'tstop': p['tstop_input_prox'],
        'stdev': p['f_stdev_prox'],
        'L2Pyr': (p['input_prox_A_weight_pyr'], p['input_prox_A_delay_L2']),
        'L5Pyr': (p['input_prox_A_weight_pyr'], p['input_prox_A_delay_L5']),
        'L2Basket': (p['input_prox_A_weight_inh'], p['input_prox_A_delay_L2']),
        'L5Basket': (p['input_prox_A_weight_inh'], p['input_prox_A_delay_L5']),
        'prng_seedcore': int(p['prng_seedcore_input_prox']),
        'lamtha': 100.,
        'loc': 'proximal',
    }

    # ensures time interval makes sense
    p_ext = feed_validate(p_ext, feed_prox, tstop)

    feed_dist = {
        'f_input': p['f_input_dist'],
        't0': p['t0_input_dist'],
        'tstop': p['tstop_input_dist'],
        'stdev': p['f_stdev_dist'],
        'L2Pyr': (p['input_dist_A_weight_pyr'], p['input_dist_A_delay_L2']),
        'L5Pyr': (p['input_dist_A_weight_pyr'], p['input_dist_A_delay_L5']),
        'L2Basket': (p['input_dist_A_weight_inh'], p['input_dist_A_delay_L2']),
        'prng_seedcore': int(p['prng_seedcore_input_dist']),
        'lamtha': 100.,
        'loc': 'distal',
    }

    p_ext = feed_validate(p_ext, feed_dist, tstop)

    # Create evoked response parameters
    # f_input needs to be defined as 0
    # these vals correspond to non-perceived max 
    # conductance threshold in uS (Jones et al. 2007)
    p_unique['evprox0'] = {
        't0': p['t_evprox_early'],
        'L2_pyramidal': (p['gbar_evprox_early_L2Pyr'], 0.1, p['sigma_t_evprox_early']),
        'L5_pyramidal': (p['gbar_evprox_early_L5Pyr'], 1., p['sigma_t_evprox_early']),
        'L2_basket': (p['gbar_evprox_early_L2Basket'], 0.1, p['sigma_t_evprox_early']),
        'L5_basket': (p['gbar_evprox_early_L5Basket'], 1., p['sigma_t_evprox_early']),
        'prng_seedcore': int(p['prng_seedcore_evprox_early']),
        'lamtha_space': 3.,
        'loc': 'proximal'
    }

    p_unique['evprox1'] = {
        't0': p['t_evprox_late'],
        'L2_pyramidal': (p['gbar_evprox_late_L2Pyr'], 0.1, p['sigma_t_evprox_late']),
        'L5_pyramidal': (p['gbar_evprox_late_L5Pyr'], 5., p['sigma_t_evprox_late']),
        'L2_basket': (p['gbar_evprox_late_L2Basket'], 0.1, p['sigma_t_evprox_late']),
        'L5_basket': (p['gbar_evprox_late_L5Basket'], 5., p['sigma_t_evprox_late']),
        'prng_seedcore': int(p['prng_seedcore_evprox_late']),
        'lamtha_space': 3.,
        'loc': 'proximal'
    }

    p_unique['evdist'] = {
        't0': p['t_evdist'],
        'L2_pyramidal': (p['gbar_evdist_L2Pyr'], 0.1, p['sigma_t_evdist']),
        'L5_pyramidal': (p['gbar_evdist_L5Pyr'], 0.1, p['sigma_t_evdist']),
        'L2_basket': (p['gbar_evdist_L2Basket'], 0.1, p['sigma_t_evdist']),
        'prng_seedcore': int(p['prng_seedcore_evdist']),
        'lamtha_space': 3.,
        'loc': 'distal'
    }

    # this needs to create many feeds
    # (amplitude, delay, mu, sigma). ordered this way to preserve compatibility
    p_unique['extgauss'] = {
        'stim': 'gaussian',
        'L2_basket': (p['L2Basket_Gauss_A_weight'], 1., p['L2Basket_Gauss_mu'], p['L2Basket_Gauss_sigma']),
        'L2_pyramidal': (p['L2Pyr_Gauss_A_weight'], 0.1, p['L2Pyr_Gauss_mu'], p['L2Pyr_Gauss_sigma']),
        'L5_basket': (p['L5Basket_Gauss_A_weight'], 1., p['L5Basket_Gauss_mu'], p['L5Basket_Gauss_sigma']),
        'L5_pyramidal': (p['L5Pyr_Gauss_A_weight'], 1., p['L5Pyr_Gauss_mu'], p['L5Pyr_Gauss_sigma']),
        'lamtha': 100.,
        'prng_seedcore': int(p['prng_seedcore_extgauss']),
        'loc': 'proximal'
    }

    # Poisson distributed inputs to proximal
    p_unique['extpois'] = {
        'stim': 'poisson',
        'L2_basket': (p['L2Basket_Pois_A_weight'], 1., p['L2Basket_Pois_lamtha']),
        'L2_pyramidal': (p['L2Pyr_Pois_A_weight'], 0.1, p['L2Pyr_Pois_lamtha']),
        'L5_basket': (p['L5Basket_Pois_A_weight'], 1., p['L5Basket_Pois_lamtha']),
        'L5_pyramidal': (p['L5Pyr_Pois_A_weight'], 1., p['L5Pyr_Pois_lamtha']),
        'lamtha_space': 100.,
        'prng_seedcore': int(p['prng_seedcore_extpois']),
        't_interval': (0., p['pois_T']),
        'loc': 'proximal'
    }

    return p_ext, p_unique

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
