# defines the large param structure of combinations
# flat file of value ranges
# tuples for different "experiments"
# np.arrays for everything else?
# turns out, some whitespace is valid for dicts!

from numpy import array, linspace

all = {
    'sim_prefix': 'spikeresponse',

    # numbers of cells making up the pyramidal grids
    'N_pyr_x': 1,
    'N_pyr_y': 1,

    # amplitudes of individual gaussian random inputs to L2Pyr and L5Pyr
    # 'Gauss_A_L2Pyr': 1.7e-5,
    # 'Gauss_A_L5Pyr': 5.5e-5,
    'Gauss_A_L2Pyr': 0.,
    'Gauss_A_L5Pyr': 0.,
    # 'Gauss_A_L2Basket': linspace(0., 1e-3, 5),
    'Gauss_A_L2Basket': 0.,
    'Gauss_A_L5Basket': linspace(0., 1e-3, 5),

    # Gaussian parameters
    'Gauss_mu': 250.,
    'Gauss_sigma': 1.,
    # 'Gauss_sigma': 4.8,

    # maximal conductances for these connections
    'gbar_L2Pyr_L2Pyr': 0.,
    'gbar_L5Pyr_L5Pyr': 0.,

    # numerics
    'tstop': 500.,
    'dt': 0.025
}
