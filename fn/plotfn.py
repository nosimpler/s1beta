# plotfn.py - pall and possibly other plot routines
#
# v 1.6.16af
# rev 2013-01-14 (MS: Added plot routine and kernel to plot dpl and spec with alpha feed hist)
# last major: (MS: Updated debug routine to plot all data at once instead of per exmpt)

from pdipole import pdipole, pdipole_with_hist
from spec import pspec, pspec_with_hist
from praster import praster
import paramrw
import itertools as it
import fileio as fio
import itertools as it
from multiprocessing import Pool

# terrible handling of variables
def pkernel(dfig, f_param, f_spk, f_dpl, data_spec, key_types):
    gid_dict, p_dict = paramrw.read(f_param)
    tstop = p_dict['tstop']

    # fig dirs
    dfig_dpl = dfig['figdpl']
    dfig_spec = dfig['figspec']
    dfig_spk = dfig['figspk']

    # plot kernels
    praster(gid_dict, tstop, f_spk, dfig_spk)
    pdipole(f_dpl, dfig_dpl, p_dict, key_types)
    pspec(data_spec, f_dpl, dfig_spec, p_dict, key_types)

    return 0

# Kernel for plotting dipole and spec with alpha feed histograms
def pkernel_with_hist(dfig, f_param, f_spk, f_dpl, data_spec, key_types):
    gid_dict, p_dict = paramrw.read(f_param)
    tstop = p_dict['tstop']

    # fig dirs
    dfig_dpl = dfig['figdpl']
    dfig_spec = dfig['figspec']
    dfig_spk = dfig['figspk']

    # plot kernels
    pdipole_with_hist(f_dpl, f_spk, dfig_dpl, p_dict, gid_dict, key_types)
    pspec_with_hist(data_spec, f_dpl, f_spk, dfig_spec, p_dict, gid_dict, key_types)

    return 0

# r is the value returned by pkernel
# this is sort of a dummy function
def cb(r):
    pass

# plot function - this is sort of a stop-gap and shouldn't live here, really
# reads all data except spec and gid_dict from files
def pall(ddir, p_exp, spec_results):
    # runtype allows easy (hard coded switching between two modes)
    runtype = 'parallel'

    # create giant list of appropriate files and run them all at the same time
    if runtype is 'parallel':
        dsim = ddir.dsim

        key_types = p_exp.get_key_types()

        # preallocate lists for use below
        param_list = []
        dpl_list = []
        spk_list = []
        dfig_list = []

        # agregate all file types from individual expmts into lists 
        for expmt_group in ddir.expmt_groups:
            # these should be equivalent lengths
            param_list.extend(ddir.file_match(expmt_group, 'param'))
            dpl_list.extend(ddir.file_match(expmt_group, 'rawdpl'))
            spk_list.extend(ddir.file_match(expmt_group, 'rawspk'))

            # append as many copies of epxt dfig dict as there were runs in expmt 
            for i in range(len(ddir.file_match(expmt_group, 'param'))):
                dfig_list.append(ddir.dfig[expmt_group])

        # apply async to compiled lists
        pl = Pool()
        for dfig, f_param, f_spk, f_dpl, data_spec in it.izip(dfig_list, param_list, spk_list, dpl_list, spec_results):
            pl.apply_async(pkernel, (dfig, f_param, f_spk, f_dpl, data_spec, key_types), callback=cb)

        pl.close()
        pl.join()

    elif runtype is 'debug':
        dsim = ddir.dsim

        key_types = p_exp.get_key_types()

        # preallocate lists for use below
        param_list = []
        dpl_list = []
        spk_list = []
        dfig_list = []

        # agregate all file types from individual expmts into lists 
        for expmt_group in ddir.expmt_groups:
            # these should be equivalent lengths
            param_list.extend(ddir.file_match(expmt_group, 'param'))
            dpl_list.extend(ddir.file_match(expmt_group, 'rawdpl'))
            spk_list.extend(ddir.file_match(expmt_group, 'rawspk'))

            # append as many copies of epxt dfig dict as there were runs in expmt 
            for i in range(len(ddir.file_match(expmt_group, 'param'))):
                dfig_list.append(ddir.dfig[expmt_group])

        # apply async to compiled lists
        for dfig, f_param, f_spk, f_dpl, data_spec in it.izip(dfig_list, param_list, spk_list, dpl_list, spec_results):
           pkernel(dfig, f_param, f_spk, f_dpl, data_spec, key_types)

# Plots dipole and spec with alpha feed histograms
def pdpl_pspec_with_hist(ddir, p_exp, spec_results):
    # preallocate lists for use below
    param_list = []
    dpl_list = []
    spk_list = []
    dfig_list = []

    # Grab all necessary data in aggregated lists
    for expmt_group in ddir.expmt_groups:
        # these should be equivalent lengths
        param_list.extend(ddir.file_match(expmt_group, 'param'))
        dpl_list.extend(ddir.file_match(expmt_group, 'rawdpl'))
        spk_list.extend(ddir.file_match(expmt_group, 'rawspk'))

        # append as many copies of epxt dfig dict as there were runs in expmt 
        for i in range(len(ddir.file_match(expmt_group, 'param'))):
            dfig_list.append(ddir.dfig[expmt_group])

    key_types = p_exp.get_key_types()

    # apply async to compiled lists
    pl = Pool()
    for dfig, f_param, f_spk, f_dpl, data_spec in it.izip(dfig_list, param_list, spk_list, dpl_list, spec_results):
        pl.apply_async(pkernel_with_hist, (dfig, f_param, f_spk, f_dpl, data_spec, key_types), callback=cb)

    pl.close()
    pl.join()

#         # run each experiment separately
#         for expmt_group in ddir.expmt_groups:
#             spec_results_expmt = [spec_result for spec_result in spec_results if expmt_group in spec_result.name]
# 
#             # these should be equivalent lengths
#             param_list = ddir.file_match(expmt_group, 'param')
#             dpl_list = ddir.file_match(expmt_group, 'rawdpl')
#             spk_list = ddir.file_match(expmt_group, 'rawspk')
# 
#             # print ddir.dfig
#             dfig = ddir.dfig[expmt_group]
# 
#             for f_param, f_spk, f_dpl, data_spec in it.izip(param_list, spk_list, dpl_list, spec_results_expmt):
#                 pkernel(dfig, f_param, f_spk, f_dpl, data_spec, key_types)
