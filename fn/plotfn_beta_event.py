#function to call FigEvokedOnBeta and fill it with data
#need to get a simdir for one beta event and a simdir for evoked events
import fileio
import proc_beta_event as proc
import ac_beta_event as ac
import matplotlib.pyplot as plt
import spikefn
from numpy import array, linspace, dot
import os
import time
#compare high vs. low beta conditions
def plot_evoked_on_beta(dfig, dproj, d_evoked_sim, d_event_sim, t_interval):
    fig = ac.FigEvokedOnBeta()
    colordict = {'beta_low':'g', 'beta_high':'b'}
    #plot time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim)
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


def plot_mean_ERP(dfig, dproj, d_evoked_sim):
    fig = ac.FigEvokedOnBeta()
    colordict = {'beta_low':'g', 'beta_high':'b'}
    #plot time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim)
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        if expmt in ['beta_high', 'beta_low']:
            fig.ax['mean'].plot(t_evoked, evoked_avg_dpl[expmt], label=expmt, color=colordict[expmt])
            for f in evoked_dpls[expmt]:
                fig.ax['individual'].plot(t_evoked, evoked_dpls[expmt][f], color=colordict[expmt])
    fig.ax['mean'].legend()

    #plot event dipole
    #event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
    #for expmt in event_dpl:
    #    fig.ax['beta_event'].plot(event_t, event_dpl[expmt], color=colordict[expmt])
    plt.show(fig)
    fig.f.savefig(dfig+'evoked_on_beta.pdf')
    fig.close()
#compare phases and high/low
def plot_multiphase(dfig, dproj, d_evoked_sim, d_event_sim, t_interval):

    colordict = {'beta_low':'g', 'beta_high':'b'}
    #plot time-locked average dipoles and individual dipoles
    t_evoked, evoked_dpls, evoked_avg_dpl = proc.compare_time_locked_average(
            dproj, d_evoked_sim)
    n_trials = len(evoked_dpls['beta_low'].keys())
    print n_trials
    fig = ac.FigBetaPhase(n_trials)
    for exp_idx, expmt in enumerate(evoked_avg_dpl.keys()):
        #fig.ax['mean'].plot(t_evoked, evoked_avg_dpl[expmt], label=expmt, color=colordict[expmt])
        for i_f, f in enumerate(evoked_dpls[expmt]):
            fig.ax[i_f].plot(t_evoked, evoked_dpls[expmt][f],
                    linewidth=2, color=colordict[expmt])
            fig.ax[i_f].set_xticklabels('')
            fig.ax[i_f].set_yticklabels('')

    #plot event dipole
    event_t, event_dpl = proc.compare_event(dproj, d_event_sim, t_interval)
    for expmt in event_dpl:
        time = t_interval[-1] - t_interval[0]
        fig.ax['beta_event'].plot(event_dpl[expmt], event_t,
                color=colordict[expmt], linewidth = 3, label=expmt)
        fig.ax['beta_event'].set_ylim(t_interval[-1] +
                time/(2.*n_trials), t_interval[0] - time/(2.*n_trials))
    
    fig.ax['beta_event'].legend(loc='upper left')
    plt.show(fig)
    fig.savepng(dfig+'multiphase_beta.png')
    fig.close()

#plots n x 2 stimulus locked spike rasters
def plot_multiphase_spikes(dfig, dproj, d_evoked_sim, layer='L2'):
    t_interval_evoked, spikes = proc.get_time_locked_spikes(dproj, d_evoked_sim)
    expmt_map = {'beta_low': 0, 'beta_high': 1}
    fig = ac.FigBetaPhaseSpikes(10,2)
    s_dict = {}
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
def plot_multiphase_currents(dfig, dproj, d_evoked_sim, d_event_sim, t_interval, layer='L2_Pyr'):

    colordict = {'beta_low':'g', 'beta_high':'b'}
    #plot time-locked average dipoles and individual dipoles
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
        time = t_interval[-1] - t_interval[0]
        fig.ax['beta_event'].plot(event_dpl[expmt], event_t,
                color=colordict[expmt], linewidth = 3, label=expmt)
        fig.ax['beta_event'].set_ylim(t_interval[-1] +
                time/(2.*n_trials), t_interval[0] - time/(2.*n_trials))
    
    fig.ax['beta_event'].legend(loc='upper left')
    plt.show(fig)
    fig.savepng(dfig+'multiphase_beta.png')
    fig.close()

def plot_seg_currents(f, filefig, times, celltype):
    #TODO: include image of cell
    t0 = times[0]
    T = times[4]
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
    I_mean, I_conf, I_samples = proc.get_stats(var, 3)
    fig = ac.FigSectionTimeSeries(segment_list)
    #TODO: more than one cell, different timecourses
    t = array(t)
    interval_idx = t >= array(t0) 
    interval_idx2 = t <= array(T)
    # multiplication is intersection
    interval_idx = interval_idx*interval_idx2
    print interval_idx
    for segment in segment_list:
        for I in I_mean[segment].keys():
            print type(I)
            current = I_mean[segment][I]
            print type(current)
            print current.shape
            print t.shape
            c = fig.colormap(I)
            fig.ax[segment].plot(t[interval_idx], current[interval_idx], color = c, linewidth=2)
            fig.set_vert_lines([tff1,tfb, tff2], [25., 70., 135.])
            fig.set_legend()
            
            fig.set_ticks()
            fig.set_section_labels() 
    plt.show(block=False)
    plt.pause(30)
    fig.savefig(filefig)
    plt.close("all")
def plot_all_currents(dproj, dsim, dfig, t_interval, celltype):
    filedict = proc.get_var_paths(dproj, dsim)
    for expmt in filedict.iterkeys():
        print filedict[expmt]        
        for i,f in enumerate(filedict[expmt]):
            print f
            print os.listdir(dfig)
            filename = expmt + '_segments_' + str(i) + '.pdf'
            filefig = os.path.join(dfig, filename)
            plot_seg_currents(f, filefig, t_interval, 'L5')

# x limits according to when perturbation occurred 
def plot_phase_currents(dproj, dsim, expmt, indices, celltype):
    filedict, pdict = proc.get_var_paths(dproj, dsim)

    print filedict
    for i,f in enumerate(filedict[expmt]):
        if i in indices:
            print f
            print os.listdir(dfig)
            filename = expmt + '_segments_' + str(i) + '.pdf'
            filefig = os.path.join(dfig, filename)
            # gets xlim and incoming spike times
            t = proc.time_lock_to_stimulus(pdict[expmt][i])
            plot_seg_currents(f, filefig, t, celltype)

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
            t = linspace(0,180,current.shape[0])
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
if __name__ == '__main__':
    dproj = "/repo/data/s1"
    dfig = os.path.join(dproj, "figures_beta/")
    #d_event_sim = dproj + '/2016-03-20/beta-event-000/'
    #d_evoked_sim = dproj + '/2016-05-16/no_proximal-000/'
    dsim = dproj + '/2016-09-16/beta-000'

    #dsim = dproj + '/2016-09-05/beta-006'
    #dsim = dproj + '/2016-09-12/beta-008'
    #t_interval = [410., 510.]
    #plot_multiphase_spikes(dfig, dproj, d_evoked_sim, layer = 'L5')
    #plot_evoked_on_beta(dfig, dproj, d_evoked_sim, d_event_sim, t_interval)
    #plot_mean_ERP(dfig, dproj, dsim)
    plot_mean_over_expmt(dproj, dsim, dfig, 'beta_low', 'L5')  
    #plot_all_currents(dproj, dsim, dfig, t_interval, 'L5')
    #plot_phase_currents(dproj, dsim, 'no_beta', [0], 'L2') 
    #plot_evoked_on_beta(dfig, dproj, dsim, 
    #plot_currents(dproj, dsim, 
    #plot_multiphase(dfig, dproj, d_evoked_sim, d_event_sim, t_interval)
    #plot_multiphase_currents(dfig, dproj, d_evoked_sim, d_event_sim, t_interval, layer = 'L2_Pyr')
