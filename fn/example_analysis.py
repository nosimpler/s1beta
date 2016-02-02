#!/usr/bin/env python
# example_analysis.py - Example for an analysis workflow
#
# v 1.9.4
# rev 2016-02-02 (SL: created)
# last major: ()

import numpy as np
import fileio as fio
import paramrw
import itertools as it
import PT_example

# example simulation
def example_analysis_for_simulation():
    # from these two directories
    droot = '/repo/data/s1beta'
    dsim = '/Users/shane/repo/data/s1/2016-02-02/test-002'

    # create the SimulationPaths() object ddata and read the simulation
    ddata = fio.SimulationPaths()
    ddata.read_sim(droot, dsim)

    # print dir(ddata)
    # print type(np.zeros(5))

    # print ddata.expmt_groups
    # print ddata.fparam
    # for key, val in ddata.dfig['testing'].iteritems():
    #     print key, val
    # print dir({})

    # p_exp = paramrw.ExpParams(ddata.fparam)
    # print p_exp.p_all['dt']
    # # print p_exp.p_all

    # iterate through experimental groups and do the analysis on individual files, etc.
    for expmt_group in ddata.expmt_groups:
        print "experiment group is: %s" % (expmt_group)
        # print ddata.dfig[expmt_group]
        flist_param = ddata.file_match(expmt_group, 'param')
        flist_dpl = ddata.file_match(expmt_group, 'rawdpl')
        # flist_spk = ddata.file_match(expmt_group, 'rawspk')
        # fio.prettyprint(flist_spk)

        # iterate through files in the lists
        for fparam, fdpl in it.izip(flist_param, flist_dpl):
            # print fparam, fdpl
            gid_dict, p_tr = paramrw.read(fparam)
            # for key, val in p_tr.iteritems():
            #     print key, val
            # fio.prettyprint(p_tr.keys())

            # more or less analysis goes here.

            # this filename already exists, use with caution ...
            fname_png = ddata.return_filename_example('figspec', expmt_group, p_tr['Sim_No'], tr=p_tr['Trial'])
            # print p_tr['Trial'], p_tr['Sim_No'], fname_png

            # example figure for this pair of files
            fig = PT_example.FigExample()
            # fig.ax['dipole'].plot(np.random.rand(1000))
            # fig.savepng(fname_png)
            fig.close()

if __name__ == '__main__':
    example_analysis_for_simulation()
