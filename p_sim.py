# defines the large param structure of combinations
# flat file of value ranges
# tuples for different "experiments"
# np.arrays for everything else?
# turns out, some whitespace is valid for dicts!

from numpy import array, linspace

all = {
    'sim_prefix': 'L2inhib-mu',

    # numbers of cells making up the pyramidal grids
    'N_pyr_x': 10,
    'N_pyr_y': 10,

    # amplitudes of individual gaussian random inputs to L2Pyr and L5Pyr
    # L2 Basket params
    # 'L2Basket_Gauss_A': 0.,
    'L2Basket_Gauss_A': 5.9e-5,
    'L2Basket_Gauss_mu': 200.,
    'L2Basket_Gauss_sigma': 3.6,

    # L2 Pyr params
    # 'L2Pyr_Gauss_A': 0.,
    'L2Pyr_Gauss_A': 1.8e-5,
    'L2Pyr_Gauss_mu': 200.,
    'L2Pyr_Gauss_sigma': 3.6,

    # L5 Pyr params
    'L5Pyr_Gauss_A': 0.,
    # 'L5Pyr_Gauss_A': linspace(5.83e-5, 5.25e-5, 5),
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

    # numerics
    'tstop': 350.,
    'dt': 0.025
}
