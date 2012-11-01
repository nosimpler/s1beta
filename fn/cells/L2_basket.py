# L2_basket.py - establish class def for layer 2 basket cells
#
# v 1.2.25
# rev 2012-11-01 (SL: Added self.celltype)
# last rev: (SL: added synaptic conductances)

import itertools as it
from neuron import h as nrn
from class_cell import Basket

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted

class L2Basket(Basket):
    def __init__(self, pos):
        # Pyr.__init__(self, pos, L, diam, Ra, cm)
        Basket.__init__(self, pos, 'L2Basket')
        self.celltype = 'L2_basket'

        # self.soma_ampa and self.soma_gabaa are inherited from Basket()
        # create nmda synapse unique to L2Basket
        self.soma_nmda = self.syn_nmda_create(self.soma(0.5))

    # par connect between all presynaptic cells
    # no connections from L5Pyr or L5Basket to L2Baskets
    def parconnect(self, gid, gid_dict, pos_dict, p):
        # FROM L2 pyramidals TO this cell
        for gid_src, pos in it.izip(gid_dict['L2_pyramidal'], pos_dict['L2_pyramidal']):
            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L2Pyr_L2Basket'],
                'A_delay': 1.,
                'lamtha': 3.
            }

            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_ampa))

        # FROM other L2Basket cells
        for gid_src, pos in it.izip(gid_dict['L2_basket'], pos_dict['L2_basket']):
        # for gid_src in gid_dict['L2_basket']:
            # if gid_src != gid:
            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L2Basket_L2Basket'],
                # 'A_weight': 2e-2,
                'A_delay': 1.,
                'lamtha': 20.
            }

            self.ncfrom_L2Basket.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_gabaa))

    # this function might make more sense as a method of net?
    # par: receive from external inputs
    def parreceive(self, gid, gid_dict, pos_dict, p_ext):
        # for some gid relating to the input feed:
        for gid_src, p_src, pos in it.izip(gid_dict['extinput'], p_ext, pos_dict['extinput']):
            # check if params are defined in the p_src
            if 'L2Basket' in p_src.keys():
                # create an nc_dict
                nc_dict = {
                    'pos_src': pos,
                    'A_weight': p_src['L2Basket'][0],
                    'A_delay': p_src['L2Basket'][1],
                    'lamtha': p_src['lamtha']
                }

                # connections depend on location of input
                if p_src['loc'] is 'proximal':
                    self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_ampa))

                elif p_src['loc'] is 'distal':
                    self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_ampa))

                    # if f_input is 0, treat as an evoked input
                    if not p_src['f_input']:
                        self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_nmda))

    def parreceive_gauss(self, gid, gid_dict, pos_dict, p_ext_gauss):
        # gid is this cell's gid
        # gid_dict is the whole dictionary, including the gids of the extgauss
        # pos_list is also the pos of the extgauss (net origin)
        # p_ext_gauss are the params (strength, etc.)
        # I recognize this is ugly (hack)
        if 'L2_basket' in p_ext_gauss.keys():
            # since gid ids are unique, then these will all be shifted.
            # if order of extgauss random feeds ever matters (likely), then will have to preserve order
            # of creation based on gid ids of the cells
            # this is a dumb place to put this information
            gid_extgauss = gid + gid_dict['extgauss'][0]

            # gid works here because there are as many pos items in pos_dict['extgauss'] as there are cells
            nc_dict = {
                'pos_src': pos_dict['extgauss'][gid],
                'A_weight': p_ext_gauss['L2_basket'][0],
                'A_delay': p_ext_gauss['L2_basket'][1],
                'lamtha': p_ext_gauss['lamtha']
            }

            self.ncfrom_extgauss.append(self.parconnect_from_src(gid_extgauss, nc_dict, self.soma_ampa))
