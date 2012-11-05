# plotfn.py - pall and possibly other plot routines
#
# v 1.2.32
# rev 2012-11-05 (MS: Now loads raw spec data and uses pspec() to plot spec data)
# last major: (SL: changed usage of file_match)

from pdipole import pdipole
from spec import pspec
from praster import praster
import itertools as it
import fileio as fio
import itertools as it
from multiprocessing import Pool

# terrible handling of variables
def pkernel(ddir, p_dict, file_spk, file_dpl, file_spec, key_types, gid_dict, tstop):
    # fig dirs
    dfig_dpl = ddir.fileinfo['figdpl'][1]
    dfig_spec = ddir.fileinfo['figspec'][1]
    dfig_spk = ddir.fileinfo['figspk'][1]

    # plot kernels
    praster(gid_dict, tstop, file_spk, dfig_spk)
    pdipole(file_dpl, dfig_dpl, p_dict, key_types)
    pspec(file_spec, dfig_spec, p_dict, key_types)

    return 0

# r is the value returned by pkernel
# this is sort of a dummy function
def cb(r):
    pass

# plot function - this is sort of a stop-gap and shouldn't live here, really
def pall(ddir, p_exp, gid_dict, tstop):
    key_types = p_exp.get_key_types()

    # these should be equivalent lengths
    dict_list = [p_exp.return_pdict(i) for i in range(p_exp.N_sims)]
    fext_dpl, ddpl = ddir.fileinfo['rawdpl']
    fext_spk, dspk = ddir.fileinfo['rawspk']
    fext_spec, dspec = ddir.fileinfo['rawspec']

    dpl_list = fio.file_match(ddpl, fext_dpl)
    spk_list = fio.file_match(dspk, fext_spk)
    spec_list = fio.file_match(dspec, fext_spec)

    # all fig stuff needs to be moved
    # dfig_dpl = ddir.fileinfo['figdpl'][1]
    # dfig_spec = ddir.fileinfo['figspec'][1]
    # dfig_spk = ddir.fileinfo['figspk'][1]

    # Please keep this code around; it's useful for debugging
    # for file_spk in spk_list:
    #     # spikefn.spikes_from_file(net.gid_dict, file_spk)
    #     praster(gid_dict, tstop, file_spk, dfig_spk)

    # for p_dict, file_dpl, file_spec in it.izip(dict_list, dpl_list, spec_list):
    #     # Plot dipole data
    #     pdipole(file_dpl, dfig_dpl)

    #     # Morlet analysis
    #     pspec(file_spec, dfig_spec, p_dict, key_types)

    pl = Pool()
    for p_dict, file_spk, file_dpl, file_spec in it.izip(dict_list, spk_list, dpl_list, spec_list):
        pl.apply_async(pkernel, (ddir, p_dict, file_spk, file_dpl, file_spec, key_types, gid_dict, tstop), callback=cb)

    pl.close()
    pl.join()
