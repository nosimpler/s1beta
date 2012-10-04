# defines the large param structure of combinations
# flat file of value ranges
# tuples for different "experiments"
# np.arrays for everything else?
# turns out, some whitespace is valid for dicts!

from numpy import array, linspace

all = {
    'sim_prefix': 'feedtest',

    # numbers of cells making up the pyramidal grids
    'N_pyr_x': 5,
    'N_pyr_y': 5,

    # amplitudes of individual gaussian random inputs to L2Pyr and L5Pyr
    # L2 Basket params
    'L2Basket_Gauss_A': 2.5e-4,
    'L2Basket_Gauss_mu': 220.,
    'L2Basket_Gauss_sigma': 5.,

    # L2 Pyr params
    'L2Pyr_Gauss_A': 1.7e-5,
    'L2Pyr_Gauss_mu': 200.,
    'L2Pyr_Gauss_sigma': 1.,

    # L5 Pyr params
    'L5Pyr_Gauss_A': 5.5e-5,
    'L5Pyr_Gauss_mu': 210.,
    'L5Pyr_Gauss_sigma': 2.,

    # L5 Basket params
    'L5Basket_Gauss_A': 2.5e-4,
    'L5Basket_Gauss_mu': 250.,
    'L5Basket_Gauss_sigma': 10.,

    # maximal conductances for these connections
    'gbar_L2Pyr_L2Pyr': 0.,
    'gbar_L5Pyr_L5Pyr': 0.,

    # numerics
    'tstop': 350.,
    'dt': 0.025
}
