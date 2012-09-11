# params_extinput.py - establishes feed params
# usage: import params_extinput as p or similar
#
# v 1.0.0
# rev 2012-09-11 (SL: created)
# last rev: 

# Create feed parameters
# p['cellobj'] is a tuple of (weight, delay)
__feed_prox = {
    'f_input': 10.,
    't0': 150.,
    'L2Pyr': (4e-5, 0.1),
    'L5Pyr': (4e-5, 1.),
    'L2Basket': (8e-5, 0.1),
    'L5Basket': (8e-5, 1.),
    'lamtha': 100.,
    'loc': 'proximal'
}

__feed_dist = {
    'f_input': 10.,
    't0': 150.,
    'L2Pyr': (4e-5, 5.),
    'L5Pyr': (4e-5, 5.),
    'L2Basket': (4e-5, 5.),
    'lamtha': 100.,
    'loc': 'distal'
}

# Create evoked response parameters
__evoked_prox_early = {
    'f_input': 0.,
    't0': 454.,
    'L2Pyr': (1e-3, 0.1),
    'L5Pyr': (5e-4, 1.),
    'L2Basket': (2e-3, 0.1),
    'L5Basket': (1e-3, 1.),
    'lamtha': 3.,
    'loc': 'proximal'
}

__evoked_prox_late = {
    'f_input': 0.,
    't0': 564.,
    'L2Pyr': (6.89e-3, 0.1),
    'L5Pyr': (3.471e-3, 5.),
    'L2Basket': (6.89e-3, 0.1),
    'L5Basket': (3.471e-3, 5.),
    'lamtha': 3.,
    'loc': 'proximal'
}

__evoked_dist = {
    'f_input': 0.,
    't0': 499.,
    'L2Pyr': (1.05e-3, 0.1),
    'L5Pyr': (1.05e-3, 0.1),
    'L2Basket': (5.02e-4, 0.1),
    'lamtha': 3.,
    'loc': 'distal'
}

# indexable py list of param dicts for parallel
p_ext = [
    __feed_prox,
    __feed_dist,
    # __evoked_prox_early,
    # __evoked_prox_late,
    # __evoked_dist
]
