# plotfn.py - pall and possibly other plot routines
#
# v 1.2.31
# rev 2012-11-05 (SL: changed usage of file_match)
# last major: (MS: using get_key_types from paramrw.py to identify keys whose value changes over runs. These keys are passed to plot functions for title generation)

from pdipole import pdipole
from spec import MorletSpec
from praster import praster
import itertools as it
import fileio as fio
import itertools as it
from multiprocessing import Pool

# terrible handling of variables
def pkernel(ddir, p_dict, file_spk, file_dpl, key_types, gid_dict, tstop):
    # fig dirs
    dfig_dpl = ddir.fileinfo['figdpl'][1]
    dfig_spec = ddir.fileinfo['figspec'][1]
    dfig_spk = ddir.fileinfo['figspk'][1]

    # plot kernels
    praster(gid_dict, tstop, file_spk, dfig_spk)
    pdipole(file_dpl, dfig_dpl, p_dict, key_types)
    MorletSpec(file_dpl, dfig_spec, p_dict, key_types)

    return 0

# r is the value returned by pkernel
# this is sort of a dummy function
def cb(r):
    pass

# plot function - this is sort of a stop-gap and shouldn't live here, really
def pall(ddir, p_exp, gid_dict, tstop):
    # all fig stuff needs to be moved
    dfig_dpl = ddir.fileinfo['figdpl'][1]
    dfig_spec = ddir.fileinfo['figspec'][1]
    dfig_spk = ddir.fileinfo['figspk'][1]

    key_types = p_exp.get_key_types()

    # these should be equivalent lengths
    dict_list = [p_exp.return_pdict(i) for i in range(p_exp.N_sims)]
    fext_dpl, ddpl = ddir.fileinfo['dipole']
    fext_spk, dspk = ddir.fileinfo['spikes']

    dpl_list = fio.file_match(ddpl, fext_dpl)
    spk_list = fio.file_match(dspk, fext_spk)
    # dpl_list = fio.file_match(ddir.fileinfo, 'dipole')
    # spk_list = fio.file_match(ddir.fileinfo, 'spikes')

    # Please keep this code around; it's useful for debugging
    # for file_spk in spk_list:
    #     # spikefn.spikes_from_file(net.gid_dict, file_spk)
    #     praster(gid_dict, tstop, file_spk, dfig_spk)

    # for file_dpl in dpl_list:
    #     # Plot dipole data
    #     pdipole(file_dpl, dfig_dpl)

    #     # Morlet analysis
    #     MorletSpec(file_dpl, dfig_spec)

    pl = Pool()
    for p_dict, file_spk, file_dpl in it.izip(dict_list, spk_list, dpl_list):
        pl.apply_async(pkernel, (ddir, p_dict, file_spk, file_dpl, key_types, gid_dict, tstop), callback=cb)

    pl.close()
    pl.join()
