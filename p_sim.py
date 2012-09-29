# defines the large param structure of combinations
# flat file of value ranges
# tuples for different "experiments"
# np.arrays for everything else?

from numpy import array, linspace

all = {
    'sim_prefix': 'some_prefix',
    'N_pyr_x': array([1, 2, 3]),
    'N_pyr_y': array([2, 3]),
    'tstop': 100.,
    'dt': 0.025
}
