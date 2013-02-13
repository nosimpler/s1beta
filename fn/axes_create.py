# axes_create.py - simple axis creation
#
# v 1.7.19
# rev 2013-02-13 (MS: figure for plotting alpha feed hists next to freq-pwr analyis)
# last major: (SL: Incomplete changes to FigRaster)

# usage:
# testfig = FigStd()
# testfig.ax0.plot(somedata)
# plt.savefig('testfig.png')
# testfig.close()

import matplotlib as mpl
# mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

class FigStd():
    def __init__(self):
        self.f = plt.figure(figsize = (12, 6))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        gs0 = gridspec.GridSpec(1, 1)
        self.ax0 = self.f.add_subplot(gs0[:])

    def save(self, file_name):
        self.f.savefig(file_name)

    def savepng(self, file_name, dpi_set=300):
        self.f.savefig(file_name, dpi=dpi_set)

    def close(self):
        plt.close(self.f)

class FigDplWithHist():
    def __init__(self):
        self.f = plt.figure(figsize = (12, 6))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        # dipole gridpec
        self.gs0 = gridspec.GridSpec(1, 1, wspace=0.05, hspace=0, bottom=0.10, top=0.55, left = 0.1, right = 0.90)

        # hist gridspec
        self.gs1 = gridspec.GridSpec(2, 1, hspace=0.14 , bottom=0.60, top=0.95, left = 0.1, right = 0.90)

        # create axes
        self.ax = {}
        self.ax['dipole'] = self.f.add_subplot(self.gs0[:, :])
        self.ax['feed_prox'] = self.f.add_subplot(self.gs1[1, :])
        self.ax['feed_dist'] = self.f.add_subplot(self.gs1[0, :])

        # self.__set_hist_props()

        # self.ax['feed_prox'].set_xticklabels('')
        # self.ax['feed_dist'].set_xticklabels('')

    def set_hist_props(self, hist_data):
        for key in self.ax.keys():
            if 'feed' in key:
                max_n = max(hist_data[key][0])
                self.ax[key].set_yticks(np.arange(0, max_n+2, np.ceil((max_n+2.)/4.)))

            if 'feed_dist' in key:
                self.ax[key].set_xticklabels('')

    # def __set_hist_props(self):
    #     for key in self.ax.keys():
    #         if 'feed_dist' in key:
    #             self.ax[key].set_xticklabels('')
    #             # self.ax[key].set_yticklabels

    def save(self, file_name):
        self.f.savefig(file_name)

    def savepng(self, file_name, dpi_set=300):
        self.f.savefig(file_name, dpi=dpi_set)

    def close(self):
        plt.close(self.f)

# spec plus dipole plus alpha feed histograms
class FigSpecWithHist():
    def __init__(self):
        self.f = plt.figure(figsize=(8, 8))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        # the right margin is a hack and NOT guaranteed!
        # it's making space for the stupid colorbar that creates a new grid to replace gs1
        # when called, and it doesn't update the params of gs1
        self.gs0 = gridspec.GridSpec(1, 4, wspace=0.05, hspace=0., bottom=0.05, top=0.45, left=0.1, right=1.)
        self.gs1 = gridspec.GridSpec(2, 1, height_ratios=[1, 3], bottom=0.50, top=0.70, left=0.1, right=0.82)
        self.gs2 = gridspec.GridSpec(2, 1, hspace=0.14, bottom=0.75, top=0.95, left = 0.1, right = 0.82)

        self.ax = {}
        self.ax['spec'] = self.f.add_subplot(self.gs0[:, :])
        self.ax['dipole'] = self.f.add_subplot(self.gs1[:, :])
        self.ax['feed_prox'] = self.f.add_subplot(self.gs2[1, :])
        self.ax['feed_dist'] = self.f.add_subplot(self.gs2[0, :])

        # self.__set_hist_props()

    def set_hist_props(self, hist_data):
        for key in self.ax.keys():
            if 'feed' in key:
                max_n = max(hist_data[key][0])
                self.ax[key].set_yticks(np.arange(0, max_n+2, np.ceil((max_n+2.)/4.)))

            if 'feed_dist' in key:
                self.ax[key].set_xticklabels('')

    def close(self):
        plt.close(self.f)

# spec plus dipole 
class FigSpec():
    def __init__(self):
        self.f = plt.figure(figsize = (8, 6))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        # the right margin is a hack and NOT guaranteed!
        # it's making space for the stupid colorbar that creates a new grid to replace gs1
        # when called, and it doesn't update the params of gs1
        self.gs0 = gridspec.GridSpec(2, 1, height_ratios=[1, 3], bottom=0.65, top=0.95, left=0.1, right=0.82)
        self.gs1 = gridspec.GridSpec(1, 4, wspace=0.05, hspace=0., bottom=0.10, top=0.60, left=0.1, right=1.)

        self.ax = {}
        self.ax['dipole'] = self.f.add_subplot(self.gs0[:, :])
        self.ax['spec'] = self.f.add_subplot(self.gs1[:, :])

    def close(self):
        plt.close(self.f)

class FigFreqpwrWithHist():
    def __init__(self):
        self.f = plt.figure(figsize = (12, 6))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        # One gridspec for both plots
        self.gs0 = gridspec.GridSpec(1, 2, bottom=0.20, top = 0.80, left=0.1, right=0.90, wspace = 0.1)

        self.ax = {}
        self.ax['freqpwr'] = self.f.add_subplot(self.gs0[0, 1])
        self.ax['hist'] = self.f.add_subplot(self.gs0[0, 0])

    def set_hist_props(self, hist_data):
        max_n = max(hist_data)
        self.ax['hist'].set_yticks(np.arange(0, max_n+2, np.ceil((max_n+2.)/4.)))

    def save(self, file_name):
        self.f.savefig(file_name)

    def close(self):
        plt.close(self.f)

class FigRaster():
    def __init__(self, tstop):
        self.tstop = tstop
        self.f = plt.figure(figsize=(6, 8))

        grid0 = gridspec.GridSpec(5, 1)
        grid0.update(wspace=0.05, hspace=0., bottom=0.05, top=0.45)

        grid1 = gridspec.GridSpec(5, 1)
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
        self.ax[layer+'_extpois'] = self.f.add_subplot(grid[3:4, :])
        self.ax[layer+'_extinput'] = self.f.add_subplot(grid[4:, :])

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

# create a grid of psth figures, and rasters(?)
class fig_psthgrid():
    def __init__(self, N_rows, N_cols, tstop):
        self.tstop = tstop

        # changes over rows and cols to inches (?) and scales
        self.f = plt.figure(figsize=(2*N_cols, 2*N_rows))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        self.grid_list = []
        self.__create_grids(N_rows, N_cols)
        # self.__create_grids(4, 5)

        # axes are a list of lists here
        self.ax = []
        self.__create_axes()

    def __create_grids(self, N_rows, gs_cols):
        gs_rows = 3
        self.grid_list = [gridspec.GridSpec(gs_rows, gs_cols) for i in range(N_rows)]
        ytop = 0.075
        ybottom = 0.05
        ypad = 0.02
        ypanel = (1 - ytop - ybottom - ypad*(N_rows-1)) / N_rows
        print ypanel

        i = 0
        ystart = 1-ytop

        # used to pre-calculate this, but whatever
        for grid in self.grid_list:
            # start at the top to order the rows down
            grid.update(wspace=0.05, hspace=0., bottom=ystart-ypanel, top=ystart)
            # grid.update(wspace=0.05, hspace=0., bottom=0.05, top=0.95)
            ystart -= ypanel+ypad
            i += 1

    # creates a list of lists of axes
    def __create_axes(self):
        for grid in self.grid_list:
            ax_list = []
            for i in range(grid._ncols):
                ax_list.append(self.f.add_subplot(grid[:, i:i+1]))
                ax_list[-1].set_yticks([0, 100., 200., 300., 400., 500.])

                # clear y-tick labels for everyone but the bottom
                for ax in ax_list:
                    ax.set_xticklabels('')

            # clear y-tick labels for everyone but the left side
            for ax in ax_list[1:]:
                ax.set_yticklabels('')
            self.ax.append(ax_list)

        # set a timescale for just the last axis
        self.ax[-1][-1].set_xticks([0., 250., 500.])
        self.ax[-1][-1].set_xticklabels([0., 250., 500.])

        # testing usage of string in title
        # self.ax[0][0].set_title(r'$\lambda_i$ = %d' % 0)

    def close(self):
        plt.close(self.f)

def testfn():
    x = np.random.rand(100)

    # testfig = FigStd()
    # testfig.ax0.plot(x)

    testfig = FigRaster(100)
    testfig.ax['L5'].plot(x)

    # testfig = FigSpecWithHist()
    # testfig.ax['spec'].plot(x)
    # testfig.ax0.plot(x)

    # testfig = fig_psth(100)
    # testfig.ax['L5_extpois'].plot(x)

    plt.savefig('testing.png')
    testfig.close()

if __name__ == '__main__':
    testfn()
