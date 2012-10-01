# defines the large param structure of combinations
# flat file of value ranges
# tuples for different "experiments"
# np.arrays for everything else?

from numpy import array, linspace

all = {
    'sim_prefix': 'spikeresponse',
    'N_pyr_x': 1.,
    'N_pyr_y': 1.,
    'Gauss_A_L2Pyr': 0.,
    # 'Gauss_A_L2Pyr': 7e-4,
    'Gauss_A_L5Pyr': 0.,
    # 'Gauss_A_L5Pyr': 3e-3,
    'Gauss_mu': 250.,
    'Gauss_sigma': 1.,
    'tstop': 500.,
    'dt': 0.025
}
