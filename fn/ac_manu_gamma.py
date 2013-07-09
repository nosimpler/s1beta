# ac_manu_gamma.py - axes for gamma manuscript paper figs
#
# v 1.8.14
# rev 2013-07-09 (SL: updates)
# last major: (SL: new fig specs)

import matplotlib as mpl
import axes_create as ac
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import itertools as it
import numpy as np

class FigLaminarComparison(ac.FigBase):
    def __init__(self, runtype='debug'):
        self.f = plt.figure(figsize=(9, 6.5))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left': gridspec.GridSpec(9, 50),
            'middle': gridspec.GridSpec(9, 50),
            'right': gridspec.GridSpec(9, 50),
        }

        # reposition the gridspecs
        l = np.arange(0.10, 0.95, 0.3)
        r = l + 0.25

        # update the gridspecs
        self.gspec['left'].update(wspace=0, hspace=0.30, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['middle'].update(wspace=0, hspace=0.30, bottom=0.1, top=0.94, left=l[1], right=r[1])
        self.gspec['right'].update(wspace=0, hspace=0.30, bottom=0.1, top=0.94, left=l[2], right=r[2])

        # create axes and handles
        self.ax = {
            'pgram_L': self.f.add_subplot(self.gspec['left'][:2, :40]),
            'pgram_M': self.f.add_subplot(self.gspec['middle'][:2, :40]),
            'pgram_R': self.f.add_subplot(self.gspec['right'][:2, :40]),

            'spec_L': None,
            'spec_M': None,
            'spec_R': self.f.add_subplot(self.gspec['right'][2:4, :]),

            'dpl_L': self.f.add_subplot(self.gspec['left'][4:6, :40]),
            'dpl_M': self.f.add_subplot(self.gspec['middle'][4:6, :40]),
            'dpl_R': self.f.add_subplot(self.gspec['right'][4:6, :40]),

            # 'spk_L': self.f.add_subplot(self.gspec['left'][6:8, :40]),
            'spk_M': self.f.add_subplot(self.gspec['middle'][6:8, :40]),
            'spk_R': self.f.add_subplot(self.gspec['right'][6:8, :40]),

            'current_M': self.f.add_subplot(self.gspec['middle'][8:, :40]),
            'current_R': self.f.add_subplot(self.gspec['right'][8:, :40]),
        }

        if runtype in ('debug', 'pub2'):
            self.ax['spec_L'] = self.f.add_subplot(self.gspec['left'][2:4, :])
            self.ax['spec_M'] = self.f.add_subplot(self.gspec['middle'][2:4, :])

        elif runtype == 'pub':
            self.ax['spec_L'] = self.f.add_subplot(self.gspec['left'][2:4, :40])
            self.ax['spec_M'] = self.f.add_subplot(self.gspec['middle'][2:4, :40])

        # remove xtick labels
        list_ax_noxtick = [ax_handle for ax_handle in self.ax.keys() if ax_handle.startswith('spec')]
        list_ax_noxtick.append('dpl_M')
        list_ax_noxtick.append('dpl_R')

        # function defined in FigBase()
        self.remove_tick_labels(list_ax_noxtick, 'x')

        # remove ytick labels
        self.ax['spk_M'].set_yticklabels('')
        self.ax['spk_R'].set_yticklabels('')
        list_ax_noytick = []

        # write list of no y tick axes
        if runtype == 'pub':
            for ax in self.ax.keys():
                if ax.startswith('spk_') or ax.endswith(('_M', '_R')):
                    list_ax_noytick.append(ax)

        # function defined in FigBase()
        self.remove_tick_labels(list_ax_noytick, 'y')
        self.__add_labels_subfig(l)

    # add text labels
    def __add_labels_subfig(self, l):
        self.f.text(l[0], 0.965, 'A.')
        self.f.text(l[1], 0.965, 'B.')
        self.f.text(l[2], 0.965, 'C.')

        self.ax['spec_L'].set_ylabel('Frequency (Hz)')
        self.ax['dpl_L'].set_ylabel('Current dipole (nAm)')
        self.ax['pgram_L'].set_ylabel('PSD ((nAm)$^2$/Hz)')
        self.ax['spk_M'].set_ylabel('Cell no.')
        self.ax['current_M'].set_ylabel('Current (nA)')

        self.f.text(l[1], 0.025, 'Time (ms)')
        # self.f.text(0.925, 0.40, 'Power spectral density ((nAm)$^2$/Hz)', rotation=270)

    def set_axes_pingping(self):
        self.ax['current_R'].set_ylim((-2000., 0.))

# strong ping and weak ping examples in Layer 5
class FigL5PingExample(ac.FigBase):
    def __init__(self, runtype='debug'):
        self.f = plt.figure(figsize=(7, 9))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left': gridspec.GridSpec(9, 50),
            'right': gridspec.GridSpec(9, 50),
        }

        # repositioning the gspec
        l = np.arange(0.12, 0.90, 0.45)
        r = l + 0.38

        # create the gridspec
        self.gspec['left'].update(wspace=0, hspace=0.30, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['right'].update(wspace=0, hspace=0.30, bottom=0.1, top=0.94, left=l[1], right=r[1])

        # create axes and handles
        # spec_L will be conditional on debug or production
        self.ax = {
            'pgram_L': self.f.add_subplot(self.gspec['left'][:2, :40]),
            'spec_L': None,
            'dpl_L': self.f.add_subplot(self.gspec['left'][4:6, :40]),
            'raster_L': self.f.add_subplot(self.gspec['left'][6:8, :40]),
            'current_L': self.f.add_subplot(self.gspec['left'][8:, :40]),

            'pgram_R': self.f.add_subplot(self.gspec['right'][:2, :40]),
            'spec_R': self.f.add_subplot(self.gspec['right'][2:4, :]),
            'dpl_R': self.f.add_subplot(self.gspec['right'][4:6, :40]),
            'raster_R': self.f.add_subplot(self.gspec['right'][6:8, :40]),
            'current_R': self.f.add_subplot(self.gspec['right'][8:, :40]),
        }

        # different spec_L depending on mode
        if runtype in ('debug', 'pub2'):
            self.ax['spec_L'] = self.f.add_subplot(self.gspec['left'][2:4, :])

        elif runtype == 'pub':
            self.ax['spec_L'] = self.f.add_subplot(self.gspec['left'][2:4, :40])

        # pgram_axes
        list_handles_pgram = [h for h in self.ax.keys() if h.startswith('pgram_')]
        # self.fmt = self.set_notation_scientific(list_handles_pgram)
        self.fmt = None

        # remove ytick labels for the rasters
        for h in [ax for ax in self.ax if ax.startswith('raster_')]:
            self.ax[h].set_yticklabels('')

        if runtype == 'pub':
            self.__remove_labels()

        self.__add_labels_subfig(l)

    # add text labels
    def __add_labels_subfig(self, l):
        self.f.text(l[0], 0.95, 'A.')
        self.f.text(l[1], 0.95, 'B.')

        self.ax['spec_L'].set_ylabel('Frequency (Hz)')
        self.ax['dpl_L'].set_ylabel('Current dipole (nAm)')
        self.ax['pgram_L'].set_ylabel('(nAm)$^2$/Hz')
        self.ax['raster_L'].set_ylabel('Cell no.')

        self.f.text(l[0], 0.05, 'Time (ms)')
        # self.f.text(0.925, 0.40, 'Power spectral density ((nAm)$^2$/Hz)', rotation=270)

    # function to remove labels when not testing
    def __remove_labels(self):
        for ax in self.ax.keys():
            if ((ax.startswith('dpl')) or (ax.startswith('spec'))):
                self.ax[ax].set_xticklabels('')

            if ax.endswith('_R'):
                self.ax[ax].set_yticklabels('')

# 2 examples of different phases and the aggregate spectral power as a function of delay
class FigDistalPhase(ac.FigBase):
    def __init__(self):
        ac.FigBase.__init__(self)
        self.f = plt.figure(figsize=(15, 4))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left0': gridspec.GridSpec(4, 50),
            'left1': gridspec.GridSpec(4, 50),
            'middle': gridspec.GridSpec(4, 50),
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

        # create the gridspecs
        self.gspec['left0'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.91, left=l[0], right=r[0])
        self.gspec['left1'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.91, left=l[1], right=r[1])
        self.gspec['middle'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.91, left=l[2], right=r[2])
        self.gspec['right'].update(wspace=0, hspace=0.15, bottom=0.1, top=0.91, left=l[3], right=r[3])

        # create axes and handles
        self.ax = {
            'spec_L': self.f.add_subplot(self.gspec['left0'][:2, :]),
            'spec_M': self.f.add_subplot(self.gspec['left1'][:2, :]),
            'spec_R': self.f.add_subplot(self.gspec['middle'][:2, :]),

            'dpl_L': self.f.add_subplot(self.gspec['left0'][2:3, :40]),
            'dpl_M': self.f.add_subplot(self.gspec['left1'][2:3, :40]),
            'dpl_R': self.f.add_subplot(self.gspec['middle'][2:3, :40]),

            'hist_L': self.f.add_subplot(self.gspec['left0'][3:, :40]),
            'hist_M': self.f.add_subplot(self.gspec['left1'][3:, :40]),
            'hist_R': self.f.add_subplot(self.gspec['middle'][3:, :40]),

            'aggregate': self.f.add_subplot(self.gspec['right'][:, :]),
        }

        self.__create_hist_twinx()
        self.__add_labels_subfig(l)

    def __create_hist_twinx(self):
        # ax_handles_hist = [ax for ax in self.ax.keys() if ax.startswith('hist')]
        for ax in self.ax.keys():
            if ax.startswith('hist'):
                self.create_axis_twinx(ax)

    # add text labels
    def __add_labels_subfig(self, l):
        self.f.text(l[0], 0.95, 'A.')
        self.f.text(l[1], 0.95, 'B.')
        self.f.text(l[2], 0.95, 'C.')
        self.f.text(l[3], 0.95, 'D.')

class FigStDev(ac.FigBase):
    def __init__(self, runtype='debug'):
        ac.FigBase.__init__(self)
        self.f = plt.figure(figsize=(11, 5))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left': gridspec.GridSpec(5, 50),
            'middle': gridspec.GridSpec(5, 50),
            'right': gridspec.GridSpec(5, 50),
        }

        # reposition the gridspecs
        l = np.arange(0.1, 0.9, 0.28)
        # l = np.arange(0.05, 0.95, 0.3)
        r = l + 0.275

        # create the gridspecs
        self.gspec['left'].update(wspace=0, hspace=0.30, bottom=0.1, top=0.94, left=l[0], right=r[0])
        self.gspec['middle'].update(wspace=0, hspace=0.30, bottom=0.1, top=0.94, left=l[1], right=r[1])
        self.gspec['right'].update(wspace=0, hspace=0.30, bottom=0.1, top=0.94, left=l[2], right=r[2])

        self.ax = {
            'hist_L': self.f.add_subplot(self.gspec['left'][:1, :40]),
            'hist_M': self.f.add_subplot(self.gspec['middle'][:1, :40]),
            'hist_R': self.f.add_subplot(self.gspec['right'][:1, :40]),

            'dpl_L': self.f.add_subplot(self.gspec['left'][1:3, :40]),
            'dpl_M': self.f.add_subplot(self.gspec['middle'][1:3, :40]),
            'dpl_R': self.f.add_subplot(self.gspec['right'][1:3, :40]),

            # these are set differently depending on runtype, below
            'spec_L': None,
            'spec_M': None,
            'spec_R': None,
        }

        if runtype in ('debug', 'pub2'):
            self.ax['spec_L'] = self.f.add_subplot(self.gspec['left'][3:, :])
            self.ax['spec_M'] = self.f.add_subplot(self.gspec['middle'][3:, :])
            self.ax['spec_R'] = self.f.add_subplot(self.gspec['right'][3:, :])

        elif runtype == 'pub':
            self.ax['spec_L'] = self.f.add_subplot(self.gspec['left'][3:, :40])
            self.ax['spec_M'] = self.f.add_subplot(self.gspec['middle'][3:, :40])
            self.ax['spec_R'] = self.f.add_subplot(self.gspec['right'][3:, :])

        if runtype.startswith('pub'):
            self.__remove_labels()

        self.__create_twinx()
        self.__add_labels_subfig(l)

    def __create_twinx(self):
        for ax_handle in self.ax.keys():
            if ax_handle.startswith('hist'):
                self.create_axis_twinx(ax_handle)

    # function to remove labels when not testing
    def __remove_labels(self):
        for ax in self.ax.keys():
            if ax.startswith(('dpl', 'hist')):
                self.ax[ax].set_xticklabels('')

            if ax.endswith(('_M', '_R')):
                self.ax[ax].set_yticklabels('')

    def remove_twinx_labels(self):
        for ax in self.ax_twinx.keys():
            self.ax_twinx[ax].set_yticklabels('')

    # add text labels
    def __add_labels_subfig(self, l):
        self.f.text(l[0], 0.95, 'A.')
        self.f.text(l[1], 0.95, 'B.')
        self.f.text(l[2], 0.95, 'C.')

        self.ax['spec_L'].set_ylabel('Frequency (Hz)')
        self.ax['dpl_L'].set_ylabel('Current dipole (nAm)')
        self.ax['hist_L'].set_ylabel('EPSP count')

        self.f.text(l[0], 0.025, 'Time (ms)')
        self.f.text(0.925, 0.40, 'Power spectral density ((nAm)$^2$/Hz)', rotation=270)

class FigHF(ac.FigBase):
    def __init__(self, runtype='debug'):
        ac.FigBase.__init__(self)
        self.f = plt.figure(figsize=(4, 6))

        # set_fontsize() is part of FigBase()
        self.set_fontsize(8)

        # various gridspecs
        self.gspec = {
            'left': gridspec.GridSpec(5, 50),
        }

        # reposition the gridspecs
        # l = np.arange(0.1, 0.9, 0.28)
        # l = np.arange(0.05, 0.95, 0.3)
        # r = l + 0.275

        # create the gridspecs
        self.gspec['left'].update(wspace=0, hspace=0.30, bottom=0.1, top=0.94, left=0.2, right=0.95)

        self.ax = {
            'hist_L': self.f.add_subplot(self.gspec['left'][:1, :40]),
            'dpl_L': self.f.add_subplot(self.gspec['left'][1:3, :40]),

            # these are set differently depending on runtype, below
            'spec_L': None,
        }

        if runtype in ('debug', 'pub2'):
            self.ax['spec_L'] = self.f.add_subplot(self.gspec['left'][3:, :])

        elif runtype == 'pub':
            self.ax['spec_L'] = self.f.add_subplot(self.gspec['left'][3:, :40])

        # if runtype.startswith('pub'):
        #     self.__remove_labels()

        # self.__create_twinx()
        # self.__add_labels_subfig(l)

    def __create_twinx(self):
        for ax_handle in self.ax.keys():
            if ax_handle.startswith('hist'):
                self.create_axis_twinx(ax_handle)

    # function to remove labels when not testing
    def __remove_labels(self):
        for ax in self.ax.keys():
            if ax.startswith(('dpl', 'hist')):
                self.ax[ax].set_xticklabels('')

            if ax.endswith(('_M', '_R')):
                self.ax[ax].set_yticklabels('')

    def remove_twinx_labels(self):
        for ax in self.ax_twinx.keys():
            self.ax_twinx[ax].set_yticklabels('')

    # add text labels
    def __add_labels_subfig(self, l):
        self.f.text(l[0], 0.95, 'A.')
        self.f.text(l[1], 0.95, 'B.')
        self.f.text(l[2], 0.95, 'C.')

        self.ax['spec_L'].set_ylabel('Frequency (Hz)')
        self.ax['dpl_L'].set_ylabel('Current dipole (nAm)')
        self.ax['hist_L'].set_ylabel('EPSP count')

        self.f.text(l[0], 0.025, 'Time (ms)')
        self.f.text(0.925, 0.40, 'Power spectral density ((nAm)$^2$/Hz)', rotation=270)

if __name__ == '__main__':
    x = np.random.rand(100)

    f_test = 'testing.png'

    # testfig for FigDipoleExp()
    # testfig = ac.FigDipoleExp(ax_handles)
    # testfig.create_colorbar_axis('spec')
    # testfig.ax['spec'].plot(x)

    # testfig = FigTest()
    testfig = FigHF()
    # testfig = FigLaminarComparison()
    # testfig = FigDistalPhase()
    # testfig = FigStDev()
    testfig.savepng(f_test)
    testfig.close()
