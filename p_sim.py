# defines the large param structure of combinations
# flat file of value ranges
# tuples for different "experiments"
# np.arrays for everything else?

from numpy import array, linspace

all = {
    'sim_prefix': 'spikeresponse',
    'N_pyr_x': 10,
    'N_pyr_y': 10,
    'Gauss_A_L2Pyr': 1.7e-5,
    'Gauss_A_L5Pyr': array([5.5e-5, 5.75e-5, 6e-5]),
    'Gauss_mu': 250.,
    'Gauss_sigma': 4.8,
    'gbar_L2Pyr_L2Pyr': 0.,
    'gbar_L5Pyr_L5Pyr': 0.,
    'tstop': 500.,
    'dt': 0.025
}
