# axes_create.py - simple axis creation
#
# v 1.8.9
# rev 2013-06-17 (SL: added new axis to the spec)
# last major: (MS: set_title() now uses external create_title() fn)

# usage:
# testfig = FigStd()
# testfig.ax0.plot(somedata)
# plt.savefig('testfig.png')
# testfig.close()

import paramrw
import matplotlib as mpl
# mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import itertools as it
import numpy as np

# Base figure class
class FigBase():
    def __init__(self):
        # self.f is typically set by the super class
        self.f = None

    # generic function to take an axis handle and make the y-axis even
    def ysymmetry(self, ax):
        ylim = ax.get_ylim()
        yabs_max = np.max(np.abs(ylim))
        ylim_new = (-yabs_max, yabs_max)
        ax.set_ylim(ylim_new)

        return ylim_new

    # set the font size globally
    def set_fontsize(self, s):
        font_prop = {
            'size': s,
        }

        mpl.rc('font', **font_prop)

    # creates title string based on params that change during simulation
    # title_str = ac.create_title(blah)
    # title_str = f.create_title(blah)
    def set_title(self, fparam, key_types):
        # get param dict
        p_dict = paramrw.read(fparam)[1]

        # create_title() is external fn
        title = create_title(p_dict, key_types)
        self.f.suptitle(title)

    # generic save png function to file_name at dpi=dpi_set
    def savepng(self, file_name, dpi_set=300):
        self.f.savefig(file_name, dpi=dpi_set)

    # generic save, works for png but supposed to be for eps
    def saveeps(self, file_name):
        self.f.savefig(file_name)

    # obligatory close function
    def close(self):
        plt.close(self.f)

# Simple one axis window
class FigStd(FigBase):
    def __init__(self):
        self.f = plt.figure(figsize=(12, 6))
        self.set_fontsize(8)

        gs0 = gridspec.GridSpec(1, 1)
        self.ax0 = self.f.add_subplot(gs0[:])

    def save(self, file_name):
        self.f.savefig(file_name)

class FigDplWithHist(FigBase):
    def __init__(self):
        self.f = plt.figure(figsize=(12, 6))
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

    def set_hist_props(self, hist_data):
        for key in self.ax.keys():
            if 'feed' in key:
                max_n = max(hist_data[key][0])
                self.ax[key].set_yticks(np.arange(0, max_n+2, np.ceil((max_n+2.)/4.)))

            if 'feed_dist' in key:
                self.ax[key].set_xticklabels('')

    def save(self, file_name):
        self.f.savefig(file_name)

# spec plus dipole plus alpha feed histograms
class FigSpecWithHist(FigBase):
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

# spec plus dipole 
class FigSpec(FigBase):
    def __init__(self):
        self.f = plt.figure(figsize=(8, 6))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        # the right margin is a hack and NOT guaranteed!
        # it's making space for the stupid colorbar that creates a new grid to replace gs1
        # when called, and it doesn't update the params of gs1
        self.gspec = {
            'dpl': gridspec.GridSpec(2, 1, height_ratios=[1, 3], bottom=0.85, top=0.95, left=0.1, right=0.82),
            'spec': gridspec.GridSpec(1, 4, wspace=0.05, hspace=0., bottom=0.30, top=0.80, left=0.1, right=1.),
            'pgram': gridspec.GridSpec(2, 1, height_ratios=[1, 3], bottom=0.05, top=0.25, left=0.1, right=0.82),
        }

        self.ax = {}
        self.ax['dipole'] = self.f.add_subplot(self.gspec['dpl'][:, :])
        self.ax['spec'] = self.f.add_subplot(self.gspec['spec'][:, :])
        self.ax['pgram'] = self.f.add_subplot(self.gspec['pgram'][:, :])

class FigFreqpwrWithHist(FigBase):
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

class FigRaster(FigBase):
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

class FigPSTH(FigBase):
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

# create a grid of psth figures, and rasters(?)
class FigGrid(FigBase):
    def __init__(self, N_rows, N_cols, tstop):
        self.tstop = tstop

        # changes over rows and cols to inches (?) and scales
        self.f = plt.figure(figsize=(2*N_cols, 2*N_rows))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        self.grid_list = []
        self.__create_grids(N_rows, N_cols)

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
        # print ypanel

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

class FigAggregateSpecWithHist(FigBase):
    def __init__(self, N_rows, N_cols):
        self.N_rows = N_rows
        self.N_cols = N_cols

        self.f = plt.figure(figsize=(2+8*N_cols, 1+8*N_rows), dpi=300)
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        # margins
        self.top_margin = 1. / (2 + 8 * N_rows)
        self.left_margin = 2. / (2 + 8 * N_cols)

        # Height is measured from top of figure 
        # i.e. row at top of figure is considered row 0
        # This is the opposite of matplotlib conventions
        # White space accounting is kind of wierd. Sorry.
        self.gap_height = 0.1 / (N_rows + 1)
        height = (0.9 - self.top_margin) / N_rows
        top = 1. - self.top_margin - self.gap_height
        bottom = top - height

        # Width is measured from left of figure
        # This is inline with matplotlib conventions 
        # White space accounting it kind of wierd. Sorry
        self.gap_width = 0.15 / (N_cols + 1.)
        width = (0.85 - self.left_margin) / N_cols
        left = self.left_margin + self.gap_width
        right = left + width

        # Preallocate some lists
        self.gs0_list = []
        self.gs1_list = []
        self.gs2_list = []
        self.ax_list = []

        # iterate over all rows/cols and create axes for each location
        for row, col in it.product(range(0, N_rows), range(0, N_cols)):
            # left and right margins for this set of axes
            tmp_left = left + width * col + self.gap_width * col 
            tmp_right = right + width * col + self.gap_width * col

            # top and bottom margins for this set of axes
            bottom_spec = bottom - height * row - self.gap_height * row
            top_spec = bottom_spec + (0.4 - self.top_margin / 5) / N_rows

            bottom_dpl = top_spec + (0.05 - self.top_margin / 5) / N_rows
            top_dpl = bottom_dpl + (0.2 - self.top_margin / 5) / N_rows

            bottom_hist = top_dpl + (0.05 - self.top_margin / 5) / N_rows
            top_hist = bottom_hist + (0.2 - self.top_margin / 5) / N_rows

            # tmp_top = top - height * row - self.gap_height * row
            # tmp_bottom = bottom - height * row - self.gap_height * row

            # Create gridspecs
            self.gs0_list.append(gridspec.GridSpec(1, 4, wspace=0., hspace=0., bottom=bottom_spec, top=top_spec, left=tmp_left, right=tmp_right))
            self.gs1_list.append(gridspec.GridSpec(2, 1, bottom=bottom_dpl, top=top_dpl, left=tmp_left, right=tmp_right-0.18/N_cols))
            self.gs2_list.append(gridspec.GridSpec(2, 1, hspace=0.14, bottom=bottom_hist, top=top_hist, left=tmp_left, right = tmp_right-0.18/N_cols))

            # create axes
            ax = {}
            ax['spec'] = self.f.add_subplot(self.gs0_list[-1][:, :])
            ax['dipole'] = self.f.add_subplot(self.gs1_list[-1][:, :])
            ax['feed_prox'] = self.f.add_subplot(self.gs2_list[-1][1, :])
            ax['feed_dist'] = self.f.add_subplot(self.gs2_list[-1][0, :])

            # store axes
            # SUPER IMPORTANT: this list iterates across rows!!!!!
            self.ax_list.append(ax)

    def set_hist_props(self, ax, hist_data):
        for key in ax.keys():
            if 'feed' in key:
                max_n = max(hist_data[key][0])
                ax[key].set_yticks(np.arange(0, max_n+2, np.ceil((max_n+2.)/4.)))

            if 'feed_dist' in key:
                ax[key].set_xticklabels('')

    # def add_column_labels(self, param_list):
    def add_column_labels(self, param_list, key): 
        # override = {'fontsize': 8*self.N_cols}

        gap = (0.85 - self.left_margin) / self.N_cols + self.gap_width 
        
        for i in range(0, self.N_cols):
            p_dict = paramrw.read(param_list[i])[1]

            x = self.left_margin + gap / 2. + gap * i
            y = 1 - self.top_margin / 2.

            self.f.text(x, y, key+' :%2.1f' %p_dict[key], fontsize=36, horizontalalignment='center', verticalalignment='top')

            # self.ax_list[i]['feed_dist'].set_title(key + ': %2.1f' %p_dict[key], **override)

    def add_row_labels(self, param_list, key):
        gap = (0.9 - self.top_margin) / self.N_rows + self.gap_height

        for i in range(0, self.N_rows):
            ind = self.N_cols * i
            p_dict = paramrw.read(param_list[ind])[1]

            # place text in middle of each row of axes
            x = self.left_margin / 2.
            y = 1. - self.top_margin - self.gap_height - gap / 2 - gap * i

            try:
                if len(key) == self.N_rows:
                    self.f.text(x, y, key[i], fontsize=36, rotation='vertical', horizontalalignment='left', verticalalignment='center')

                else:
                    print "Not enough row labels passed. Not using any"
                    return 0

            except TypeError:
                self.f.text(x, y, key+': %s' %p_dict[key], fontsize=36, rotation='vertical', horizontalalignment='left', verticalalignment='center')

    def save(self, file_name):
        self.f.savefig(file_name, dpi=250)

# aggregate figures for the experiments
class FigDipoleExp(FigBase):
    def __init__(self, ax_handles):
        # ax_handles is a list of axis handles in order
        # previously called N_expmt_groups for legacy reasons (original intention)
        # now generally repurposed for arbitrary numbers of axes with these handle names
        self.ax_handles = ax_handles
        self.N_expmt_groups = len(ax_handles)
        self.f = plt.figure(figsize=(8, 2*self.N_expmt_groups))
        font_prop = {'size': 8}
        mpl.rc('font', **font_prop)

        # create a gridspec that has width of "50"
        # there is some dark magic here whereby colorbars change the original axis by some
        # unspecified dimension. Rescaling non-spec axes to 40/50 is not the same as rescaling
        # non-spec axes 4/5, for reason that's unclear to me at the time of this writing
        # 40/50 works though
        # 'spec' must be specified in the name of the spec
        self.gspec = gridspec.GridSpec(self.N_expmt_groups, 55)
        self.__create_axes()
        self.__set_ax_props()

    def __create_axes(self):
        # self.ax = [self.f.add_subplot(self.gspec[i:(i+1)]) for i in range(self.N_expmt_groups)]
        self.ax = dict.fromkeys(self.ax_handles)

        # iterating like this because indices are useful in defining the recursive gspec locations
        i = 0
        for ax in self.ax_handles:
            if 'spec' not in ax:
                self.ax[ax] = self.f.add_subplot(self.gspec[i:(i+1), :20])
                self.ax[ax+'_L5'] = self.f.add_subplot(self.gspec[i:(i+1), 30:50])
                # self.ax[ax] = self.f.add_subplot(self.gspec[i:(i+1), :40])
            else:
                self.ax[ax] = self.f.add_subplot(self.gspec[i:(i+1), :25])
                self.ax[ax+'_L5'] = self.f.add_subplot(self.gspec[i:(i+1), 30:])
                # self.ax[ax] = self.f.add_subplot(self.gspec[i:(i+1), :])

            i += 1

        # if ax_twinx keys exist, the keys will mirror those in self.ax
        self.ax_twinx = {}

    # extern function to create a colorbar on an arbitrary axis
    # creates and rescales the specified axis and then scales down the rest of the axes accordingly
    # I hope
    def create_colorbar_axis(self, ax_name):
        # print self.ax[N_ax]
        cax, kw = mpl.colorbar.make_axes_gridspec(self.ax[ax_name])
        # a = self.ax[N_ax].get_axes()
        # for item in dir(self.ax[N_ax]):
        #     if not item.startswith('__'):
        #         print item

    # take an external list of dipoles and plot them
    # such a list is created externally
    def plot(self, t, dpl_list):
        if len(dpl_list) == self.N_expmt_groups:
            # list of max and min dipoles for each in dpl_list
            dpl_max = []
            dpl_min = []

            # check on all the mins and maxes
            for dpl, ax_name in it.izip(dpl_list, self.ax_handles):
                self.ax[ax_name].plot(t, dpl)
                ylim_tmp = ax.get_ylim()

                dpl_min.append(ylim_tmp[0])
                dpl_max.append(ylim_tmp[1])

            # find the overall min and max
            ymin = np.min(dpl_min)
            ymax = np.max(dpl_max)

            # set the ylims for all, the same
            for ax_name in self.ax.keys():
                self.ax[ax_name].set_ylim((ymin, ymax))

    # creates a twinx axis for the specified axis
    def create_axis_twinx(self, ax_name):
    # def create_axis_twinx(self, n):
        # if n < len(self.ax):
        # self.ax_twinx.append(self.ax[n].twinx())
        if ax_name in self.ax.keys():
            self.ax_twinx[ax_name] = self.ax[ax_name].twinx()

            # returns the index of most recently added element (now the length)
            return ax_name

        else:

            # returns valid axis name ONLY if it existed
            # otherwise, None will break other code
            return None

    def __set_ax_props(self):
        # remove xtick labels for everyone but the last axis
        for ax_name in self.ax_handles[:-1]:
            self.ax[ax_name].set_xticklabels('')
        # for ax in self.ax[:-1]:
        #     ax.set_xticklabels('')

# creates title string based on params that change during simulation
# title_str = ac.create_title(blah)
# title_str = f.create_title(blah)
def create_title(p_dict, key_types):
    title = []

    for key in key_types['dynamic_keys']:
        # Rules for when to use scientific notation
        if p_dict[key] >= 0.1 or p_dict[key] == 0:
            title.append(key + ': %2.1f' %p_dict[key])
        else:
            title.append(key + ': %2.1e' %p_dict[key])

    # Return string in alphabetical order
    title.sort()
    return title

# just a quick test for running this function
def testfn():
    x = np.random.rand(100)

    # testfig = FigStd()
    # testfig.ax0.plot(x)

    ax_handles = [
        'spec',
        'test1',
        'test2',
    ]

    # testfig = FigDipoleExp(ax_handles)
    # testfig.create_colorbar_axis('spec')
    # testfig.create_colorbar_axis('spectest')
    # testfig.ax['spec'].plot(x)

    # testfig = FigSpecWithHist()
    # testfig = FigAggregateSpecWithHist(3, 3)
    # testfig.ax['spec'].plot(x)

    # testfig = FigSpecWithHist()
    # testfig.ax['spec'].plot(x)
    # testfig.ax0.plot(x)

    # testfig = FigGrid(3, 3, 100)

    # testfig = FigPSTH(100)
    # testfig.ax['L5_extpois'].plot(x)

    testfig = FigSpec()
    testfig.ax['dipole'].plot(x)

    plt.savefig('testing.png', dpi=250)
    testfig.close()

if __name__ == '__main__':
    testfn()
