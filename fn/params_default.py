# params_default.py - master list of changeable params. most set to default val of inactive
#
# v 1.8.5
# rev 2013-06-12 (MS: renamed spec_max_freq as f_max_spec)
# last major: (SL: fixed minimum delay bug)

# Note that nearly all start times are set BEYOND tstop for this file
# Most values here are set to whatever default value inactivates them, such as 0 for conductance
# prng seed values are also set to 0 (non-random)
# flat file of default values
# will most often be overwritten
def get_params_default():
    return {
        'sim_prefix': 'default',

        # simulation end time (ms)
        'tstop': 250.,

        # numbers of cells making up the pyramidal grids
        'N_pyr_x': 1,
        'N_pyr_y': 1,

        # amplitudes of individual Gaussian random inputs to L2Pyr and L5Pyr
        # L2 Basket params
        'L2Basket_Gauss_A_weight': 0.,
        'L2Basket_Gauss_mu': 1000.,
        'L2Basket_Gauss_sigma': 3.6,
        'L2Basket_Pois_A_weight': 0.,
        'L2Basket_Pois_lamtha': 10.,

        # L2 Pyr params
        'L2Pyr_Gauss_A_weight': 0.,
        'L2Pyr_Gauss_mu': 1000.,
        'L2Pyr_Gauss_sigma': 3.6,
        'L2Pyr_Pois_A_weight': 0.,
        'L2Pyr_Pois_lamtha': 10.,

        # L5 Pyr params
        'L5Pyr_Gauss_A_weight': 0.,
        'L5Pyr_Gauss_mu': 1000.,
        'L5Pyr_Gauss_sigma': 4.8,
        'L5Pyr_Pois_A_weight': 0.,
        'L5Pyr_Pois_lamtha': 10.,

        # L5 Basket params
        'L5Basket_Gauss_A_weight': 0.,
        'L5Basket_Gauss_mu': 1000.,
        'L5Basket_Gauss_sigma': 2.,
        'L5Basket_Pois_A_weight': 0.,
        'L5Basket_Pois_lamtha': 10.,

        # maximal conductances for all synapses
        # max conductances TO L2Pyrs
        'gbar_L2Pyr_L2Pyr_ampa': 0.,
        'gbar_L2Pyr_L2Pyr_nmda': 0.,
        'gbar_L2Basket_L2Pyr_gabaa': 0.,
        'gbar_L2Basket_L2Pyr_gabab': 0.,

        # max conductances TO L2Baskets
        'gbar_L2Pyr_L2Basket': 0.,
        'gbar_L2Basket_L2Basket': 0.,

        # max conductances TO L5Pyr
        'gbar_L5Pyr_L5Pyr_ampa': 0.,
        'gbar_L5Pyr_L5Pyr_nmda': 0.,
        'gbar_L2Pyr_L5Pyr': 0.,
        'gbar_L2Basket_L5Pyr': 0.,
        'gbar_L5Basket_L5Pyr_gabaa': 0.,
        'gbar_L5Basket_L5Pyr_gabab': 0.,

        # max conductances TO L5Baskets
        'gbar_L5Basket_L5Basket': 0.,
        'gbar_L5Pyr_L5Basket': 0.,
        'gbar_L2Pyr_L5Basket': 0.,

        # Ongoing proximal alpha rhythm
        'distribution_prox': 'normal',
        't0_input_prox': 1000.,
        'tstop_input_prox': 250.,
        'f_input_prox': 10.,
        'f_stdev_prox': 20.,
        'events_per_cycle_prox': 2,

        # Ongoing distal alpha rhythm
        'distribution_dist': 'normal',
        't0_input_dist': 1000.,
        'tstop_input_dist': 250.,
        'f_input_dist': 10.,
        'f_stdev_dist': 20.,
        'events_per_cycle_dist': 2,

        # thalamic input amplitudes abd delays
        'input_prox_A_weight_L2Pyr': 0.,
        'input_prox_A_weight_L5Pyr': 0.,
        'input_prox_A_weight_inh': 0.,
        'input_prox_A_delay_L2': 0.1,
        'input_prox_A_delay_L5': 1.0,

        # current values, not sure where these distal values come from, need to check
        'input_dist_A_weight_L2Pyr': 0.,
        'input_dist_A_weight_L5Pyr': 0.,
        'input_dist_A_weight_inh': 0.,
        'input_dist_A_delay_L2': 5.,
        'input_dist_A_delay_L5': 5.,

        # evprox (early) feed strength
        'gbar_evprox_early_L2Pyr': 0.,
        'gbar_evprox_early_L5Pyr': 0.,
        'gbar_evprox_early_L2Basket': 0.,
        'gbar_evprox_early_L5Basket': 0.,

        # evprox (late) feed strength
        'gbar_evprox_late_L2Pyr': 0.,
        'gbar_evprox_late_L5Pyr': 0.,
        'gbar_evprox_late_L2Basket': 0.,
        'gbar_evprox_late_L5Basket': 0.,

        # evdist feed strengths
        'gbar_evdist_L2Pyr': 0.,
        'gbar_evdist_L5Pyr': 0.,
        'gbar_evdist_L2Basket': 0.,

        # times and stdevs for evoked responses
        't_evprox_early': 1000.,
        'sigma_t_evprox_early': 2.5,

        'dt_evprox0_evdist': -1,
        't_evdist': 1000.,
        'sigma_t_evdist': 6.,

        'dt_evprox0_evprox1': -1,
        't_evprox_late': 1000.,
        'sigma_t_evprox_late': 7.,

        # analysis
        'save_spec_data': 0,
        'f_max_spec': 40.,

        # IClamp params for L2Pyr
        'Itonic_A_L2Pyr_soma': 0.,
        'Itonic_t0_L2Pyr_soma': 50.,
        'Itonic_T_L2Pyr_soma': -1.,

        # IClamp params for L5Pyr
        'Itonic_A_L5Pyr_soma': 0.,
        'Itonic_t0_L5Pyr_soma': 50.,
        'Itonic_T_L5Pyr_soma': -1.,

        # numerics
        # N_trials of 0 means that seed is set by rank, will still run 1 trial (obviously)
        'N_trials': 0,

        # prng_state is a string for a filename containing the random state one wants to use
        # prng seed cores are the base integer seed for the specific
        # prng object for a specific random number stream
        # 'prng_state': None,
        'prng_seedcore_input_prox': 0,
        'prng_seedcore_input_dist': 0,
        'prng_seedcore_extpois': 0,
        'prng_seedcore_extgauss': 0,
        'prng_seedcore_evprox_early': 0,
        'prng_seedcore_evdist': 0,
        'prng_seedcore_evprox_late': 0,

        # default end time for pois inputs
        'pois_T': 250.,
        'dt': 0.025,
    }
