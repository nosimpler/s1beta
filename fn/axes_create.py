# axes_create.py - simple axis creation
#
# v 1.2.25
# rev 2012-11-01 (SL: Changed axes on raster plot)
# last major: (SL: added raster fig)

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
        font_prop = {'size': 10}
        mpl.rc('font', **font_prop)

        gs0 = gridspec.GridSpec(1, 1)
        self.ax0 = self.f.add_subplot(gs0[:])

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

        self.__panel_create(grid0, 'L2')
        self.__panel_create(grid1, 'L5')

        # self.ax_L5 = self.f.add_subplot(grid[1:2, :])
        # self.ax_L5_extgauss = self.f.add_subplot(grid[2:3, :])
        # self.ax_L5_extpois = self.f.add_subplot(grid[1:2, :])

        for key in self.ax.keys():
            if key is 'ax_L5_extpois':
                self.__bottom_panel_prop(self.ax[key])

            else:
                self.__raster_prop(self.ax[key])

        # self.__raster_prop(self.ax_L2)
        # self.__raster_prop(self.ax_L5)
        # self.__raster_prop(self.ax_extgauss)

        # self.__bottom_panel_prop()

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

def testfn():
    x = np.random.rand(100)

    # testfig = fig_std()
    # testfig.ax0.plot(x)

    testfig = fig_raster(100)
    testfig.ax['L5'].plot(x)

    plt.savefig('testing.png')
    testfig.close()

if __name__ == '__main__':
    testfn()
