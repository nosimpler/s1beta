# ac_manu_gamma.py - axes for gamma manuscript paper figs
#
# v 1.7.59a
# rev 2013-06-07 (SL: added new fig specs)
# last major: (SL: created)

import matplotlib as mpl
import axes_create as ac
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import itertools as it
import numpy as np

# strong ping and weak ping examples in Layer 5
class FigL5PingExample(ac.FigBase):
    def __init__(self):
        self.f = plt.figure(figsize=(7, 5))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left': gridspec.GridSpec(3, 50),
            'right': gridspec.GridSpec(3, 50),
        }

        # repositioning the gspec
        l = np.arange(0.1, 0.95, 0.45)
        r = l + 0.4
        print l, r

        # create the gridspec
        self.gspec['left'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['right'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[1], right=r[1])

        # create axes and handles
        self.ax = {
            'spec_L': self.f.add_subplot(self.gspec['left'][:1, :]),
            'dpl_L': self.f.add_subplot(self.gspec['left'][1:2, :40]),
            'raster_L': self.f.add_subplot(self.gspec['left'][2:, :40]),

            'spec_R': self.f.add_subplot(self.gspec['right'][:1, :]),
            'dpl_R': self.f.add_subplot(self.gspec['right'][1:2, :40]),
            'raster_R': self.f.add_subplot(self.gspec['right'][2:, :40]),
        }

# 2 examples of different phases and the aggregate spectral power as a function of delay
class FigDistalPhase(ac.FigBase):
    def __init__(self):
        self.f = plt.figure(figsize=(13, 4))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left': gridspec.GridSpec(3, 50),
            'middle': gridspec.GridSpec(3, 50),
            'right': gridspec.GridSpec(1, 1),
        }

        # reposition the gridspecs
        l = np.arange(0.05, 0.95, 0.3)
        r = l + 0.25

        # create the gridspecs
        self.gspec['left'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['middle'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[1], right=r[1])
        self.gspec['right'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[2], right=r[2])

        # create axes and handles
        self.ax = {
            'spec_L': self.f.add_subplot(self.gspec['left'][:2, :]),
            'spec_R': self.f.add_subplot(self.gspec['middle'][:2, :]),

            'dpl_L': self.f.add_subplot(self.gspec['left'][2:, :40]),
            'dpl_R': self.f.add_subplot(self.gspec['middle'][2:, :40]),

            'aggregate': self.f.add_subplot(self.gspec['right'][:, :]),
        }

        self.__add_labels_subfig(l)

    # add text labels
    def __add_labels_subfig(self, l):
        self.f.text(l[0], 0.95, 'A.')
        self.f.text(l[1], 0.95, 'B.')
        self.f.text(l[2], 0.95, 'C.')

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
        r = l + 0.25

        # create the gridspecs
        self.gspec['left'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['middle'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[1], right=r[1])
        self.gspec['right'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[2], right=r[2])

        self.ax = {
            'dpl_L': self.f.add_subplot(self.gspec['left'][:-1, :40]),
            'dpl_M': self.f.add_subplot(self.gspec['middle'][:-1, :40]),
            'dpl_R': self.f.add_subplot(self.gspec['right'][:-1, :40]),

            'spec_L': self.f.add_subplot(self.gspec['left'][1:, :40]),
            'spec_M': self.f.add_subplot(self.gspec['middle'][1:, :40]),
            'spec_R': self.f.add_subplot(self.gspec['right'][1:, :]),
        }

        # self.__remove_labels()
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
    testfig = FigL5PingExample()
    testfig.savepng(f_test)
    testfig.close()
