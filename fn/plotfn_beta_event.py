# plotfn_beta_event.py: Plotting calls for Law, et al 2020(?)
# Author: Rob Law

import fileio
import proc_beta_event as proc
import ac_beta_event as ac
import matplotlib.pyplot as plt
import spikefn
from numpy import array, linspace, dot, mean, zeros, pad, diff, histogram
import os
import time
import itertools as it
from scipy import signal, histogram
from scipy import io as sio
from scipy.optimize import nnls
from scipy.signal import resample
import math
from tvregdiff import *
import math
#compare high vs. low beta conditions
# i.e. event vs. no-event
def plot_evoked_on_beta(dfig, dproj, d_evoked_sim, d_event_sim, t_interval):
    fig = ac.FigEvokedOnBeta()
    #colordict = {'beta_low': [0.,0.447, 0.741], 'beta_high': [0.85, 0.325, 0.098], 'prox':'r', 'dist': 'm'}
    #plot time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim)
    colordict = get_colordict(evoked_avg_dpl)
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        if expmt in ['beta_high', 'beta_low']:
            fig.ax['mean'].plot(t_evoked, evoked_avg_dpl[expmt], label=expmt, color=colordict[expmt])
            for f in evoked_dpls[expmt]:
                fig.ax['individual'].plot(t_evoked, evoked_dpls[expmt][f], color=colordict[expmt])
    fig.ax['mean'].legend()
    
    #plot event dipole
    event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
    for expmt in event_dpl:
        fig.ax['beta_event'].plot(event_t, event_dpl[expmt], color=colordict[expmt])
    plt.show(fig)
    fig.f.savefig(dfig+'evoked_on_beta.pdf')
    fig.close()

# set color dictionary
def get_colordict(expmts):
    colorlist = [[0., 0.447, 0.741],
            [0.85, 0.325, 0.098],
            'r',
            'm',
            'y',
            'g',
            'k',
            'b',
            'k']
    # hack for reverse order
    #colorlist = colorlist[-1:0:-1]
    colordict = {}
    for idx, key in enumerate(sorted(expmts.keys())):
        colordict[key] = colorlist[idx]
    return colordict

# plot mean ERP over latencies (Fig 6)
def plot_mean_ERP(dfig, dproj, d_evoked_sim, window = False):
    fig = ac.FigEvokedOnBeta()
    #colordict = {'0': 'b'}
    #colordict = {'8e-5': [0.,0.447, 0.741], '12e-5': [0.85, 0.325, 0.098], '24e-5':'r', 'dist': 'm'}
    #plot time-locked average dipoles and individual dipoles
    
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim, window)    
    
    
    colordict = get_colordict(evoked_avg_dpl)
    colors = plt.cm.brg(linspace(0,1,len(evoked_avg_dpl.keys())))
    scale = 1.0
    data_low = np.squeeze(sio.loadmat('/repo/data/s1/mean_low.mat')['mean_low'])
    data_high = np.squeeze(sio.loadmat('/repo/data/s1/mean_high.mat')['mean_high'])
    datatime = np.linspace(0,250,150)
   
    #model_resample = resample(evoked_avg_dpl['nobeta'], 150)
    #print model_resample.shape, data_low.shape
    #scale, res = nnls(np.asmatrix(model_resample).T, data_low) 
    
#    for idx, expmt in enumerate(sorted(evoked_avg_dpl.keys())):
#        colordict[expmt] = colors[idx]
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        
        if expmt in colordict.keys():
            alldpls = []
            
#            evoked_avg_dpl[expmt] = proc.window_dipole(evoked_avg_dpl[expmt]) 
            fig.ax['mean'].plot(t_evoked, evoked_avg_dpl[expmt]*scale, label=expmt, color=colordict[expmt], linewidth = 3)
            for f in evoked_dpls[expmt]:
                #hack 
                
                fig.ax['individual'].plot(t_evoked, evoked_dpls[expmt][f]*scale, color=colordict[expmt], linewidth = 1)
                alldpls.append(evoked_dpls[expmt][f])
            alldpls = np.array(alldpls)
            sio.savemat(dfig+'expmt_' + str(expmt) + '_mean_and_all_phases.mat', {'meandpl': evoked_avg_dpl, 'dpl': alldpls})
    fig.ax['mean'].legend(loc=1, fontsize = 'xx-small')
    fig.ax['mean'].text(0.1, 0.1, str(scale))
     
    #fig.ax['mean'].plot(datatime[0:100], data_low[0:100], 'b')
    #fig.ax['mean'].plot(datatime[0:100], data_high[0:100], 'r')
    #fig.ax['mean'].set_ylim([-10000, 20000])
    #plot event dipole
    #event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
    #for expmt in event_dpl:
    #    fig.ax['beta_event'].plot(event_t, event_dpl[expmt], color=colordict[expmt])
    plt.show(fig)
    fig.f.savefig(dfig+'ERP.pdf')
    fig.close()
    
#compare phases and high/low beta variances (not used in paper)
def plot_var_ERP(dfig, dproj, d_evoked_sim, window = False):
    fig = ac.FigEvokedOnBeta()
    #colordict = {'0': 'b'}
    #colordict = {'8e-5': [0.,0.447, 0.741], '12e-5': [0.85, 0.325, 0.098], '24e-5':'r', 'dist': 'm'}
    #plot time-locked average dipoles and individual dipoles
    
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim, window)    
    
    
    colordict = get_colordict(evoked_avg_dpl)
    colors = plt.cm.brg(linspace(0,1,len(evoked_avg_dpl.keys())))
    #scale = 18000.*1e-15
    #data_low = np.squeeze(sio.loadmat('/repo/data/s1/var_low.mat')['var_low'])
    #data_high = np.squeeze(sio.loadmat('/repo/data/s1/var_high.mat')['var_high'])
    #datatime = np.linspace(0,250,150)
   
    #model_resample = resample(evoked_avg_dpl['nobeta'], 150)
    #print model_resample.shape, data_low.shape
    #scale, res = nnls(np.asmatrix(model_resample).T, data_low) 
    
#    for idx, expmt in enumerate(sorted(evoked_avg_dpl.keys())):
#        colordict[expmt] = colors[idx]
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        
        if expmt in colordict.keys():
            alldpls = []
            
            evoked_avg_dpl[expmt] = proc.window_dipole(evoked_avg_dpl[expmt]) 
            for f in evoked_dpls[expmt]:
                fig.ax['individual'].plot(t_evoked, evoked_dpls[expmt][f], color=colordict[expmt], linewidth = 1)
                alldpls.append(evoked_dpls[expmt][f])
            
            alldpls = np.array(alldpls)
            variance = np.var(alldpls, axis = 0)
            fig.ax['mean'].plot(t_evoked, variance, color = colordict[expmt], linewidth = 2)
            sio.savemat(dfig+'expmt_' + str(expmt) + '_mean_and_all_phases.mat', {'meandpl': evoked_avg_dpl, 'dpl': alldpls})
    fig.ax['mean'].legend(loc=1, fontsize = 'xx-small')
    #fig.ax['mean'].text(0.1, 0.1, str(scale))
     
    #fig.ax['mean'].plot(datatime[0:100], data_low[0:100], 'b')
    #fig.ax['mean'].plot(datatime[0:100], data_high[0:100], 'r')
    #fig.ax['mean'].set_ylim([-10000, 20000])
    #plot event dipole
    #event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
    #for expmt in event_dpl:
    #    fig.ax['beta_event'].plot(event_t, event_dpl[expmt], color=colordict[expmt])
    plt.show(fig)
    fig.f.savefig(dfig+'ERP_var.pdf')
    fig.close()
    
#compare phases and high/low beta PSDs

def plot_PSD_phase(dfig, dproj, d_evoked_sim, whichexpmt, phases):
    fig = ac.FigEvokedOnBeta()
    colordict = {}
    colordict = {0: [0.,0.447, 0.741], 1: [0.85, 0.325, 0.098]}
    #plot time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim)    
    
    # use this if using diff. comment out if using tdiff
    t_evoked = t_evoked.tolist()
    #t_evoked.pop()
    colors = plt.cm.brg(linspace(0,1,len(evoked_avg_dpl.keys())))
#    for idx, expmt in enumerate(sorted(evoked_avg_dpl.keys())):
#        colordict[expmt] = colors[idx]
    avg = [zeros(10001), zeros(10001)]
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        if expmt == whichexpmt:
            for i, ph in enumerate(phases):
                for phase in ph:
                    n = len(ph)
                    dip = evoked_dpls[expmt][phase]
                    fig.ax['individual'].plot(t_evoked, dip, color=colordict[i], linewidth = 1)
                    avg[i] = avg[i] + dip/n
                fig.ax['mean'].plot(t_evoked, avg[i], label=expmt, color=colordict[i], linewidth = 3)
    fig.ax['mean'].legend(loc=2)

# latency-dependent ER (overlaid)
def plot_ERP_phase(dfig, dproj, d_evoked_sim, whichexpmt, phases):
    fig = ac.FigEvokedOnBeta()
    colordict = {}
    #plot time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim)    
     
    colordict = get_colordict(evoked_avg_dpl)
    # use this if using diff. comment out if using tdiff
    t_evoked = t_evoked.tolist()
    #t_evoked.pop()
    colors = plt.cm.brg(linspace(0,1,len(evoked_avg_dpl.keys())))
#    for idx, expmt in enumerate(sorted(evoked_avg_dpl.keys())):
#        colordict[expmt] = colors[idx]
    avg = [zeros(10001), zeros(10001)]
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        if expmt == whichexpmt:
            for i, ph in enumerate(phases):
                for phase in ph:
                    n = len(ph)
                    dip = evoked_dpls[expmt][phase]
                    fig.ax['individual'].plot(t_evoked, dip, color=colordict[i], linewidth = 1)
                    avg[i] = avg[i] + dip/n
                fig.ax['mean'].plot(t_evoked, avg[i], label=expmt, color=colordict[i], linewidth = 3)
    fig.ax['mean'].legend(loc=2)

    #plot event dipole
    #event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
    #for expmt in event_dpl:
    #    fig.ax['beta_event'].plot(event_t, event_dpl[expmt], color=colordict[expmt])
    plt.show(fig)
    fig.f.savefig(dfig+'ERP.pdf')
    fig.close()

# phase dependent ER time-derivative (overlaid)
def plot_ERP_derivative_phase(dfig, dproj, d_evoked_sim, whichexpmt, phases):
    fig = ac.FigEvokedOnBeta()
    colordict = {}
    colordict = {0: [0.,0.447, 0.741], 1: [0.85, 0.325, 0.098]}
    #plot time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim)    
    
    # use this if using diff. comment out if using tdiff
    t_evoked = t_evoked.tolist()
    t_evoked.pop()
    colors = plt.cm.brg(linspace(0,1,len(evoked_avg_dpl.keys())))
#    for idx, expmt in enumerate(sorted(evoked_avg_dpl.keys())):
#        colordict[expmt] = colors[idx]
    avg = [zeros(10000), zeros(10000)]
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        if expmt == whichexpmt:
            for i, ph in enumerate(phases):
                for phase in ph:
                    n = len(ph)
                    _diff = diff(evoked_dpls[expmt][phase])
                    fig.ax['individual'].plot(t_evoked, _diff, color=colordict[i], linewidth = 1)
                    avg[i] = avg[i] + _diff/n
                fig.ax['mean'].plot(t_evoked, avg[i], label=expmt, color=colordict[i], linewidth = 3)
    fig.ax['mean'].legend(loc=2)

    #plot event dipole
    #event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
    #for expmt in event_dpl:
    #    fig.ax['beta_event'].plot(event_t, event_dpl[expmt], color=colordict[expmt])
    plt.show(fig)
    fig.f.savefig(dfig+'ERP-derivative.pdf')
    fig.close()
#compare phases and high/low

# Mean ER derivatives
def plot_ERP_derivative(dfig, dproj, d_evoked_sim, window = False):
    fig = ac.FigEvokedOnBeta()
    colordict = {}
    #colordict = {'8e-5': [0.,0.447, 0.741], '12e-5': [0.85, 0.325, 0.098], '24e-5':'r', 'dist': 'm'}
    
    scale = 1.0
    #datatime = np.linspace(0,250,150)
    #data_low = np.squeeze(sio.loadmat('/repo/data/s1/der_mean_low.mat')['X_der_mean_low'])
    #data_high = np.squeeze(sio.loadmat('/repo/data/s1/der_mean_high.mat')['X_der_mean_high'])
    #plot time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim, window)    
    colordict = get_colordict(evoked_avg_dpl)
    # use this if using diff. comment out if using tdiff
    t_evoked = t_evoked.tolist()
    t_evoked.pop()
    colors = plt.cm.brg(linspace(0,1,len(evoked_avg_dpl.keys())))
#    for idx, expmt in enumerate(sorted(evoked_avg_dpl.keys())):
#        colordict[expmt] = colors[idx]
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        if expmt in colordict.keys():
            fig.ax['mean'].plot(t_evoked, diff(evoked_avg_dpl[expmt])*scale, label=expmt, color=colordict[expmt], linewidth = 3)
            for f in evoked_dpls[expmt]:
                fig.ax['individual'].plot(t_evoked, diff(evoked_dpls[expmt][f])*scale, color=colordict[expmt], linewidth = 1)
    #fig.ax['mean'].legend(loc=2)

    #fig.ax['mean'].plot(datatime[0:100], -data_low[0:100], 'b')
    #fig.ax['mean'].plot(datatime[0:100], -data_high[0:100], 'r')
    #plot event dipole
    #event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
    #for expmt in event_dpl:
    #    fig.ax['beta_event'].plot(event_t, event_dpl[expmt], color=colordict[expmt])
    plt.show(fig)
    fig.f.savefig(dfig+'ERP-derivative.pdf')
    fig.close()
#compare phases and high/low

# mean PSDs
def plot_mean_PSD(dfig, dproj, d_evoked_sim):
    fig = ac.FigEvokedOnBeta()
    #fig = plt.Figure()
    colordict = {}
    colordict = {'8e-5': [0.,0.447, 0.741], '12e-5': [0.85, 0.325, 0.098], '25e-5':'r', 'dist': 'm'}
    #plot time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim)
    psd = []
    #psdmean = zeros((1,len(t_evoked)))
    colors = plt.cm.brg(linspace(0,1,len(evoked_avg_dpl.keys())))
    fs = 40000
#    for idx, expmt in enumerate(sorted(evoked_avg_dpl.keys())):
#        colordict[expmt] = colors[idx]
    winsize = 2048
    window = signal.slepian(winsize, 0.005)
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        if expmt in colordict.keys():
            #fr, psd = signal.welch(evoked_avg_dpl[expmt][0:winsize], fs = fs, nperseg = winsize, noverlap = winsize-1)            
            #fig.ax['mean'].semilogy(fr[fr<500], psd[fr<500], color=colordict[expmt], linewidth = 3)            
            # psd of mean, not mean of psd
            #print psd_mean
            mean_psd = zeros((winsize/2+1,1))
            for f in evoked_dpls[expmt]:
                fr, psd = signal.welch(pad(evoked_dpls[expmt][f][0:7500],5000, mode ='constant'), fs = fs, nperseg = winsize, noverlap = winsize - 1, window = window)
                mean_psd = mean_psd + psd/len(evoked_dpls[expmt]) 
                fig.ax['individual'].semilogy(fr[fr<500], psd[fr<500], color=colordict[expmt], linewidth = 1)
            fig.ax['mean'].semilogy(fr[fr<500], mean_psd.T[fr<500], color = colordict[expmt], linewidth = 3)

#fig.ax['mean'].legend(loc=2)

    #plot event dipole
    #event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
    #for expmt in event_dpl:
    #    fig.ax['beta_event'].plot(event_t, event_dpl[expmt], color=colordict[expmt])
    plt.show(fig)
    fig.f.savefig(dfig+'ERP-PSD.pdf')
    fig.close()

# Plot individual ERs for several latencies
# (as a function of latency)
def plot_multiphase(dfig, dproj, d_evoked_sim, d_event_sim, t_interval, window = False):
    #colordict = {'super_beta': 'k'}
    colordict = {'rest': [0.,0.447, 0.741], 'beta': [0.85, 0.325, 0.098], 'beta2':'r', 'prox_only': 'm'}
    
    #get time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim, window)
    #colordict = get_colordict(evoked_avg_dpl)
    
    expmts = evoked_avg_dpl.keys()
    n_trials = len(evoked_dpls[expmts[0]])
    fig = ac.FigBetaPhase(n_trials)
    #colordict = {}
    colors = plt.cm.Set1(linspace(0,1,len(evoked_avg_dpl.keys())))
    #for idx, expmt in enumerate(sorted(evoked_avg_dpl.keys())):
    #    colordict[expmt] = colors[idx]
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        #fig.ax['mean'].plot(t_evoked, evoked_avg_dpl[expmt], label=expmt, color=colordict[expmt])
        for i_f, f in enumerate(evoked_dpls[expmt]):
            
            fig.ax[i_f].plot(t_evoked, evoked_dpls[expmt][f],
                    linewidth=1, color=colordict[expmt])
            #if i_f < n_trials-1:
                #fig.ax[i_f].set_xticklabels('')
            fig.ax[i_f].set_yticklabels('')

    #plot event dipole

    if d_event_sim is not None:
        event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
        for expmt in event_dpl:
            time = t_interval[-1] - t_interval[0]
            fig.ax['beta_event'].plot(event_dpl[expmt], event_t,
                    color=colordict[expmt], linewidth = 3, label=expmt)
            fig.ax['beta_event'].set_ylim(t_interval[-1] +
                    time/(2.*n_trials), t_interval[0] - time/(2.*n_trials))
    
    fig.ax['beta_event'].legend(loc='upper left')
    plt.show(fig)
    fig.f.savefig(dfig+'multiphase_beta.pdf')
    fig.close()

# Not used
def plot_three_class_phase(dfig, dproj, d_evoked_sim, d_event_sim, t_interval, phases_low, phases_high):
    #phases map to a color dictionary
    dfig = d_evoked_sim
    colordict = {'beta_low':
            {},
            'beta_high':
            {}
            }
    color_scheme = {}
    color_scheme['beta_low'] = ([0.,0.447,0.741],)
    color_scheme['beta_high'] = ([0.635, 0.078, 0.184],[0.929, 0.694, 0.125])
    for color_idx, p in enumerate(phases_low):
        for trial_idx in p:
            colordict['beta_low'][trial_idx] = color_scheme['beta_low'][color_idx]
    
    for color_idx, p in enumerate(phases_high):
        for trial_idx in p:
            colordict['beta_high'][trial_idx] = color_scheme['beta_high'][color_idx]

    #get time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim)
    expmts = evoked_avg_dpl.keys()
    n_trials = len(evoked_dpls[expmts[0]])
    
    offset = (t_interval[-1] - t_interval[0])/n_trials 
    print n_trials
    fig = ac.FigBetaPhase(n_trials)
    #colordict = {}
    colors = plt.cm.Set1(linspace(0,1,len(evoked_avg_dpl.keys())))
    #for idx, expmt in enumerate(sorted(evoked_avg_dpl.keys())):
    #    colordict[expmt] = colors[idx]
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        #fig.ax['mean'].plot(t_evoked, evoked_avg_dpl[expmt], label=expmt, color=colordict[expmt])
        for i_f, f in enumerate(evoked_dpls[expmt]):
            fig.ax[i_f].plot(t_evoked, evoked_dpls[expmt][f],
                    linewidth=2, color=colordict[expmt][i_f])
            if i_f < n_trials -1:
                fig.ax[i_f].set_xticklabels('')

            fig.ax[i_f].set_yticklabels('')

    #plot event dipole

    if d_event_sim is not None:
        event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
        
        for expmt in ['beta_low', 'beta_high']:
            
            time = t_interval[-1] - t_interval[0]
            l = len(colordict[expmt])
            for i,c in enumerate(colordict[expmt]): 
                t_idx = [math.floor(i*len(event_t)/l), math.floor((i+1)*len(event_t)/l)-1]
                print t_idx
                t = range(int(t_idx[0]), int(t_idx[1]))
                fig.ax['beta_event'].plot(event_dpl[expmt][t], event_t[t],
                    color=colordict[expmt][i], linewidth = 3)
                fig.ax['beta_event'].set_ylim(t_interval[-1] +
                    time/(2.*n_trials), t_interval[0] - time/(2.*n_trials))
    
    fig.ax['beta_event'].legend(loc='upper left')
    plt.show(fig)
    fig.f.savefig(dfig+'multiphase_beta.pdf')
    fig.close()

#plots n x 2 stimulus locked spike rasters
def plot_multiphase_spikes(dfig, dproj, d_evoked_sim, layer='L2'):
    t_interval_evoked, spikes = proc.get_time_locked_spikes(dproj, d_evoked_sim)
    filefig = dfig + layer + 'phase_spikes.pdf'
    #expmt_map = {'beta_low': 0, 'beta_high': 1}
    expmts = sorted(spikes.keys())
    n_trials = len(spikes[expmts[0]]) 
    print n_trials
    print len(expmts)
    expmt_map = dict(zip(expmts, range(len(expmts))))
    print expmt_map
    #expmt_map = dict(zip(['2e-5', '4e-5', '6e-5', '8e-5', '12e-5', '16e-5', '24e-5'], range(7)))
    fig = ac.FigBetaPhaseSpikes(n_trials, len(expmts))
    s_dict = {}
    print spikes.keys()
    for expmt in spikes.keys():
      
        for f_idx in spikes[expmt]:
            a = fig.ax[f_idx, expmt_map[expmt]]
            if layer == 'L2':
                for key in spikes[expmt][f_idx]:
                    if key == 'L2_pyramidal' or key == 'L2_basket':
                        s_dict[key] = spikes[expmt][f_idx][key]
                
                #print s_dict.keys()
                spikefn.spike_png(a, s_dict)
            
            if layer == 'L5':
                for key in spikes[expmt][f_idx]:
                    if key == 'L5_pyramidal' or key == 'L5_basket':
                        s_dict[key] = spikes[expmt][f_idx][key]
                spikefn.spike_png(a, s_dict)
            a.set_xlim(t_interval_evoked[expmt][f_idx])
            #a.set_xticklabels('')
            a.set_yticklabels('')
            #a.set_yticks('')
           #a.set_xticks(None)
            #plt.setp(a.get_xticklabels(), visible = False)
            #a.xaxis.set_tick_params(size=0)
        
            xticks = [25, 70, 135]
            a.set_xticks([x+t_interval_evoked[expmt][f_idx][0] for x in xticks])
            a.set_xticklabels(xticks)
            a.xaxis.set_tick_params(size=20, color='g')
    plt.show(fig)
    fig.f.savefig(filefig)

# averaged currents at multiple latencies
def plot_multiphase_currents(dfig, dproj, d_evoked_sim, d_event_sim, t_interval, layer='L2_Pyr'):

    colordict = {'beta_low':'g', 'beta_high':'b'}
    #time-locked average dipoles and individual dipoles
    t_evoked, evoked_L2, evoked_L5, evoked_avg_L2, evoked_avg_L5 = proc.compare_time_locked_average_current(dproj, d_evoked_sim)
    if layer == 'L2_Pyr':
        evoked = evoked_L2
        evoked_avg = evoked_avg_L2
    if layer == 'L5_Pyr':
        evoked = evoked_L5
        evoked_avg = evoked_avg_L5
    n_trials = len(evoked_avg.keys()[0]) 
    fig = ac.FigBetaPhase(n_trials)
    for exp_idx, expmt in enumerate(evoked_avg.keys()):
        #fig.ax['mean'].plot(t_evoked, evoked_avg_dpl[expmt], label=expmt, color=colordict[expmt])
        for i_f, f in enumerate(evoked[expmt]):
            fig.ax[i_f].plot(t_evoked, evoked[expmt][f],
                    linewidth=2, color=colordict[expmt])
            fig.ax[i_f].set_xticklabels('')
            fig.ax[i_f].set_yticklabels('')

    #plot event dipole
    event_t, event_dpl = proc.compare_event_current(dproj, d_event_sim, t_interval, layer=layer)
    for expmt in event_dpl:
        if d_event_sim is not None:
            time = t_interval[-1] - t_interval[0]
            fig.ax['beta_event'].plot(event_dpl[expmt], event_t,
                    color=colordict[expmt], linewidth = 3, label=expmt)
            fig.ax['beta_event'].set_ylim(t_interval[-1] +
                    time/(2.*n_trials), t_interval[0] - time/(2.*n_trials))
    
    fig.ax['beta_event'].legend(loc='upper left')
    plt.show(fig)
    fig.savepng(dfig+'multiphase_beta.png')
    fig.close()

# currents for all segments
def plot_seg_currents(f, filefig, times, celltype, cellidx):
    #TODO: include image of cell

    t0 = times[0]
    T = times[4]
    #t0 = 0
    #T = 500 #for superthreshold currents 
    tff1 = times[1]
    tfb = times[2]
    tff2 = times[3]
    if celltype == 'L5':
        segment_list = ['apical_tuft', 'apical_1', 'apical_2',
                'apical_trunk', 'apical_oblique',
                'soma', 'basal_1', 'basal_2', 'basal_3']
    elif celltype == 'L2':
        
        segment_list = ['apical_tuft', 'apical_1',
                'apical_trunk', 'apical_oblique',
                'soma', 'basal_1', 'basal_2', 'basal_3']
    t, var = proc.get_currents(f)
    #I_mean, I_conf, I_samples = proc.get_stats(var, 1)
    print var[0].keys() 
    fig = ac.FigSectionTimeSeries(segment_list)
    #TODO: more than one cell, different timecourses
    t = array(t)
    #t0 = t0 + 70.0
    #T = t0 + 40.0
    interval_idx = t >= array(t0) 
    interval_idx2 = t <= array(T)
    # multiplication is intersection
    interval_idx = interval_idx*interval_idx2
    print interval_idx
    
    # uncomment and change segment names to generate Figure 7C,D
    for segment in segment_list:
    #for segment in ['apical_tuft']:
        for I in var[cellidx][segment].keys():
        #for I in ['i_ar', 'ampa', 'nmda']:    
            if I in ['gabaa','gabab', 'ampa', 'nmda']:
                # scaled according to L2 somatic surface area
                # scale = 1.62*1e-5
                # scaled according to L5 apical tuft area
                scale = 4.54*1e-5
            else:
                scale = 1.0
            current = scale*array(var[cellidx][segment][I])
            #print type(current)
            #print current.shape
            #print t.shape
            c = fig.colormap(I)
            fig.ax[segment].plot(t[interval_idx], current[interval_idx], color = c, linewidth=0.5)
            #fig.set_vert_lines([tff1,tfb, tff2], [25., 70., 135.])
            fig.set_legend()
            
            fig.set_ticks()
            fig.set_section_labels() 
    plt.show(block=False)
    plt.pause(30)
    fig.savefig(filefig)
    plt.close("all")

# runs plot_seg_currents for all files (takes a long time)
def plot_all_currents(dproj, dsim, dfig, celltype, cellidx):
    filedict, pdict, spikedict = proc.get_var_paths(dproj, dsim)
    for expmt in filedict.iterkeys():
        print filedict[expmt]        
        for i,f in enumerate(filedict[expmt]):
            print f
            print os.listdir(dfig)
            filename = expmt + '_segments_' + str(i) + '.pdf'
            filefig = os.path.join(dfig, filename)
            t = proc.time_lock_to_stimulus(pdict[expmt][i])
            plot_seg_currents(f, filefig, t, celltype, cellidx)

# plot currents at chosen latency (indices)
# x limits according to when perturbation occurred 
def plot_phase_currents(dproj, dsim, expmt, indices, celltype, cellidx):
    filedict, pdict, spikedict = proc.get_var_paths(dproj, dsim)

    print filedict
    for i,f in enumerate(filedict[expmt]):
        if i in indices:
            print f
            print os.listdir(dfig)
            filename = expmt + '_segments_trial_' + str(i) + '_cell_'+str(cellidx)+'.pdf'
            filefig = os.path.join(dfig, filename)
            # gets xlim and incoming spike times
            t = proc.time_lock_to_stimulus(pdict[expmt][i])
            plot_seg_currents(f, filefig, t, celltype, cellidx)

# plots voltages at each cell segment for one cell (takes awhile)
def plot_cell_segs_v(dproj, dsim, dfig, indices, celltype, cellidx):
    filedict, pdict, spikedict = proc.get_var_paths(dproj, dsim)

    print filedict
    for expmt in filedict.iterkeys():
        for i,f in enumerate(filedict[expmt]):
            if i in indices:
                print f
                print os.listdir(dfig)
                filename = expmt + '_segments_v' + str(i) + 'cell_' + str(cellidx)  + '.pdf'
                filefig = os.path.join(dfig, filename)
                # gets xlim and incoming spike times
                t = proc.time_lock_to_stimulus(pdict[expmt][i])
                plot_indiv_cell_seg_v(f, filefig, t, celltype, cellidx)

# not used
def plot_mean_over_expmt(dproj, dsim, dfig, expmt, celltype):
    means = proc.mean_currents_over_expmt(dproj, dsim, expmt)
    filename = expmt + celltype + '_meansegments_rescaled.pdf'
    filefig = os.path.join(dfig, filename)
    if celltype == 'L5':
        segment_list = ['apical_tuft', 'apical_1', 'apical_2',
                'apical_trunk', 'apical_oblique',
                'soma', 'basal_1', 'basal_2', 'basal_3']
    elif celltype == 'L2':
        
        segment_list = ['apical_tuft', 'apical_1',
                'apical_trunk', 'apical_oblique',
                'soma', 'basal_1', 'basal_2', 'basal_3']
    
    fig = ac.FigSectionTimeSeries(segment_list)
    for segment in segment_list:
        for I in means[segment].keys():
            print type(I)
            current = means[segment][I]
            print current.shape
            t = linspace(0,250,current.shape[0])
            print type(current)
            print current.shape
            c = fig.colormap(I)
            fig.ax[segment].plot(t, current, color = c, linewidth=2)
            fig.set_vert_lines([25., 70., 135.], [25., 70., 135.])
            fig.set_legend()
            
            fig.set_ticks()
            fig.set_section_labels() 
    plt.show(block=False)
    plt.pause(30)
    fig.savefig(filefig)
    plt.close("all")

# plot one cell's segmentwise voltage
def plot_indiv_cell_seg_v(f, filefig, times, celltype='L5', cell_idx = 0):
    #TODO: include image of cell
    
    t0 = times[0]
    T = times[4]
    #for superthrehold non-locked
    #t0 = 0.
    #T = 250.
    tff1 = times[1]
    tfb = times[2]
    tff2 = times[3]
    if celltype == 'L5':
        segment_list = ['apical_tuft', 'apical_1', 'apical_2',
                'apical_trunk', 'apical_oblique',
                'soma', 'basal_1', 'basal_2', 'basal_3']
    elif celltype == 'L2':
        
        segment_list = ['apical_tuft', 'apical_1',
                'apical_trunk', 'apical_oblique',
                'soma', 'basal_1', 'basal_2', 'basal_3']
    t, var = proc.get_voltages(f)
    I = 0
    fig = ac.FigSectionTimeSeries(segment_list)
    
    
    #TODO: more than one cell, different timecourses
    t = array(t)
    interval_idx = t >= array(t0) 
    interval_idx2 = t <= array(T)
    # multiplication is intersection
    interval_idx = interval_idx*interval_idx2
    print interval_idx
    for segment in segment_list:
        voltage = array(var[cell_idx][segment])
        print len(voltage)
        #print voltage.shape
        #print t.shape
        c = fig.colormap(I)
        fig.ax[segment].plot(t[interval_idx], voltage[interval_idx], color = c, linewidth=0.75)
        fig.ax[segment].set_ylim([-80, 60])
        fig.set_vert_lines([tff1,tfb, tff2], [25., 70., 135.])
        fig.set_legend()
            
        fig.set_ticks()
        fig.set_section_labels() 
    plt.show(block=False)
    plt.pause(30)
    fig.savefig(filefig)
    plt.close("all")

# spike histograms
def plot_spike_rates(dproj, dsim, dfig):
    t_interval, spikes = proc.get_time_locked_spikes(dproj, dsim)
    for expmt in spikes.keys():
        for f_idx, spikefile in enumerate(spikes[expmt].keys()):
            spikedict = spikes[expmt][spikefile]
            
            filename = expmt + str(f_idx) + '_spikerates.pdf'
            filefig = os.path.join(dfig, filename)
            celltypes = [
                    'L2_pyramidal',
                    'L5_pyramidal',
                    'L2_basket',
                    'L5_basket'
                    ]
            colordict = ['k','k','r','r']
            fig = ac.FigSpikeHist()
            for c_idx, celltype in enumerate(celltypes):

                spike_lists = spikefn.filter_spike_dict(
                    spikedict, celltype)[celltype].collapse_all()
                agg_spikes = array(list(it.chain(spike_lists)))-t_interval[expmt][f_idx][0]
                bins = spikefn.hist_bin_opt(agg_spikes,1)
                print bins
                print agg_spikes
                if celltype[0:2] == 'L2':
                    fig.ax['L2'].hist( 
                            agg_spikes,
                            bins,
                            normed = True,
                            label = celltype, 
                            facecolor = colordict[c_idx],
                            edgecolor = colordict[c_idx],
                            alpha = 0.5
                            )
                    #fig.ax['L2'].set_xlim(t_interval[expmt][f_idx])

                    fig.ax['L2'].set_xlim([0,250])
                elif celltype[0:2] == 'L5':     
                    fig.ax['L5'].hist(
                            agg_spikes,
                            bins,
                            normed = True,
                            label=celltype,
                            facecolor = colordict[c_idx],
                            edgecolor = colordict[c_idx],
                            alpha = 0.5)
                    fig.ax['L5'].set_xlim([0,250])
            plt.show(block = False)
            plt.pause(10)
            fig.f.savefig(filefig)
            plt.close("all")

# plot classified waveforms taking mean over classes
def plot_means_over_phase_subsets(dfig, dproj, d_evoked_sim, whichexpmt, phases, transform = None):
    fig = ac.FigClassDipoleWithSpikes(len(phases), phases)
    
    #labels = ['Negative deflection', 'Early spiking', 'No effect']
    celltypes = ['L5_pyramidal', 'L5_basket', 'L2_pyramidal', 'L2_basket']    
    #colordict = {labels[0]:'r', labels[1]:'b', labels[2]:'g'}
    #plot time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim)
    #t_evoked, evoked_dpls_w, evoked_avg_dpl_w = proc.compare_time_locked_average(dproj, d_evoked_sim, WINDOW = True) 
    colordict = get_colordict(evoked_avg_dpl) 
    t_interval, spikes = proc.get_time_locked_spikes(dproj, d_evoked_sim)
    # hard code to just get the whole simulation intrval
    
    #t_interval['uper_bet'][0] = linspace(0.,700.,28401)
    scale = 10.0
    colors = plt.cm.brg(linspace(0,1,len(evoked_avg_dpl.keys())))
#    for idx, expmt in enumerate(sorted(evoked_avg_dpl.keys())):
#        colordict[expmt] = colors[idx]
    mean_dpl = [[]]*(len(phases))
    dpl = [[]]*(len(phases))
    mean_dpl_sav = []
    #print mean_dpl
    #mean_dpl = [[],[],[],[]]
    #mean_dpl_win = [[],[],[],[]]
    nonsensitive = []
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        if expmt == whichexpmt:
            print 'OK'
            for phase_class in range(len(phases)):
                n_phase = len(phases[phase_class]) 
                spike_list = []
                t0 = []
                dpl = []
                for phase in phases[phase_class]:
                    if transform == None:
                        transformed_signal = evoked_dpls[expmt][phase]
                    else:
                        transformed_signal = transform(evoked_dpls[expmt][phase])
                    dpl.append(transformed_signal)
                    print expmt, phase, phase_class
                    #print spikes.keys()
                    spike_list.append(spikes[expmt][phase])
                    t0.append(t_interval[expmt][phase])
                    #t0.append(linspace(0., 450., 400/0.025+1)) 
                    spike_colordict = {'L5_pyramidal':'b',
                            'L5_basket':'r',
                            'L2_pyramidal':'c',
                            'L2_basket':'m'}
                agg_spikes, bins = proc.combine_spikes(spike_list, t0, expmt)       
                print array(dpl).shape      
                mean_dpl = mean(array(dpl), axis = 0)
                mean_dpl_sav.append(proc.window_dipole(mean_dpl))
                #mean_dpl = proc.window_dipole(mean_dpl)
                #fig.ax[phase_class]['dipole'].plot(t_evoked, mean_dpl_win[phase_class], color='k', linewidth = 3)
                fig.ax[phase_class]['dipole'].plot(t_evoked, mean_dpl, color='k', linewidth = 2)
                fig.ax[phase_class]['dipole'].plot(t_evoked, proc.window_dipole(mean_dpl)*scale, color = 'k', linewidth = 1)
                fig.ax[phase_class]['dipole'].set_ylim([-2000,2000]) 
                for celltype in celltypes:
                    # need to divide by number of trials in each class
                    #hist, bin_edges = histogram(agg_spikes[celltype], bins[celltype])
                    #hist = list(hist)
                    #print hist
                    #print g
                    #hist = [h/n_phase for h in hist]
                    # now plot
                    #even bin option
                    bins[celltype] = linspace(0,166, 83)
                    if agg_spikes[celltype]:
                        h, b = histogram(agg_spikes[celltype], bins[celltype])
                        h = np.concatenate((h, [0]))
                        print h.shape, b[0:-1].shape
                        fig.ax[phase_class]['spikes'].step(
                            b,
                            # 2ms bins, correct for spikes/ms
                            h/(2.0*n_phase), 
                            label=celltype,
                            color = spike_colordict[celltype],
                            linewidth = 1)
                        #fig.ax[phase_class]['spikes'].set_xlim([0,180])
    #fig.normalize_spike_axes()
                fig.ax[phase_class]['dipole'].set_xlim([0., 140.]) 
    fig.ax[0]['dipole'].set_ylim([-2000., 2000.])
    fig.equalize_scales()
    sio.savemat(dfig+'expmt_' + str(whichexpmt) + '_mean_over_phases.mat', {'templates': mean_dpl_sav,
        'phase_idx': phases})
    sio.savemat(dfig+'expmt_' + str(whichexpmt) + '_all_phases.mat', {'dpl': dpl}) 
            #fig.ax[0]['spikes'].legend(loc = 1)
                #    plt.hist(
#         fig2 = plt.figure()

    #fig.ax['mean'].legend(loc=2)

    #plot event dipole
    #event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
    #for expmt in event_dpl:
    #    fig.ax['beta_event'].plot(event_t, event_dpl[expmt], color=colordict[expmt])
    plt.show(fig)
    fig.f.savefig(dfig+'dipoles_with_spikes'+str(whichexpmt)+'.pdf')
    fig.close()


# not used
def plot_events(dfig, dproj, d_evoked_sim):
        
    filedict, pdict, _ = proc.get_var_paths(dproj, d_evoked_sim)
    for whichexpmt in filedict.iterkeys():
        plot_means_over_phase_subsets(dfig, dproj, d_evoked_sim, whichexpmt, [[0]] )

# tv-regularized differentiation on model
def tdiff(data):
    #print data.shape
    d = TVRegDiff( data, 10, 1000., None, 'large', 1e-5, 2.5e-5, 0, 0)
    #print d.shape
    return d

# utilities
def get_most_recent_dir():

    all_dirs = all_subdirs_of('/repo/data/s1/')
    latest_dir = max(all_dirs, key = os.path.getmtime)
    print latest_dir
    all_subdirs = all_subdirs_of(latest_dir)
    latest_subdir = max(all_subdirs, key = os.path.getmtime)
    print latest_subdir
    return latest_subdir
def all_subdirs_of(b = '.'):
    result = []
    for d in os.listdir(b):
        bd = os.path.join(b,d)
        if os.path.isdir(bd): result.append(bd)
    return result
def get_all_dirs():
    pass

if __name__ == '__main__':
  
    dproj = "/repo/data/s1"
    d_event_sim = None 
    
# The following are used in the main text

    # Beta event only (supplement, with noise)
    #d_event_sim = dproj+'/2020-06-12/jones_law_event-000/'
    
    # L5 recording
    dsim = dproj+'/2020-08-21/jones_law_event-000/'
    
    # High latency waveforms in L5
    #dsim = dproj + '/2018-05-08/jones_law_phase-001/'
    
    # Exemplar phases in L5
    #dsim = dproj + '/2018-04-03/jones_law_L5-000'
    
    # 11 phases over 1000ms
    #dsim = dproj + '/2018-03-18/jones_law-001/'
    
    # 60 phases over 120ms
    #dsim = dproj + '/2018-05-15/jones_law_coherence-000'
    
    # 100 phases over 1000ms (beta only; no rest)
    #dsim = dproj + '/2018-03-21/jones_law_phase-000/'
    
    # cut L2/3 distal and GABAB inputs to L5
    #dsim = dproj + '/2018-06-18/jones_law_event-004/'

    # segment voltages (L2)
    #dsim = dproj + '/2020-03-17/jones_law_event-000/'

# supplement (evoked responses, beta with noise)
    #dsim = dproj + '/2020-05-15/jones_law_event-000/'
#    d_evoked_sim = dsim
#    WINDOW = True 
    dfig = dsim
    
    # for plotting the beta event itself
    #t_interval = [165., 1065.]
    #plot_events(dfig, dproj, dsim) 
    #plot_multiphase_spikes(dfig, dproj, d_evoked_sim, layer = 'L2')

    #plot_multiphase(dfig, dproj, d_evoked_sim, d_event_sim, t_interval)
    #plot_multiphase_spikes(dfig, dproj, d_evoked_sim, layer = 'L5')
    #plot_multiphase(dfig, dproj, d_evoked_sim, d_event_sim, t_interval)
    #plot_multiphase_spikes(dfig, dproj, d_evoked_sim, layer = 'L5')
    #plot_mean_PSD(dfig, dproj, dsim, WINDOW)
    #plot_var_ERP(dfig, dproj, dsim, WINDOW)
    #plot_mean_ERP(dfig, dproj, dsim, WINDOW)
    #plot_ERP_derivative(dfig, dproj, dsim, WINDOW)
    #plot_M50_M70(dproj, dsim)
    #plot_spike_rates(dproj, dsim, dfig)
    #cell 44 gives small early spiking
    #plot_cell_segs_v(dproj, dsim, dfig, [0], 'L2' , 44)
    #plot_mean_over_expmt(dproj, dsim, dfig, 'beta_low', 'L5')  
    #plot_all_currents(dproj, dsim, dfig, [0,500], 'L5', 42)
    
    #dsim = dproj + "/2020-05-08/jones_law_event-000/"
    #dfig = dsim
    #plot_multiphase(dfig, dproj, dsim, d_event_sim, t_interval, window= False)
#for i in [23]:
#    plot_cell_segs_v(dproj, dsim, dfig, [0], 'L2', i)
    for i in range(50):
        #plot_phase_currents(dproj, dsim, 'beta', [1], 'L5', i) 
        #plot_phase_currents(dproj, dsim, 'beta', [1], 'L5', i) 
        plot_cell_segs_v(dproj, dsim, dfig, [0], 'L5', i) 
    
    #phases = [range(60)]
    #splits into three classes
    #phases = [[2,3,4],range(5,48),range(49,99)]
    # For averaging and plotting averages
    #phases = [[0]]
    #plot_means_over_phase_subsets(dfig, dproj, dsim, 'beta', phases, transform = None)
