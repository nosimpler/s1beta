# L5_basket.py - establish class def for layer 5 basket cells
#
# v 1.2.8
# rev 2012-10-02 (SL: added parreceive_gauss)
# last rev: (SL: parameterization of parconnect)

import itertools as it
from neuron import h as nrn
from class_cell import Basket

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted

class L5Basket(Basket):
    def __init__(self, pos):
        # Pyr.__init__(self, pos, L, diam, Ra, cm)
        Basket.__init__(self, pos, 'L5Basket')

    # connections FROM other cells TO this cell
    # there are no connections from the L2Basket cells. congrats! 
    def parconnect(self, gid, gid_dict, pos_list, p):
        # FROM other L5Basket cells TO this cell
        for gid_src in gid_dict['L5_basket']:
            # if gid_src != gid:
            nc_dict = {
                'pos_src': pos_list[gid_src],
                'A_weight': 2e-2,
                'A_delay': 1.,
                'lamtha': 20.
            }

            self.ncfrom_L5Basket.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_gabaa))

        # FROM other L5Pyr cells TO this cell
        for gid_src in gid_dict['L5_pyramidal']:
            nc_dict = {
                'pos_src': pos_list[gid_src],
                'A_weight': 5e-4,
                'A_delay': 1.,
                'lamtha': 3.
            }

            self.ncfrom_L5Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_ampa))

        # FROM other L2Pyr cells TO this cell
        for gid_src in gid_dict['L2_pyramidal']:
            nc_dict = {
                'pos_src': pos_list[gid_src],
                'A_weight': 2.5e-4,
                'A_delay': 1.,
                'lamtha': 3.
            }

            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_ampa))

    # parallel receive function parreceive()
    def parreceive(self, gid, gid_dict, pos_list, p_ext):
        for gid_src, p_src in it.izip(gid_dict['extinput'], p_ext):
            if 'L5Basket' in p_src.keys():
                # if p_src['loc'] is 'proximal':
                nc_dict = {
                    'pos_src': pos_list[gid_src],
                    'A_weight': p_src['L5Basket'][0],
                    'A_delay': p_src['L5Basket'][1],
                    'lamtha': p_src['lamtha']
                }

                self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_ampa))

    def parreceive_gauss(self, gid, gid_dict, pos_list, p_ext_gauss):
        # gid is this cell's gid
        # gid_dict is the whole dictionary, including the gids of the extgauss
        # pos_list is also the pos of the extgauss (net origin)
        # p_ext_gauss are the params (strength, etc.)
        if 'L2Pyr' in p_ext_gauss.keys():
            gid_extgauss = gid + gid_dict['extgauss'][0]
            nc_dict = {
                'pos_src': pos_list[gid_extgauss],
                'A_weight': p_ext_gauss['L5Basket'][0],
                'A_delay': p_ext_gauss['L5Basket'][1],
                'lamtha': p_ext_gauss['lamtha']
            }

            self.ncfrom_extgauss.append(self.parconnect_from_src(gid_extgauss, nc_dict, self.soma_ampa))
