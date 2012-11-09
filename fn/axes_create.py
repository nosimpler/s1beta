# axes_create.py - simple axis creation
#
# v 1.4.2
# rev 2012-11-09 (SL: Added fig_psth)
# last major: (MS: Added class fig_spec)

# usage:
# testfig = fig_std()
# testfig.ax0.plot(somedata)
# plt.savefig('testfig.png')
# testfig.close()

import matplotlib as mpl
# mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

class fig_std():
    def __init__(self):
        self.f = plt.figure(figsize = (12, 6))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        gs0 = gridspec.GridSpec(1, 1)
        self.ax0 = self.f.add_subplot(gs0[:])

    def close(self):
        plt.close(self.f)

class fig_spec():
    def __init__(self):
        self.f = plt.figure(figsize = (8, 6))
        font_prop = {'size': 10}
        mpl.rc('font', **font_prop)

        gs0 = gridspec.GridSpec(1, 1)
        self.ax0 = self.f.add_subplot(gs0[:])

        # gs0 = gridspec.GridSpec(2, 1, height_ratios=[1,3])
        # self.ax0 = self.f.add_subplot(gs0[:1, :])
        # self.ax1 = self.f.add_subplot(gs0[1:2, :])

    def close(self):
        plt.close(self.f)

class fig_raster():
    def __init__(self, tstop):
        self.tstop = tstop
        self.f = plt.figure(figsize=(6, 8))

        grid0 = gridspec.GridSpec(4, 1)
        grid0.update(wspace=0.05, hspace=0., bottom=0.05, top=0.45)

        grid1 = gridspec.GridSpec(4, 1)
        grid1.update(wspace=0.05, hspace=0., bottom=0.50, top=0.95)

        self.ax = {}

        self.__panel_create(grid1, 'L2')
        self.__panel_create(grid0, 'L5')

        for key in self.ax.keys():
            if key is 'ax_L5_extpois':
                self.__bottom_panel_prop(self.ax[key])

            else:
                self.__raster_prop(self.ax[key])

    def __panel_create(self, grid, layer):
        self.ax[layer] = self.f.add_subplot(grid[:2, :])
        self.ax[layer+'_extgauss'] = self.f.add_subplot(grid[2:3, :])
        self.ax[layer+'_extpois'] = self.f.add_subplot(grid[3:, :])
        # self.ax_L2 = self.f.add_subplot(grid[:2, :])

    def __bottom_panel_prop(self, ax):
        ax.set_yticklabels('')
        ax.set_xlim(0, self.tstop)

    def __raster_prop(self, ax):
        ax.set_yticklabels('')
        ax.set_xticklabels('')
        ax.set_xlim(0, self.tstop)

    def close(self):
        plt.close(self.f)

class fig_psth():
    def __init__(self, tstop):
        self.tstop = tstop
        self.f = plt.figure(figsize=(6, 5))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        grid0 = gridspec.GridSpec(6, 2)
        grid0.update(wspace=0.05, hspace=0., bottom=0.05, top=0.95)

        self.ax = {}

        self.ax['L2'] = self.f.add_subplot(grid0[:2, :1], title='Layer 2')
        self.ax['L2_psth'] = self.f.add_subplot(grid0[2:4, :1])
        self.ax['L2_extgauss'] = self.f.add_subplot(grid0[4:5, :1])
        self.ax['L2_extpois'] = self.f.add_subplot(grid0[5:, :1], xlabel='Time (ms)')

        self.ax['L5'] = self.f.add_subplot(grid0[:2, 1:], title='Layer 5')
        self.ax['L5_psth'] = self.f.add_subplot(grid0[2:4, 1:])
        self.ax['L5_extgauss'] = self.f.add_subplot(grid0[4:5, 1:])
        self.ax['L5_extpois'] = self.f.add_subplot(grid0[5:, 1:], xlabel='Time (ms)')

        for key in self.ax.keys():
            if key.endswith('_extpois'):
                self.__bottom_panel_prop(self.ax[key])

            elif key.endswith('_psth'):
                self.__psth_prop(self.ax[key])

            else:
                self.__raster_prop(self.ax[key])

        grid0.tight_layout(self.f, rect=[0, 0, 1, 1], h_pad=0., w_pad=1)

    def __bottom_panel_prop(self, ax):
        ax.set_yticklabels('')
        ax.set_xlim(0, self.tstop)
        ax.get_xticklabels()
        # locs, labels = plt.xticks()
        # plt.setp(labels, rotation=45)

    def __psth_prop(self, ax):
        # ax.set_yticklabels('')
        ax.set_xticklabels('')
        ax.set_xlim(0, self.tstop)

        for tick in ax.yaxis.get_major_ticks():
            tick.label1On = False
            tick.label2On = True

    def __raster_prop(self, ax):
        ax.set_yticklabels('')
        ax.set_xticklabels('')
        ax.set_xlim(0, self.tstop)

    def close(self):
        plt.close(self.f)

def testfn():
    x = np.random.rand(100)

    # testfig = fig_std()
    # testfig.ax0.plot(x)

    # testfig = fig_raster(100)
    # testfig.ax['L5'].plot(x)

    # testfig = fig_spec()
    # testfig.ax0.plot(x)

    testfig = fig_psth(100)
    testfig.ax['L5_extpois'].plot(x)

    plt.savefig('testing.png')
    testfig.close()

if __name__ == '__main__':
    testfn()
