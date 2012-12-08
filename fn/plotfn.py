# plotfn.py - pall and possibly other plot routines
#
# v 1.5.1
# rev 2012-12-08 (SL: simplified pall)
# last major: (SL/MS: fixed spec with expmts)

from pdipole import pdipole
from spec import pspec
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
    pspec(data_spec, dfig_spec, p_dict, key_types)

    return 0

# r is the value returned by pkernel
# this is sort of a dummy function
def cb(r):
    pass

# plot function - this is sort of a stop-gap and shouldn't live here, really
# reads all data except spec and gid_dict from files
def pall(ddir, p_exp, spec_results):
# def pall(ddir, p_exp, gid_dict, tstop):
    # runtype allows easy (hard coded switching between two modes)
    runtype = 'parallel'

    # create giant list of appropriate files and run them all at the same time
    if runtype is 'parallel':
        dsim = ddir.dsim

        key_types = p_exp.get_key_types()

        # run each experiment separately
        for expmt_group in ddir.expmt_groups:
            spec_results_expmt = [spec_result for spec_result in spec_results if expmt_group in spec_result.name]

            # these should be equivalent lengths
            param_list = ddir.file_match(expmt_group, 'param')
            dpl_list = ddir.file_match(expmt_group, 'rawdpl')
            spk_list = ddir.file_match(expmt_group, 'rawspk')

            # print ddir.dfig
            dfig = ddir.dfig[expmt_group]

            pl = Pool()
            for f_param, f_spk, f_dpl, data_spec in it.izip(param_list, spk_list, dpl_list, spec_results_expmt):
                pl.apply_async(pkernel, (dfig, f_param, f_spk, f_dpl, data_spec, key_types), callback=cb)

            pl.close()
            pl.join()

    elif runtype is 'debug':
        # This is largely broken at the moment and not maintained
        # so the comments are preserved. However when it is useful again, these lines are a good guide
        pass

        # dict_list = [p_exp.return_pdict(i) for i in range(p_exp.N_sims)]
        # fext_dpl, ddpl = ddir.fileinfo['rawdpl']
        # fext_spk, dspk = ddir.fileinfo['rawspk']
        # fext_spec, dspec = ddir.fileinfo['rawspec']
        # fext_param, dparam = ddir.fileinfo['param']

        # dpl_list = fio.file_match(ddpl, fext_dpl)
        # spk_list = fio.file_match(dspk, fext_spk)
        # spec_list = fio.file_match(dspec, fext_spec)
        # fext_param, dparam = ddir.fileinfo['param']

        # all fig stuff needs to be moved
        # dfig_dpl = ddir.fileinfo['figdpl'][1]
        # dfig_spec = ddir.fileinfo['figspec'][1]
        # dfig_spk = ddir.fileinfo['figspk'][1]

        # Please keep this code around; it's useful for debugging
        # for file_spk in spk_list:
        #     # spikefn.spikes_from_file(net.gid_dict, file_spk)
        #     praster(gid_dict, tstop, file_spk, dfig_spk)

        # for p_dict, file_dpl, file_spec in it.izip(param_list, dpl_list, spec_list):
        #     # # Plot dipole data
        #     # pdipole(file_dpl, dfig_dpl)

        #     # Morlet analysis
        #     pspec(file_spec, dfig_spec, p_dict, key_types)
