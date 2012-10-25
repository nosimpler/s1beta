# plotfn.py - pall and possibly other plot routines
#
# v 1.2.17
# rev 2012-10-25 (SL: created from s1run.py)
# last major:

from pdipole import pdipole
from spec import MorletSpec
from praster import praster
import fileio as fio

# plot function - this is sort of a stop-gap and shouldn't live here, really
def pall(ddir, gid_dict, tstop):
    # all fig stuff needs to be moved
    dfig_dpl = ddir.fileinfo['figdpl'][1]
    dfig_spec = ddir.fileinfo['figspec'][1]
    dfig_spk = ddir.fileinfo['figspk'][1]

    dpl_list = fio.file_match(ddir.fileinfo, 'dipole')
    spk_list = fio.file_match(ddir.fileinfo, 'spikes')

    for file_spk in spk_list:
        # spikefn.spikes_from_file(net.gid_dict, file_spk)
        praster(gid_dict, tstop, file_spk, dfig_spk)

    for file_dpl in dpl_list:
        # Plot dipole data
        pdipole(file_dpl, dfig_dpl)

        # Morlet analysis
        MorletSpec(file_dpl, dfig_spec)
