# plotfn.py - pall and possibly other plot routines
#
# v 1.4.99
# rev 2012-12-03 (SL: experiments system added, currently broken spec)
# last major: (MS: Using spec data stored in list rather than reading from data file)

from pdipole import pdipole
from spec import pspec
from praster import praster
import paramrw
import itertools as it
import fileio as fio
import itertools as it
from multiprocessing import Pool

# terrible handling of variables
def pkernel(dfig, f_param, f_spk, f_dpl, key_types):
# def pkernel(dfig, f_param, f_spk, f_dpl, d_spec, key_types):
    gid_dict, p_dict = paramrw.read(f_param)
    tstop = p_dict['tstop']

    # fig dirs
    dfig_dpl = dfig['figdpl']
    dfig_spec = dfig['figspec']
    dfig_spk = dfig['figspk']

    # plot kernels
    praster(gid_dict, tstop, f_spk, dfig_spk)
    pdipole(f_dpl, dfig_dpl, p_dict, key_types)
    # pspec(d_spec, dfig_spec, p_dict, key_types)

    return 0

# r is the value returned by pkernel
# this is sort of a dummy function
def cb(r):
    pass

# plot function - this is sort of a stop-gap and shouldn't live here, really
def pall(ddir, p_exp, gid_dict, tstop):
# def pall(ddir, p_exp, spec_results, gid_dict, tstop):
    # runtype allows easy (hard coded switching between two modes)
    runtype = 'parallel'

    # create giant list of appropriate files and run them all at the same time
    if runtype is 'parallel':
        dsim = ddir.dsim

        key_types = p_exp.get_key_types()

        # run each experiment separately
        for expmt_group in ddir.expmt_groups:
            # these should be equivalent lengths
            param_list = ddir.file_match(expmt_group, 'param')
            dpl_list = ddir.file_match(expmt_group, 'rawdpl')
            spk_list = ddir.file_match(expmt_group, 'rawspk')
            spec_list = ddir.file_match(expmt_group, 'rawspec')

            # print ddir.dfig
            dfig = ddir.dfig[expmt_group]

            # *** spec is disabled here ***
            # *** remove comment when successfully fixed ***
            pl = Pool()
            for f_param, f_spk, f_dpl in it.izip(param_list, spk_list, dpl_list):
            # for f_param, f_spk, f_dpl, d_spec in it.izip(param_list, spk_list, dpl_list, spec_results):
                pl.apply_async(pkernel, (dfig, f_param, f_spk, f_dpl, key_types), callback=cb)
                # pl.apply_async(pkernel, (ddir, f_param, f_spk, f_dpl, d_spec, key_types), callback=cb)

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
