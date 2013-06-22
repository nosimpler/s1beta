# ac_manu_gamma.py - axes for gamma manuscript paper figs
#
# v 1.8.12
# rev 2013-06-22 (SL: new fig specs)
# last major: (SL: added new fig specs)

import matplotlib as mpl
import axes_create as ac
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import itertools as it
import numpy as np

class FigLaminarComparison(ac.FigBase):
    def __init__(self):
        self.f = plt.figure(figsize=(8, 6))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left': gridspec.GridSpec(4, 50),
            'middle': gridspec.GridSpec(4, 50),
            'right': gridspec.GridSpec(4, 50),
        }

        # reposition the gridspecs
        l = np.arange(0.10, 0.95, 0.3)
        r = l + 0.25

        # update the gridspecs
        self.gspec['left'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['middle'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[1], right=r[1])
        self.gspec['right'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[2], right=r[2])

        # create axes and handles
        self.ax = {
            'pgram_L': self.f.add_subplot(self.gspec['left'][:1, :40]),
            'pgram_M': self.f.add_subplot(self.gspec['middle'][:1, :40]),
            'pgram_R': self.f.add_subplot(self.gspec['right'][:1, :40]),

            'spec_L': self.f.add_subplot(self.gspec['left'][1:2, :]),
            'spec_M': self.f.add_subplot(self.gspec['middle'][1:2, :]),
            'spec_R': self.f.add_subplot(self.gspec['right'][1:2, :]),

            'dpl_L': self.f.add_subplot(self.gspec['left'][2:3, :40]),
            'dpl_M': self.f.add_subplot(self.gspec['middle'][2:3, :40]),
            'dpl_R': self.f.add_subplot(self.gspec['right'][2:3, :40]),

            # 'spk_L': self.f.add_subplot(self.gspec['left'][3:, :40]),
            'spk_M': self.f.add_subplot(self.gspec['middle'][3:, :40]),
            'spk_R': self.f.add_subplot(self.gspec['right'][3:, :40]),
        }

        # remove ytick labels
        self.ax['spk_M'].set_yticklabels('')
        self.ax['spk_R'].set_yticklabels('')

# strong ping and weak ping examples in Layer 5
class FigL5PingExample(ac.FigBase):
    def __init__(self):
        self.f = plt.figure(figsize=(7, 5))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left': gridspec.GridSpec(4, 50),
            'right': gridspec.GridSpec(4, 50),
        }

        # repositioning the gspec
        l = np.arange(0.1, 0.95, 0.45)
        r = l + 0.4

        # create the gridspec
        self.gspec['left'].update(wspace=0, hspace=0.20, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['right'].update(wspace=0, hspace=0.20, bottom=0.1, top=0.94, left=l[1], right=r[1])

        # create axes and handles
        self.ax = {
            'pgram_L': self.f.add_subplot(self.gspec['left'][:1, :40]),
            'spec_L': self.f.add_subplot(self.gspec['left'][1:2, :]),
            'dpl_L': self.f.add_subplot(self.gspec['left'][2:3, :40]),
            'raster_L': self.f.add_subplot(self.gspec['left'][3:, :40]),

            'pgram_R': self.f.add_subplot(self.gspec['right'][:1, :40]),
            'spec_R': self.f.add_subplot(self.gspec['right'][1:2, :]),
            'dpl_R': self.f.add_subplot(self.gspec['right'][2:3, :40]),
            'raster_R': self.f.add_subplot(self.gspec['right'][3:, :40]),
        }

        # pgram_axes
        list_handles_pgram = [h for h in self.ax.keys() if h.startswith('pgram_')]
        # self.fmt = self.set_notation_scientific(list_handles_pgram)
        self.fmt = None

        # remove ytick labels for the rasters
        for h in [ax for ax in self.ax if ax.startswith('raster_')]:
            self.ax[h].set_yticklabels('')

        self.__remove_labels()

    # function to remove labels when not testing
    def __remove_labels(self):
        for ax in self.ax.keys():
            if ((ax.startswith('dpl')) or (ax.startswith('spec'))):
                self.ax[ax].set_xticklabels('')

# 2 examples of different phases and the aggregate spectral power as a function of delay
class FigDistalPhase(ac.FigBase):
    def __init__(self):
        self.f = plt.figure(figsize=(15, 4))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left0': gridspec.GridSpec(3, 50),
            'left1': gridspec.GridSpec(3, 50),
            'middle': gridspec.GridSpec(3, 50),
            'right': gridspec.GridSpec(1, 1),
        }

        # number of cols are the number of gridspecs
        n_cols = len(self.gspec.keys())

        # find the start values by making a linspace from L margin to R margin
        # and then remove the R margin's element
        # this is why you need n_cols+1
        l = np.linspace(0.1, 0.95, n_cols+1)[:-1]

        # ensure first element of the unique on the diff of l to find
        # the width of each panel
        # remove the width of some margin
        w_margin = 0.05
        w = np.unique(np.diff(l))[0] - w_margin

        # to find the right position, just add w to the l
        r = l + w
        # print l, r
        # l = np.arange(0.05, 0.95, 0.2)
        # r = l + 0.15

        # create the gridspecs
        self.gspec['left0'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['left1'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[1], right=r[1])
        self.gspec['middle'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[2], right=r[2])
        self.gspec['right'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[3], right=r[3])

        # create axes and handles
        self.ax = {
            'spec_L': self.f.add_subplot(self.gspec['left0'][:2, :]),
            'spec_M': self.f.add_subplot(self.gspec['left1'][:2, :]),
            'spec_R': self.f.add_subplot(self.gspec['middle'][:2, :]),

            'dpl_L': self.f.add_subplot(self.gspec['left0'][2:, :40]),
            'dpl_M': self.f.add_subplot(self.gspec['left1'][2:, :40]),
            'dpl_R': self.f.add_subplot(self.gspec['middle'][2:, :40]),

            'aggregate': self.f.add_subplot(self.gspec['right'][:, :]),
        }

        self.__add_labels_subfig(l)

    # add text labels
    def __add_labels_subfig(self, l):
        self.f.text(l[0], 0.95, 'A.')
        self.f.text(l[1], 0.95, 'B.')
        self.f.text(l[2], 0.95, 'C.')
        self.f.text(l[3], 0.95, 'D.')

class FigStDev(ac.FigBase):
    def __init__(self):
        # ac.FigBase.__init__(self)
        self.f = plt.figure(figsize=(13, 5))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left': gridspec.GridSpec(2, 50),
            'middle': gridspec.GridSpec(2, 50),
            'right': gridspec.GridSpec(2, 50),
        }

        # reposition the gridspecs
        l = np.arange(0.05, 0.95, 0.3)
        r = l + 0.28

        # create the gridspecs
        self.gspec['left'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['middle'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[1], right=r[1])
        self.gspec['right'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[2], right=r[2])

        self.ax = {
            'dpl_L': self.f.add_subplot(self.gspec['left'][:-1, :40]),
            'dpl_M': self.f.add_subplot(self.gspec['middle'][:-1, :40]),
            'dpl_R': self.f.add_subplot(self.gspec['right'][:-1, :40]),

            'spec_L': self.f.add_subplot(self.gspec['left'][1:, :]),
            'spec_M': self.f.add_subplot(self.gspec['middle'][1:, :]),
            'spec_R': self.f.add_subplot(self.gspec['right'][1:, :]),
        }

        self.__remove_labels()
        self.__add_labels_subfig(l)

    # function to remove labels when not testing
    def __remove_labels(self):
        for ax in self.ax.keys():
            if ax.startswith('dpl'):
                self.ax[ax].set_xticklabels('')

    # add text labels
    def __add_labels_subfig(self, l):
        self.f.text(l[0], 0.95, 'A.')
        self.f.text(l[1], 0.95, 'B.')
        self.f.text(l[2], 0.95, 'C.')

if __name__ == '__main__':
    x = np.random.rand(100)

    f_test = 'testing.png'

    # testfig for FigDipoleExp()
    # testfig = ac.FigDipoleExp(ax_handles)
    # testfig.create_colorbar_axis('spec')
    # testfig.ax['spec'].plot(x)

    # testfig = FigTest()
    # testfig = FigL5PingExample()
    # testfig = FigLaminarComparison()
    testfig = FigDistalPhase()
    testfig.savepng(f_test)
    testfig.close()
