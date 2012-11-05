# defines the large param structure of combinations
# flat file of value ranges
# tuples for different "experiments"
# np.arrays for everything else?
# turns out, some whitespace is valid for dicts!

from numpy import array, linspace

all = {
    'sim_prefix': 'test',

    # numbers of cells making up the pyramidal grids
    'N_pyr_x': 1,
    'N_pyr_y': 1,

    # Poisson input
    # 'pois_lamtha': 20.,
    'pois_T': 250.,

    # amplitudes of individual gaussian random inputs to L2Pyr and L5Pyr
    # L2 Basket params
    'L2Basket_Gauss_A': 0.,
    # 'L2Basket_Gauss_A': 5.9e-5,
    'L2Basket_Gauss_mu': 2000.,
    'L2Basket_Gauss_sigma': 3.6,
    'L2Basket_Pois_A': 0.,
    # 'L2Basket_Pois_A': 1.25e-2,
    'L2Basket_Pois_lamtha': 0.,

    # L2 Pyr params
    'L2Pyr_Gauss_A': 0.,
    # 'L2Pyr_Gauss_A': 1.8e-5,
    'L2Pyr_Gauss_mu': 200.,
    'L2Pyr_Gauss_sigma': 3.6,
    'L2Pyr_Pois_A': 0.,
    # 'L2Pyr_Pois_A': 6.25e-3,
    'L2Pyr_Pois_lamtha': 0.,

    # L5 Pyr params
    'L5Pyr_Gauss_A': 0.,
    # 'L5Pyr_Gauss_A': linspace(5.83e-5, 5.25e-5, 5),
    'L5Pyr_Gauss_mu': 1000.,
    'L5Pyr_Gauss_sigma': 4.8,
    'L5Pyr_Pois_A': 0.,
    # 'L5Pyr_Pois_A': 6.25e-3,
    'L5Pyr_Pois_lamtha': 0.,

    # L5 Basket params
    'L5Basket_Gauss_A': 0.,
    # 'L5Basket_Gauss_A': 7.3e-5,
    'L5Basket_Gauss_mu': 1000.,
    'L5Basket_Gauss_sigma': 2.,
    'L5Basket_Pois_A': 0.,
    # 'L5Basket_Pois_A': 6.25e-3,
    'L5Basket_Pois_lamtha': 100.,

    # maximal conductacnes for all synapses
    # max conductances TO L2Pyrs
    'gbar_L2Pyr_L2Pyr': 0.,
    'gbar_L2Basket_L2Pyr': 0.,
    # 'gbar_L2Pyr_L2Pyr': 5e-4,
    # 'gbar_L2Basket_L2Pyr': 5e-2,

    # max conductances TO L2Baskets
    'gbar_L2Pyr_L2Basket': 0.,
    'gbar_L2Basket_L2Basket': 0.,
    # 'gbar_L2Pyr_L2Basket': 5e-4,
    # 'gbar_L2Basket_L2Basket': 2e-2,
    
    # max conductances TO L5Pyrs
    'gbar_L5Pyr_L5Pyr': 0.,
    'gbar_L2Pyr_L5Pyr': 0.,
    'gbar_L2Basket_L5Pyr': 0.,
    'gbar_L5Basket_L5Pyr': 0.,
    # 'gbar_L5Pyr_L5Pyr': 5e-4,
    # 'gbar_L2Pyr_L5Pyr': 2.5e-4,
    # 'gbar_L2Basket_L5Pyr': 5e-4,
    # 'gbar_L5Basket_L5Pyr': 2.5e-2,

    # max conductances TO L5Baskets
    'gbar_L5Basket_L5Basket': 0.,
    'gbar_L5Pyr_L5Basket': 0.,
    'gbar_L2Pyr_L5Basket': 0.,
    # 'gbar_L5Basket_L5Basket': 2e-2,
    # 'gbar_L5Pyr_L5Basket': 5e-4,
    # 'gbar_L2Pyr_L5Basket': 2.5e-4,

    # Ongoing alpha rhythms
    't0_input': 150.,
    'f_input_prox': [10.],
    'f_input_dist': [10.],
    # 'f_input_prox': linspace(5, 30, num=6),
    # 'f_input_dist': linspace(5, 30, num=6),

    # times for evoked responses
    't_evoked_prox_early': 1200.,
    't_evoked_prox_late': 1200.,
    't_evoked_dist': 1200.,

    # analysis
    'spec_max_freq': 41.,

    # numerics
    'tstop': 1000.,
    'dt': 0.025,
}
