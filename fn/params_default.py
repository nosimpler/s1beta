# params_default.py - list of default params and values
#
# v 1.2.18
# rev 2012-10-26 (SL: created)
# last major:

# flat file of default values
# tuples for different "experiments"
# will most often be overwritten
params_default = {
    'sim_prefix': 'default',

    # numbers of cells making up the pyramidal grids
    'N_pyr_x': 1,
    'N_pyr_y': 1,

    # amplitudes of individual gaussian random inputs to L2Pyr and L5Pyr
    # L2 Basket params
    'L2Basket_Gauss_A': 5.9e-5,
    'L2Basket_Gauss_mu': 200.,
    'L2Basket_Gauss_sigma': 3.6,

    # L2 Pyr params
    'L2Pyr_Gauss_A': 1.8e-5,
    'L2Pyr_Gauss_mu': 150.,
    'L2Pyr_Gauss_sigma': 3.6,

    # L5 Pyr params
    'L5Pyr_Gauss_A': 5.83e-5,
    'L5Pyr_Gauss_mu': 500.,
    'L5Pyr_Gauss_sigma': 4.8,

    # L5 Basket params
    'L5Basket_Gauss_A': 0.,
    # 'L5Basket_Gauss_A': 7.3e-5,
    'L5Basket_Gauss_mu': 500.,
    'L5Basket_Gauss_sigma': 2.,

    # maximal conductances for these connections
    'gbar_L2Pyr_L2Pyr': 0.,
    'gbar_L5Pyr_L5Pyr': 0.,

    # Ongoing alpha rhythms
    'f_input_prox': 10.,

    # numerics
    'tstop': 100.,
    'dt': 0.025,
}
