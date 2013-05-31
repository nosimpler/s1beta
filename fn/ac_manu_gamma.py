# ac_manu_gamma.py - axes for gamma manuscript paper figs
#
# v 1.7.57
# rev 2013-05-31 (SL: created)
# last major:

import matplotlib as mpl
import axes_create as ac
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import itertools as it
import numpy as np

class FigTest(ac.FigBase):
    def __init__(self):
        # ac.FigBase.__init__(self)
        self.f = plt.figure(figsize=(13, 5))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left': gridspec.GridSpec(2, 1),
            'middle': gridspec.GridSpec(2, 1),
            'right': gridspec.GridSpec(2, 1),
        }

        # reposition the gridspecs
        l = np.arange(0.05, 0.95, 0.3)
        r = l + 0.25

        # create the gridspecs
        self.gspec['left'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['middle'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[1], right=r[1])
        self.gspec['right'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.94, left=l[2], right=r[2])

        self.ax = {
            'dpl_L': self.f.add_subplot(self.gspec['left'][:-1, :]),
            'dpl_M': self.f.add_subplot(self.gspec['middle'][:-1, :]),
            'dpl_R': self.f.add_subplot(self.gspec['right'][:-1, :]),

            'spec_L': self.f.add_subplot(self.gspec['left'][1:, :]),
            'spec_M': self.f.add_subplot(self.gspec['middle'][1:, :]),
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

    testfig = FigTest()
    testfig.savepng(f_test)
    testfig.close()
