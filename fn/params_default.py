# params_default.py - list of default params and values
#
# v 1.4.5
# rev 2012-11-27 (MS: Added param to toggle saving of rawspec data on and off)
# last major: (MS: Added param to set standard deviation of external alpha feed randomness)

# flat file of default values
# tuples for different "experiments"
# will most often be overwritten

params_default = {
    'sim_prefix': 'default',

    # numbers of cells making up the pyramidal grids
    'N_pyr_x': 10,
    'N_pyr_y': 10,

    # 'pois_lamtha': 10.,
    'pois_T': 1000.,

    # amplitudes of individual gaussian random inputs to L2Pyr and L5Pyr
    # L2 Basket params
    'L2Basket_Gauss_A': 5.9e-5,
    'L2Basket_Gauss_mu': 200.,
    'L2Basket_Gauss_sigma': 3.6,
    'L2Basket_Pois_A': 0.,
    'L2Basket_Pois_lamtha': 10.,

    # L2 Pyr params
    'L2Pyr_Gauss_A': 1.8e-5,
    'L2Pyr_Gauss_mu': 150.,
    'L2Pyr_Gauss_sigma': 3.6,
    'L2Pyr_Pois_A': 0.,
    'L2Pyr_Pois_lamtha': 10.,

    # L5 Pyr params
    'L5Pyr_Gauss_A': 5.83e-5,
    'L5Pyr_Gauss_mu': 500.,
    'L5Pyr_Gauss_sigma': 4.8,
    'L5Pyr_Pois_A': 0.,
    'L5Pyr_Pois_lamtha': 10.,

    # L5 Basket params
    'L5Basket_Gauss_A': 0.,
    # 'L5Basket_Gauss_A': 7.3e-5,
    'L5Basket_Gauss_mu': 500.,
    'L5Basket_Gauss_sigma': 2.,
    'L5Basket_Pois_A': 0.,
    'L5Basket_Pois_lamtha': 10.,

    # maxsimal conducatnces for all synapses
    # max conductances TO L2Pyrs
    'gbar_L2Pyr_L2Pyr': 5e-4,
    'gbar_L2Basket_L2Pyr': 5e-2,

    # max conductances TO L2Baskets
    'gbar_L2Pyr_L2Basket': 5e-4,
    'gbar_L2Basket_L2Basket': 2e-2,

    # max conductances TO L5Pyr
    'gbar_L5Pyr_L5Pyr': 5e-4,
    'gbar_L2Pyr_L5Pyr': 2.5e-4,
    'gbar_L2Basket_L5Pyr': 1e-3,
    'gbar_L5Basket_L5Pyr': 2.5e-2,

    # max conductances TO L5Baskets
    'gbar_L5Basket_L5Basket': 2e-2,
    'gbar_L5Pyr_L5Basket': 5e-4,
    'gbar_L2Pyr_L5Basket': 2.5e-4,

    # Ongoing alpha rhythms
    't0_input': 150.,
    'f_input_prox': 10.,
    'f_input_dist': 10.,
    'f_stand_dev': 20.,

    # times for evoked responses
    't_evoked_prox_early': 454.,
    't_evoked_prox_late': 564.,
    't_evoked_dist': 499.,

    # analysis
    'save_spec_data': 0,
    'spec_max_freq': 41.,

    # numerics
    # N_trials of 0 means that seed is set by rank, will still run 1 trial (obviously)
    'N_trials': 0,
    'tstop': 1000.,
    'dt': 0.025,
}
