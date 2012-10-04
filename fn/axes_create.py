# axes_create.py - simple axis creation
#
# v 1.2.12
# rev 2012-10-04 (SL: added raster fig)
# last major: (SL: moved from plot, did not delete original yet)

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
        grid = gridspec.GridSpec(3, 1)
        grid.update(wspace=0.05, hspace=0.025, bottom=0.05, top=0.95)
        self.ax_L2 = self.f.add_subplot(grid[:1, :])
        self.ax_L5 = self.f.add_subplot(grid[1:2, :])
        self.ax_extgauss = self.f.add_subplot(grid[2:, :])

        self.raster_prop(self.ax_L2)
        self.raster_prop(self.ax_L5)

        self.extgauss_prop()

    def extgauss_prop(self):
        self.ax_extgauss.set_yticklabels('')
        self.ax_extgauss.set_xlim(0, self.tstop)

    def raster_prop(self, ax):
        ax.set_yticklabels('')
        ax.set_xticklabels('')
        ax.set_xlim(0, self.tstop)

    def close(self):
        plt.close(self.f)

def testfn():
    testfig = fig_raster(100)
    # testfig = fig_std()

    x = np.random.rand(100)

    testfig.ax_L2.plot(x)
    # testfig.ax0.plot(x)
    plt.savefig('testing.png')
    testfig.close()

if __name__ == '__main__':
    testfn()
