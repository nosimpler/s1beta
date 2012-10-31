# plotfn.py - pall and possibly other plot routines
#
# v 1.2.23
# rev 2012-10-30 (MS: p_dict input added to pkernal() for title generation in plot fns)
# last major: (SL: attempting to make this truly asynchronous)

from pdipole import pdipole
from spec import MorletSpec
from praster import praster
import itertools as it
import fileio as fio
import itertools as it
from multiprocessing import Pool

# terrible handling of variables
def pkernel(ddir, p_dict, file_spk, file_dpl, gid_dict, tstop):
    # fig dirs
    dfig_dpl = ddir.fileinfo['figdpl'][1]
    dfig_spec = ddir.fileinfo['figspec'][1]
    dfig_spk = ddir.fileinfo['figspk'][1]

    # plot kernels
    praster(gid_dict, tstop, file_spk, dfig_spk)
    pdipole(file_dpl, p_dict, dfig_dpl)
    MorletSpec(file_dpl, p_dict, dfig_spec)

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

    # these should be equivalent lengths
    dict_list = [p_exp.return_pdict(i) for i in range(p_exp.N_sims)]
    dpl_list = fio.file_match(ddir.fileinfo, 'dipole')
    spk_list = fio.file_match(ddir.fileinfo, 'spikes')

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
        pl.apply_async(pkernel, (ddir, p_dict, file_spk, file_dpl, gid_dict, tstop), callback=cb)

    pl.close()
    pl.join()
