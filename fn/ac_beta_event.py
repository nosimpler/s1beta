# ac_beta_event.py: Figure (axes creation) classes for beta events
# Author: Rob Law

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import axes_create as ac
import numpy as np
import matplotlib.patches as mpatches
from collections import defaultdict
import math

# Figure class for comparing evoked responses
# Plots mean and individual ERs in separate panels
class FigEvokedOnBeta(ac.FigBase):
    def __init__(self):
        ac.FigBase.__init__(self)

        self.f = plt.figure(figsize=(12, 6)) 
        self.set_fontsize(12)

        self.gs = {
            'main': gridspec.GridSpec(2, 3),
        }
        #self.gs['main'].update(wspace=0.2, hspace=0, bottom=0.05, top=0.95, left=0.05, right=0.95)

        self.ax = { 
            'individual': self.f.add_subplot(self.gs['main'][0, :]),
            'mean': self.f.add_subplot(self.gs['main'][1, :]),
            #'beta_event':self.f.add_subplot(self.gs['main'][:, 0]),
            }
        
        #TODO: title

# Figure for spike rasters for various post-event latencies/phases
class FigBetaPhaseSpikes(ac.FigBase):
    def __init__(self, n_phases, n_expmts):
        ac.FigBase.__init__(self)
        self.f = plt.figure(figsize=(12,6))
        self.set_fontsize(12)

        self.gs = {
                'main': gridspec.GridSpec(n_phases,n_expmts)
                }
        self.gs['main'].update(wspace=0.2, hspace = 0, bottom = 0.05, top = 0.95, left=0.05, right=0.95)
        self.ax = {}
        for j in range(n_expmts):
            for i in range(n_phases):
                self.ax[i,j] = self.f.add_subplot(self.gs['main'][i,j])
                #print dir(self.ax[i,j]
                #print dir(self.ax[i,j].spines['right'])
                self.ax[i,j].spines['right'].set_visible(False)
                self.ax[i,j].spines['left'].set_visible(False)
                self.ax[i,j].spines['top'].set_visible(False)
                self.ax[i,j].spines['bottom'].set_visible(False)
                self.ax[i,j].set_ylabel(str(i), rotation=0)

# Figures for latency-dependent evoked response
# Figs 6, 9A

class FigBetaPhase(ac.FigBase):

    def __init__(self, n_axes):
        ac.FigBase.__init__(self)

        self.f = plt.figure(figsize=(12, 6)) 
        self.set_fontsize(12)

        self.gs = {
            'main': gridspec.GridSpec(n_axes, 3),
        }
        #self.gs['main'].update(wspace=0.2, hspace=0, bottom=0.05, top=0.95, left=0.05, right=0.95)

        self.ax = { 
            #0: self.f.add_subplot(self.gs['main'][0, 1:]),
            'beta_event':self.f.add_subplot(self.gs['main'][:, 0]),
            }
        #add plots for each phase
        for i in range(n_axes):

            self.ax[i] = self.f.add_subplot(self.gs['main'][i, 1:])
            self.ax[i].spines['right'].set_visible(False)
            self.ax[i].spines['top'].set_visible(False)
            self.ax[i].spines['bottom'].set_visible(False)
            self.ax[i].spines['left'].set_visible(False)
            self.ax[i].set_yticks([])
            if i != n_axes -1:
                self.ax[i].set_xticklabels([])
            else:
                self.ax[i].spines['top'].set_visible(False)

# TODO: Figure class for viewing CSDs
#class FigCSD(ac.FigBase):
#    
#    def __init__(self):
#        self.f = plt.figure(figsize=(12,6))
#        self.set_fontsize(12)
#        self.gs = {
#                'main': gridspec.GridSpec(4,5)
#                }
#        self.ax = {
#                'cell_diagram': self.f.add_subplot(self.gs['main'][0, :]),
#                'CSD': self.f.add_subplot(self.gs['main'][0:-1, 1:-1]),
#                'dipole': self.f.add_subplot(self.gs['main'][-1, 1:-1]),
#                }

# Spike histogram figure

class FigSpikeHist(ac.FigBase):
    def __init__(self):
        self.f = plt.figure(figsize=(12,6))
        self.set_fontsize(12)
        self.gs = {
                'main': gridspec.GridSpec(2,1)
                }
        self.ax = {
                'L2': self.f.add_subplot(self.gs['main'][0,0]),
                'L5': self.f.add_subplot(self.gs['main'][1,0])
                }

# Plot classwise dipoles and spike histograms overlaid
# Figure 7

class FigClassDipoleWithSpikes(ac.FigBase):
    def __init__(self, n_classes, phases):
        self.phases = phases
        self.f = plt.figure(figsize=(12,6))
        self.set_fontsize(12)
        self.gs = {
                'main': gridspec.GridSpec(n_classes, 1)
                }
        self.ax = defaultdict(dict)
        for i in range(n_classes):
            self.ax[i]['dipole'] = self.f.add_subplot(self.gs['main'][i, 0])
            self.ax[i]['spikes'] = self.ax[i]['dipole'].twinx()   
    def normalize_spike_axes(self):
        factor = []
        for i,p in enumerate(self.phases):
            factor = 1./(len(p)+1)
            print factor
            
            labels = self.ax[i]['spikes'].get_yticks().tolist()
            ceiling = math.ceil(max(labels)*factor)
            print labels
            #newlabels = [label*factor for label in labels]
            self.ax[i]['spikes'].set_yticks([0, ceiling/factor])
            self.ax[i]['spikes'].set_yticklabels([0, int(ceiling)])
    def equalize_scales(self):
        ymax = []
        ymin = []
        spikemax = []
        n_classes = len(self.phases)
        for i in range(n_classes):
            print i
            lims = self.ax[i]['dipole'].get_ylim()
            spikemax.append(self.ax[i]['spikes'].get_ylim()[1])
            ymin.append(lims[0])
            ymax.append(lims[1])
            
        print ymin
        print ymax
        ymin = min(ymin)
        ymax = max(ymax)
        spikemax = max(spikemax)
        print ymin, ymax 
        for i in range(n_classes):
            self.ax[i]['dipole'].set_ylim([ymin, ymax])
            self.ax[i]['spikes'].set_ylim([0, spikemax*1.1])
            self.ax[i]['spikes'].set_yticks([spikemax])
            self.ax[i]['dipole'].set_yticks([ymin, ymax])

# Plot currents, voltages, etc. from individual neuron components 
# Needs to be unpacked and copy/pasted to generate Figure 9

class FigSectionTimeSeries(ac.FigBase):
    def __init__(self, section_list, cell_img = None):
    
        self.color = {}
        # hack - should be same # of colors as currents
        self.colorsc = plt.cm.Set1(np.linspace(0,1,9))
        # color is a dictionary from currents to color indices
        # then get actual color from cmap
        self.section_list = section_list
        #hack to get same scale
        #layer 5
        # for mean
        #ylims = [(-0.16,0.1642),(-0.14,1.),(-0.143,1.),(-0.157,1.),(-1.733,1.),(-0.24,9.92),(-0.155,1.),(-1.868,1.),(-1.868,1.)]
        # for indiv
       #ylims = [(-0.2,0.5),(-0.2,0.3),(-0.2,0.3),(-0.2,0.3),(-3,0.5),(-1.,15.),(-0.2,0.3),(-3.,0.5),(-3.,0.5)]
        #for layer 2
        #ylims = [(-0.2,0.5),(-0.2,0.3),(-0.2,0.3),(-3,0.5),(-1.,15.),(-0.2,0.3),(-3.,0.5),(-3.,0.5)]
        # for voltage layer 2
        ylims = [(-80,65)]*9
        self.ylims_dict = dict(zip(section_list, ylims))
        n_sections = len(section_list) + 1
        self.f = plt.figure(figsize=(12,6))
        self.set_fontsize(12)
        self.gs = {
                'main': gridspec.GridSpec(n_sections, 7)
                }
        self.ax = {
             #   'cell_diagram': self.f.add_subplot(self.gs['main'][:, 0]),
                'dipole': self.f.add_subplot(self.gs['main'][-1, 0:-2]),
                'legend': self.f.add_subplot(self.gs['main'][0::, -1])
                }
        sides = ['top', 'bottom', 'left', 'right']
        for side in sides:
            #self.ax['cell_diagram'].spines[side].set_visible(False)
            self.ax['legend'].spines[side].set_visible(False)
            self.ax['legend'].set_xticks([])
            self.ax['legend'].set_yticks([])
            if side != 'bottom':
                self.ax['dipole'].spines[side].set_visible(False)
        for i, section in enumerate(section_list):
            self.ax[section] = self.f.add_subplot(self.gs['main'][i,0:-2]) 
            self.ax[section].spines['top'].set_visible(False)
            self.ax[section].spines['right'].set_visible(False)
            self.ax[section].spines['bottom'].set_visible(False)
            self.ax[section].spines['left'].set_visible(False)
            #self.ax[section].set_yticks([])            
    def colormap(self, variable_string):
        if variable_string not in self.color.keys():
            n = len(self.color.keys())
            self.color[variable_string] = self.colorsc[n]
       
        return self.color[variable_string]
    def plot_outgoing_spikes(self, spiketimes, color='b'):
        ymin, ymax = self.ax[section].get_ylim()
        for st in spiketimes:
            self.ax['soma'].plot([st,st], [ymin, ymax], color = color, alpha = 0.2, linewidth = 1)

    def savefig(self, filename):
        self.f.savefig(filename)

    def set_section_labels(self):
        for section in self.section_list:
            self.ax[section].set_ylabel(section, rotation=0, fontsize=10)
    
    def set_vert_lines(self, times, reltimes):
        for axes in self.ax.iterkeys():
            if axes in self.section_list:
                ymin, ymax = self.ax[axes].get_ylim()
                for t in times:
                    self.ax[axes].plot([t,t], [ymin, ymax], color = 'black', alpha = 0.5, linewidth = 0.5)
                self.ax[axes].set_xticks(times, reltimes)
    def set_ticks(self):
        for axes in self.ax.iterkeys():
            if axes in self.section_list:
                self.ax[axes].yaxis.tick_right()
                ymin, ymax = self.ax[axes].get_ylim()
                #self.ax[axes].set_ylim(self.ylims_dict[axes])
                #self.ax[axes].set_yticks(self.ylims_dict[axes])
                #self.ax[axes].set_yticks([ymin, ymax])
                self.ax[axes].set_xticks([])
                self.ax[axes].tick_params(labelsize=8)
        self.ax['dipole'].set_xlim([0., 140.])
        self.ax['dipole'].set_yticks([])

        self.ax['dipole'].set_xticks([0,50,100])
        #self.ax['dipole'].set_xticks([25., 70., 135.])
    def set_legend(self):
        patches = {}
        for c in self.color.iterkeys():
            patches[c] = mpatches.Patch(color=self.color[c], label = c)
        self.ax['legend'].legend(handles = [p for p in patches.itervalues()], fontsize=14)
if __name__ == '__main__':
    #x = np.random.rand(1000)
    #fig = FigEvokedOnBeta()
    #fig.ax['individual'].plot(x, lw=0.5)
    #fig.show()
    pass
