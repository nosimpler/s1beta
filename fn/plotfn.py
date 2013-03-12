# plotfn.py - pall and possibly other plot routines
#
# v 1.7.31
# rev 2013-03-12 (MS: method for creating spectrogram aggregate fig)
# last major: (MS: spec now specfn)

from pdipole import pdipole, pdipole_with_hist
from praster import praster
from axes_create import AggregateSpecWithHist
import paramrw
import specfn
import os
import itertools as it
import fileio as fio
import itertools as it
from multiprocessing import Pool

# terrible handling of variables
def pkernel(dfig, f_param, f_spk, f_dpl, data_spec, key_types, xlim=[0, 'tstop']):
    gid_dict, p_dict = paramrw.read(f_param)
    tstop = p_dict['tstop']

    # fig dirs
    dfig_dpl = dfig['figdpl']
    dfig_spec = dfig['figspec']
    dfig_spk = dfig['figspk']

    pdipole_dict = {
        'xmin': xlim[0],
        'xmax': xlim[1],
        'ymin': None,
        'ymax': None,
    }

    # plot kernels
    praster(gid_dict, tstop, f_spk, dfig_spk)
    pdipole(f_dpl, dfig_dpl, p_dict, key_types, pdipole_dict)
    # pdipole(f_dpl, dfig_dpl, p_dict, key_types, xlim)
    specfn.pspec(data_spec, f_dpl, dfig_spec, p_dict, key_types, xlim)

    return 0

# Kernel for plotting dipole and spec with alpha feed histograms
def pkernel_with_hist(dfig, f_param, f_spk, f_dpl, data_spec, key_types, xlim=[0., 'tstop']):
    gid_dict, p_dict = paramrw.read(f_param)
    tstop = p_dict['tstop']

    # fig dirs
    dfig_dpl = dfig['figdpl']
    dfig_spec = dfig['figspec']
    dfig_spk = dfig['figspk']

    # plot kernels
    pdipole_with_hist(f_dpl, f_spk, dfig_dpl, p_dict, gid_dict, key_types, xlim)
    specfn.pspec_with_hist(data_spec, f_dpl, f_spk, dfig_spec, p_dict, gid_dict, key_types, xlim)

    return 0

# r is the value returned by pkernel
# this is sort of a dummy function
def cb(r):
    pass

# plot function - this is sort of a stop-gap and shouldn't live here, really
# reads all data except spec and gid_dict from files
def pall(ddir, p_exp, spec_results, xlim=[0., 'tstop']):
    # runtype allows easy (hard coded switching between two modes)
    # either 'parallel' or 'debug'
    runtype = 'parallel'
    # runtype = 'debug'

    # create giant list of appropriate files and run them all at the same time
    if runtype is 'parallel':
        dsim = ddir.dsim

        key_types = p_exp.get_key_types()

        # preallocate lists for use below
        param_list = []
        dpl_list = []
        spk_list = []
        dfig_list = []

        # aggregate all file types from individual expmts into lists
        for expmt_group in ddir.expmt_groups:
            # these should be equivalent lengths
            param_list.extend(ddir.file_match(expmt_group, 'param'))
            dpl_list.extend(ddir.file_match(expmt_group, 'rawdpl'))
            spk_list.extend(ddir.file_match(expmt_group, 'rawspk'))

            # append as many copies of expmt dfig dict as there were runs in expmt
            for i in range(len(ddir.file_match(expmt_group, 'param'))):
                dfig_list.append(ddir.dfig[expmt_group])

        # apply async to compiled lists
        pl = Pool()
        for dfig, f_param, f_spk, f_dpl, data_spec in it.izip(dfig_list, param_list, spk_list, dpl_list, spec_results):
            pl.apply_async(pkernel, (dfig, f_param, f_spk, f_dpl, data_spec, key_types, xlim), callback=cb)

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
           pkernel(dfig, f_param, f_spk, f_dpl, data_spec, key_types, xlim)

# Plots dipole and spec with alpha feed histograms
def pdpl_pspec_with_hist(ddir, p_exp, spec_results, xlim=[0., 'tstop']):
    runtype = 'parallel'

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

        # append as many copies of expmt dfig dict as there were runs in expmt
        for i in range(len(ddir.file_match(expmt_group, 'param'))):
            dfig_list.append(ddir.dfig[expmt_group])

    # grab the key types
    key_types = p_exp.get_key_types()

    if runtype is 'parallel':
        # apply async to compiled lists
        pl = Pool()
        for dfig, f_param, f_spk, f_dpl, data_spec in it.izip(dfig_list, param_list, spk_list, dpl_list, spec_results):
            pl.apply_async(pkernel_with_hist, (dfig, f_param, f_spk, f_dpl, data_spec, key_types, xlim), callback=cb)

        pl.close()
        pl.join()

    elif runtype is 'debug':
        for dfig, f_param, f_spk, f_dpl, data_spec in it.izip(dfig_list, param_list, spk_list, dpl_list, spec_results):
            pkernel_with_hist(dfig, f_param, f_spk, f_dpl, data_spec, key_types, xlim)

def aggregate_spec_with_hist(ddir, p_exp, spec_results, labels):
    runtype = 'debug'

    # preallocate lists for use below
    param_list = []
    dpl_list = []
    spk_list = []
    dfig_list = []
    spec_list = spec_results

    # Get dimensions for aggregate fig
    N_rows = len(ddir.expmt_groups)
    N_cols = len(ddir.file_match(ddir.expmt_groups[0], 'param'))

    # Create figure
    f = AggregateSpecWithHist(N_rows, N_cols)

    # Grab all necessary data in aggregated lists
    for expmt_group in ddir.expmt_groups:
        # these should be equivalent lengths
        param_list.extend(ddir.file_match(expmt_group, 'param'))
        dpl_list.extend(ddir.file_match(expmt_group, 'rawdpl'))
        spk_list.extend(ddir.file_match(expmt_group, 'rawspk'))

    # apply async to compiled lists
    if runtype is 'parallel':
        print 'yay'
        pl = Pool()
        for f_param, f_spk, f_dpl, dspec, ax in it.izip(param_list, spk_list, dpl_list, spec_list, f.ax_list):
            gid_dict, p_dict = paramrw.read(f_param)
            pl.apply_async(specfn.aggregate_with_hist, (f, ax, dspec, f_dpl, f_spk, p_dict, gid_dict))

        pl.close()
        pl.join()
        
    elif runtype is 'debug':
        for f_param, f_spk, f_dpl, dspec, ax in it.izip(param_list, spk_list, dpl_list, spec_list, f.ax_list):
            gid_dict, p_dict = paramrw.read(f_param)
            specfn.aggregate_with_hist(f, ax, dspec, f_dpl, f_spk, p_dict, gid_dict)

    # add row labels
    f.add_row_labels(param_list, labels[0])

    # add column labels
    f.add_column_labels(param_list, labels[1])

    fig_name = os.path.join(ddir.dsim, 'aggregate_hist.png')
    f.save(fig_name)
    f.close()
