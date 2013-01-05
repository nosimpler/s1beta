# L2_pyramidal.py - est class def for layer 2 pyramidal cells
#
# v 1.5.12
# rev 2013-01-05 (SL: added parreceive_evprox)
# last rev: (MS: Soma properties, dend properties set in dictionaries. Reorganized)

from neuron import h as nrn
from class_cell import Pyr
import sys
import numpy as np
import itertools as it

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted

class L2Pyr(Pyr):
    def __init__(self, pos):
        # Set somatic and dendritic properties
        soma_props = self.__set_soma_props(pos)
        dend_props, dend_names = self.__set_dend_props()

        # usage: Pyr.__init__(self, soma_props)
        Pyr.__init__(self, soma_props)
        self.celltype = 'L2_pyramidal'

        # geometry
        # creates self.list_dend
        # Dend Cm and dend Ra set with Soma Cm and Soma Ra
        self.create_dends(dend_names, dend_props, soma_props)
        self.__connect_sections()
        # self.__set_3Dshape()

        # biophysics
        self.__biophys_soma()
        self.__biophys_dends()

        # dipole_insert() comes from Cell()
        self.yscale = self.get_sectnames()
        self.dipole_insert(self.yscale)

        # create synapses
        self.__synapse_create()

    # Set somatic properties
    def __set_soma_props(self, pos):
        return {
            'pos': pos,
            'L': 22.1,
            'diam': 23.4,
            'cm': 0.6195,
            'Ra': 200.,
            'name': 'L2Pyr',
        }

    # Sets dendritic properties
    def __set_dend_props(self):
        # Hardcode dend properties
        dend_props = {
            'apical_trunk': {'L': 59.5, 'diam': 4.25},
            'apical_1': {'L': 306., 'diam': 4.08},
            'apical_tuft': {'L': 238., 'diam': 3.4},
            'apical_oblique': {'L': 340., 'diam': 3.91},
            'basal_1': {'L': 85., 'diam': 4.25},
            'basal_2': {'L': 255., 'diam': 2.72},
            'basal_3': {'L': 255., 'diam': 2.72},
        }

        # This order matters!
        dend_order = ['apical_trunk', 'apical_1', 'apical_tuft', 'apical_oblique',
                      'basal_1', 'basal_2', 'basal_3']

        return dend_props, dend_order

    # Connects sections of THIS cell together
    def __connect_sections(self):
        # child.connect(parent, parent_end, {child_start=0})
        # Distal (Apical)
        self.list_dend[0].connect(self.soma, 1, 0)
        self.list_dend[1].connect(self.list_dend[0], 1, 0)

        self.list_dend[2].connect(self.list_dend[1], 1, 0)

        # dend[4] comes off of dend[0](1)
        self.list_dend[3].connect(self.list_dend[0], 1, 0)

        # Proximal (Basal)
        self.list_dend[4].connect(self.soma, 0, 0)
        self.list_dend[5].connect(self.list_dend[4], 1, 0)
        self.list_dend[6].connect(self.list_dend[4], 1, 0)

    # Adds biophysics to soma
    def __biophys_soma(self):
        # set soma biophysics specified in Pyr
        # self.pyr_biophys_soma()

        # Insert 'hh' mechanism
        self.soma.insert('hh')
        self.soma.gkbar_hh = 0.01
        self.soma.gl_hh = 4.26e-5
        self.soma.el_hh = -65
        self.soma.gnabar_hh = 0.18
                
        # Insert 'km' mechanism
        # Units: pS/um^2
        self.soma.insert('km')
        self.soma.gbar_km = 250

    # Defining biophysics for dendrites
    def __biophys_dends(self):
        # set dend biophysics specified in Pyr()
        # self.pyr_biophys_dends()

        # set dend biophysics not specified in Pyr()
        for sec in self.list_dend:
            # neuron syntax is used to set values for mechanisms
            # sec.gbar_mech = x sets value of gbar for mech to x for all segs
            # in a section. This method is significantly faster than using
            # a for loop to iterate over all segments to set mech values

            # Insert 'hh' mechansim
            sec.insert('hh')
            sec.gkbar_hh = 0.01
            sec.gl_hh = 4.26e-5
            sec.gnabar_hh = 0.15
            sec.el_hh = -65

            # Insert 'km' mechanism
            # Units: pS/um^2
            sec.insert('km')
            sec.gbar_km = 250

    def __synapse_create(self):
        # creates synapses onto this cell 
        # Somatic synapses
        self.soma_gabaa = self.syn_gabaa_create(self.soma(0.5))
        self.soma_gabab = self.syn_gabab_create(self.soma(0.5))

        # Dendritic synapses
        # Here list_dend[3] is the oblique apical dendritic section, different from the L5Pyr!
        self.apicaloblique_ampa = self.syn_ampa_create(self.list_dend[3](0.5))
        self.apicaloblique_nmda = self.syn_nmda_create(self.list_dend[3](0.5))

        self.basal2_ampa = self.syn_ampa_create(self.list_dend[5](0.5))
        self.basal2_nmda = self.syn_nmda_create(self.list_dend[5](0.5))

        self.basal3_ampa = self.syn_ampa_create(self.list_dend[6](0.5))
        self.basal3_nmda = self.syn_nmda_create(self.list_dend[6](0.5))

        self.apicaltuft_ampa = self.syn_ampa_create(self.list_dend[2](0.5))
        self.apicaltuft_nmda = self.syn_nmda_create(self.list_dend[2](0.5))

    # collect receptor-type-based connections here
    def parconnect(self, gid, gid_dict, pos_dict, p):
        # Connections FROM all other L2 Pyramidal cells to this one
        for gid_src, pos in it.izip(gid_dict['L2_pyramidal'], pos_dict['L2_pyramidal']):
            # don't be redundant, this is only possible for LIKE cells, but it might not hurt to check
            # if gid_src != gid:
            # default value: 'A_weight': 5e-4,
            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L2Pyr_L2Pyr'],
                'A_delay': 1.,
                'lamtha': 3.
            }

            # parconnect_from_src(gid_presyn, nc_dict, postsyn)
            # ampa connections
            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaloblique_ampa))
            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.basal2_ampa))
            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.basal3_ampa))

            # nmda connections
            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaloblique_nmda))
            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.basal2_nmda))
            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.basal3_nmda))

        # connections FROM L2 basket cells TO this L2Pyr cell
        for gid_src, pos in it.izip(gid_dict['L2_basket'], pos_dict['L2_basket']):

            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L2Basket_L2Pyr'],
                'A_delay': 1.,
                'lamtha': 50.
            }

            self.ncfrom_L2Basket.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_gabaa))
            self.ncfrom_L2Basket.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_gabab))

        # connections FROM L5 basket cells TO this L2Pyr cell
        # for gid_src in gid_dict['L5_basket']:
        #     nc_dict = {
        #         'pos_src': pos_list[gid_src],
        #         'A_weight': 2.5e-2,
        #         'A_delay': 1.,
        #         'lamtha': 70.
        #     }

        #     self.ncfrom_L5Basket.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_gabaa))
        #     self.ncfrom_L5Basket.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_gabab))

    # may be reorganizable
    def parreceive(self, gid, gid_dict, pos_dict, p_ext):
        for gid_src, p_src, pos in it.izip(gid_dict['extinput'], p_ext, pos_dict['extinput']):
            # only connect extinput to synapses if the params exist in this param dict
            if 'L2Pyr' in p_src.keys():
                nc_dict = {
                    'pos_src': pos,
                    'A_weight': p_src['L2Pyr'][0],
                    'A_delay': p_src['L2Pyr'][1],
                    'lamtha': p_src['lamtha']
                }

                if p_src['loc'] is 'proximal':
                    self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.basal2_ampa))
                    self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.basal3_ampa))
                    self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaloblique_ampa))

                elif p_src['loc'] is 'distal':
                    self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaltuft_ampa))

                    # if this evoked, do nmda
                    if not p_src['f_input']:
                        self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaltuft_nmda))

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

            self.ncfrom_evprox.append(self.parconnect_from_src(gid_evprox, nc_dict, self.basal2_ampa))
            self.ncfrom_evprox.append(self.parconnect_from_src(gid_evprox, nc_dict, self.basal3_ampa))
            self.ncfrom_evprox.append(self.parconnect_from_src(gid_evprox, nc_dict, self.apicaloblique_ampa))

    def parreceive_gauss(self, gid, gid_dict, pos_dict, p_ext_gauss):
        # gid is this cell's gid
        # gid_dict is the whole dictionary, including the gids of the extgauss
        # pos_list is also the pos of the extgauss (net origin)
        # p_ext_gauss are the params (strength, etc.)

        # gid shift is based on L2_pyramidal cells NOT L5
        # I recognize this is ugly (hack)
        # gid_shift = gid_dict['extgauss'][0] - gid_dict['L2_pyramidal'][0]
        if 'L2_pyramidal' in p_ext_gauss.keys():
            gid_extgauss = gid + gid_dict['extgauss'][0]

            nc_dict = {
                'pos_src': pos_dict['extgauss'][gid],
                'A_weight': p_ext_gauss['L2_pyramidal'][0],
                'A_delay': p_ext_gauss['L2_pyramidal'][1],
                'lamtha': p_ext_gauss['lamtha']
            }

            self.ncfrom_extgauss.append(self.parconnect_from_src(gid_extgauss, nc_dict, self.basal2_ampa))
            self.ncfrom_extgauss.append(self.parconnect_from_src(gid_extgauss, nc_dict, self.basal3_ampa))
            self.ncfrom_extgauss.append(self.parconnect_from_src(gid_extgauss, nc_dict, self.apicaloblique_ampa))

        # Define 3D shape and position of cell. By default neuron uses xy plane for
    # height and xz plane for depth. This is opposite for model as a whole, but
    # convention is followed in this function for ease use of gui. 
    def __set_3Dshape(self):
        # set 3d shape of soma by calling shape_soma from class Cell
        # print "Warning: You are setiing 3d shape geom. You better be doing"
        # print "gui analysis and not numerical analysis!!"
        self.shape_soma()
        
        # soma proximal coords
        x_prox = 0
        y_prox = 0

        # soma distal coords
        x_distal = 0
        y_distal = self.soma.L

        # dend 0-2 are major axis, dend 3 is branch
        # deal with distal first along major cable axis
        # the way this is assigning variables is ugly/lazy right now
        for i in range(0, 3):
            nrn.pt3dclear(sec=self.list_dend[i])

            # x_distal and y_distal are the starting points for each segment
            # these are updated at the end of the loop
            nrn.pt3dadd(0, y_distal, 0, self.dend_diam[i], sec=self.list_dend[i])

            # update x_distal and y_distal after setting them
            # x_distal += dend_dx[i]
            y_distal += self.dend_L[i]

            # add next point
            nrn.pt3dadd(0, y_distal, 0, self.dend_diam[i], sec=self.list_dend[i])

        # now deal with dend 3
        # dend 3 will ALWAYS be positioned at the end of dend[0]
        nrn.pt3dclear(sec=self.list_dend[3])

        # activate this section with 'sec =' notation
        # self.list_dend[0].push()
        x_start = nrn.x3d(1, sec = self.list_dend[0])
        y_start = nrn.y3d(1, sec = self.list_dend[0])
        # nrn.pop_section()

        nrn.pt3dadd(x_start, y_start, 0, self.dend_diam[3], sec=self.list_dend[3])
        # self.dend_L[3] is subtracted because lengths always positive, 
        # and this goes to negative x
        nrn.pt3dadd(x_start-self.dend_L[3], y_start, 0, self.dend_diam[3], sec=self.list_dend[3])

        # now deal with proximal dends
        for i in range(4, 7):
            nrn.pt3dclear(sec=self.list_dend[i])

        # deal with dend 4, ugly. sorry.
        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[i], sec=self.list_dend[4])
        y_prox += -self.dend_L[4]

        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[4],sec=self.list_dend[4])

        # x_prox, y_prox are now the starting points for BOTH last 2 sections

        # dend 5
        # Calculate x-coordinate for end of dend
        dend5_x = -self.dend_L[5] * np.sqrt(2)/2
        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[5], sec=self.list_dend[5])
        nrn.pt3dadd(dend5_x, y_prox-self.dend_L[5] * np.sqrt(2)/2, 
                    0, self.dend_diam[5], sec=self.list_dend[5])

        # dend 6
        # Calculate x-coordinate for end of dend
        dend6_x = self.dend_L[6] * np.sqrt(2)/2
        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[6], sec=self.list_dend[6])
        nrn.pt3dadd(dend6_x, y_prox-self.dend_L[6] * np.sqrt(2)/2, 
                    0, self.dend_diam[6], sec=self.list_dend[6])

        # set 3D position
        # z grid position used as y coordinate in nrn.pt3dchange() to satisfy
        # gui convention that y is height and z is depth. In nrn.pt3dchange()
        # x and z components are scaled by 100 for visualization clarity
        self.soma.push()
        for i in range(0, int(nrn.n3d())):
            nrn.pt3dchange(i, self.pos[0]*100 + nrn.x3d(i), self.pos[2] + 
                           nrn.y3d(i), self.pos[1] * 100 + nrn.z3d(i), 
                           nrn.diam3d(i))

        nrn.pop_section()
