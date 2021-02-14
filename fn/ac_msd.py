#!/usr/bin/env python
# ac_msd.py - Plot Templates for membrane state diagram-related plots
#
# v 1.9.6
# rev 2016-02-08 (RL: created)
# last major: ()

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import axes_create as ac

# plots voltage trace and membrane state diagrams at various points - 
# needs argument n_diagrams to set up array of diagrams
class FigMSDTrace(ac.FigBase):
    def __init__(self, n_diagrams):
        ac.FigBase.__init__(self)
        self.f = plt.figure(figsize=(8, 6))

        font_prop = {'size': 16}
        mpl.rc('font', **font_prop)

        self.gs = {
            'trace': gridspec.GridSpec(2, 1),
            'msd': gridspec.GridSpec(2, n_diagrams, wspace=0, hspace=0.35)
            }
        self.ax = {
                'trace': self.f.add_subplot(self.gs['trace'][0, :]),
            }
        
        for i in range(n_diagrams):
            self.ax[i] = self.f.add_subplot(self.gs['msd'][1, i], projection='polar')


if __name__ == '__main__':
    fig = FigExample()
    fig.ax['dipole'].plot(np.random.rand(1000))
    fig.savepng('testing.png')
    fig.close()
