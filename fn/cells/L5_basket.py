# L5_basket.py - establish class def for layer 5 basket cells
#
# v 1.5.12
# rev 2013-01-05 (SL: Added parreceive_evprox)
# last rev: (MS: Synapse creation and biophysics moved from class_cell.py to here)

import itertools as it
from neuron import h as nrn
from class_cell import BasketSingle

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted

class L5Basket(BasketSingle):
    def __init__(self, pos):
        # Note: Cell properties are set in BasketSingle()
        BasketSingle.__init__(self, pos, 'L5Basket')
        self.celltype = 'L5_basket'

        self.__synapse_create()
        self.__biophysics()

    def __synapse_create(self):
        # ceates synapses onto this cell 
        self.soma_ampa = self.syn_ampa_create(self.soma(0.5))
        self.soma_gabaa = self.syn_gabaa_create(self.soma(0.5))

    def __biophysics(self):
        self.soma.insert('hh')

    # connections FROM other cells TO this cell
    # there are no connections from the L2Basket cells. congrats! 
    def parconnect(self, gid, gid_dict, pos_dict, p):
        # FROM other L5Basket cells TO this cell
        for gid_src, pos in it.izip(gid_dict['L5_basket'], pos_dict['L5_basket']):
            # if gid_src != gid:
            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L5Basket_L5Basket'],
                'A_delay': 1.,
                'lamtha': 20.
            }

            self.ncfrom_L5Basket.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_gabaa))

        # FROM other L5Pyr cells TO this cell
        for gid_src, pos in it.izip(gid_dict['L5_pyramidal'], pos_dict['L5_pyramidal']):
            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L5Pyr_L5Basket'],
                # 'A_weight': 5e-4,
                'A_delay': 1.,
                'lamtha': 3.
            }

            self.ncfrom_L5Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_ampa))

        # FROM other L2Pyr cells TO this cell
        for gid_src, pos in it.izip(gid_dict['L2_pyramidal'], pos_dict['L2_pyramidal']):
            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L2Pyr_L5Basket'],
                # 'A_weight': 2.5e-4,
                'A_delay': 1.,
                'lamtha': 3.
            }

            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_ampa))

    # parallel receive function parreceive()
    def parreceive(self, gid, gid_dict, pos_dict, p_ext):
        for gid_src, p_src, pos in it.izip(gid_dict['extinput'], p_ext, pos_dict['extinput']):
            if 'L5Basket' in p_src.keys():
                # if p_src['loc'] is 'proximal':
                nc_dict = {
                    'pos_src': pos,
                    'A_weight': p_src['L5Basket'][0],
                    'A_delay': p_src['L5Basket'][1],
                    'lamtha': p_src['lamtha']
                }

                self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_ampa))

    # evprox
    def parreceive_evprox(self, gid, gid_dict, pos_dict, p_evprox):
        if self.celltype in p_evprox.keys():
            gid_evprox = gid + gid_dict['evprox'][0]

            nc_dict = {
                'pos_src': pos_dict['evprox'][gid],
                'A_weight': p_evprox[self.celltype][0],
                'A_delay': p_evprox[self.celltype][1],
                'lamtha': p_evprox['lamtha_space']
            }

            self.ncfrom_evprox.append(self.parconnect_from_src(gid_evprox, nc_dict, self.soma_ampa))

    def parreceive_gauss(self, gid, gid_dict, pos_dict, p_ext_gauss):
        # gid is this cell's gid
        # gid_dict is the whole dictionary, including the gids of the extgauss
        # pos_dict is also the pos of the extgauss (net origin)
        # p_ext_gauss are the params (strength, etc.)
        if 'L5_basket' in p_ext_gauss.keys():
            gid_extgauss = gid + gid_dict['extgauss'][0]

            nc_dict = {
                'pos_src': pos_dict['extgauss'][gid],
                'A_weight': p_ext_gauss['L5_basket'][0],
                'A_delay': p_ext_gauss['L5_basket'][1],
                'lamtha': p_ext_gauss['lamtha']
            }

            self.ncfrom_extgauss.append(self.parconnect_from_src(gid_extgauss, nc_dict, self.soma_ampa))
