# L5_pyramidal.py - establish class def for layer 5 pyramidal cells
#
# v 1.6.2ev
# rev 2013-01-07 (SL: added evdist)
# last rev: (SL: changed parreceives)

from neuron import h as nrn
from class_cell import Pyr
import sys 
import numpy as np
import itertools as it

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted
# units for taur: ms

class L5Pyr(Pyr):
    def __init__(self, pos):
        # Set morphology properties
        soma_props = self.__set_soma_props(pos)
        dend_props, dend_names = self.__set_dend_props()

        # Pyr.__init__(self, soma_props)
        Pyr.__init__(self, soma_props)
        # Pyr.__init__(self, pos, 39, 28.9, 0.85, 'L5Pyr')
        self.celltype = 'L5_pyramidal'

        # preallocate namespaces for dend properties
        # set in dend_props()
        # self.dend_names = []
        # self.dend_L = []
        # self.dend_diam = []
        # self.dend_cm = soma_props['cm']
        # self.cm = 0.85

        # Geometry
        # dend Cm and dend Ra set using soma Cm and soma Ra
        self.create_dends(dend_names, dend_props, soma_props)
        # self.create_dends(self.dend_props, self.cm)
        self.__connect_sections()
        # self.__set_3Dshape()

        # biophysics
        self.__biophys_soma()
        self.__biophys_dends()

        # Dictionary of length scales to calculate dipole without 3d shape. Comes from Pyr().
        self.yscale = self.get_sectnames()
        # dipole_insert() comes from Cell()
        self.dipole_insert(self.yscale)

        # create synapses
        self.__synapse_create()

    # Sets somatic properties. Returns dictionary.
    def __set_soma_props(self, pos):
         return {
            'pos': pos,
            'L': 39.,
            'diam': 28.9,
            'cm': 0.85,
            'Ra': 200.,
            'name': 'L5Pyr',
        }

    # Returns dictionary of dendritic properties and list of dendrite names
    def __set_dend_props(self):
        # Hard coded dend properties
        dend_props =  {
            'apical_trunk': {
                'L': 102.,
                'diam': 10.2,
            },
            'apical_1': {
                'L': 680.,
                'diam': 7.48,
            },
            'apical_2': {
                'L': 680.,
                'diam': 4.93,
            },
            'apical_tuft': {
                'L': 425.,
                'diam': 3.4,
            },
            'apical_oblique': {
                'L': 255.,
                'diam': 5.1,
            },
            'basal_1': {
                'L': 85.,
                'diam': 6.8,
            },
            'basal_2': {
                'L': 255.,
                'diam': 8.5,
            },
            'basal_3': {
                'L': 255.,
                'diam': 8.5,
            },
        }

        # These MUST match order the above keys in exact order!
        dend_names = [
            'apical_trunk', 'apical_1', 'apical_2',
            'apical_tuft', 'apical_oblique', 'basal_1',
            'basal_2', 'basal_3'
        ]

        return dend_props, dend_names

        # self.dend_L = [102, 680, 680, 425, 255, 85, 255, 255]
        # self.dend_diam = [10.2, 7.48, 4.93, 3.4, 5.1, 6.8, 8.5, 8.5]

        # # check lengths for congruity
        # if len(self.dend_L) == len(self.dend_diam):
        #     # Zip above lists together
        #     self.dend_props = it.izip(self.dend_names, self.dend_L, self.dend_diam) 
        # else:
        #     print "self.dend_L and self.dend_diam are not the same length"
        #     print "please fix in L5_pyramidal.py"
        #     sys.exit()

    # connects sections of this cell together
    def __connect_sections(self):
        # child.connect(parent, parent_end, {child_start=0})
        # Distal
        self.list_dend[0].connect(self.soma, 1, 0)
        self.list_dend[1].connect(self.list_dend[0], 1, 0)

        self.list_dend[2].connect(self.list_dend[1], 1, 0)
        self.list_dend[3].connect(self.list_dend[2], 1, 0)

        # dend[4] comes off of dend[0](1)
        self.list_dend[4].connect(self.list_dend[0], 1, 0)

        # Proximal
        self.list_dend[5].connect(self.soma, 0, 0)
        self.list_dend[6].connect(self.list_dend[5], 1, 0)
        self.list_dend[7].connect(self.list_dend[5], 1, 0)
            
    # adds biophysics to soma
    def __biophys_soma(self):
        # set soma biophysics specified in Pyr
        # self.pyr_biophys_soma()

        # Insert 'hh' mechanism
        self.soma.insert('hh')
        self.soma.gkbar_hh = 0.01
        self.soma.gl_hh = 4.26e-5
        self.soma.el_hh = -65

        self.soma.gnabar_hh = 0.16

        # insert 'ca' mechanism
        # Units: pS/um^2
        self.soma.insert('ca')
        self.soma.gbar_ca = 60

        # insert 'cad' mechanism
        # units of tau are ms
        self.soma.insert('cad')
        self.soma.taur_cad = 20

        # insert 'kca' mechanism
        # units are S/cm^2?
        self.soma.insert('kca')
        self.soma.gbar_kca = 2e-4

        # Insert 'km' mechanism
        # Units: pS/um^2
        self.soma.insert('km')
        self.soma.gbar_km = 200 

        # insert 'cat' mechanism
        self.soma.insert('cat')
        self.soma.gbar_cat = 2e-4

        # insert 'ar' mechanism
        self.soma.insert('ar')
        self.soma.gbar_ar = 1e-6
        
    def __biophys_dends(self):
        # set dend biophysics specified in Pyr()
        # self.pyr_biophys_dends()

        # set dend biophysics not specified in Pyr()
        for sec in self.list_dend:
            # Insert 'hh' mechanism
            sec.insert('hh')
            sec.gkbar_hh = 0.01
            sec.gl_hh = 4.26e-5
            sec.gnabar_hh = 0.14
            sec.el_hh = -71

            # Insert 'ca' mechanims
            # Units: pS/um^2
            sec.insert('ca')
            sec.gbar_ca = 60

            # Insert 'cad' mechanism
            sec.insert('cad')
            sec.taur_cad = 20

            # Insert 'kca' mechanism
            sec.insert('kca')
            sec.gbar_kca = 2e-4

            # Insert 'km' mechansim
            # Units: pS/um^2
            sec.insert('km')
            sec.gbar_km = 200

            # insert 'cat' and 'ar' mechanisms
            sec.insert('cat')
            sec.gbar_cat = 2e-4
            sec.insert('ar')

        # set gbar_ar
        # Value depends on distance from the soma. Soma is set as 
        # origin by passing self.soma as a sec argument to nrn.distance()
        # Then iterate over segment nodes of dendritic sections 
        # and set gbar_ar depending on nrn.distance(seg.x), which returns
        # distance from the soma to this point on the CURRENTLY ACCESSED
        # SECTION!!!
        nrn.distance(sec=self.soma)

        for sec in self.list_dend:
            sec.push()
            for seg in sec:
                seg.gbar_ar = 1e-6 * np.exp(3e-3 * nrn.distance(seg.x))

            nrn.pop_section()

    def __synapse_create(self):
        # creates synapses onto this cell 
        # Somatic synapses
        self.soma_gabaa = self.syn_gabaa_create(self.soma(0.5))
        self.soma_gabab = self.syn_gabab_create(self.soma(0.5))

        # Dendritic synapses
        self.apicaltuft_gabaa = self.syn_gabaa_create(self.list_dend[3](0.5))
        self.apicaltuft_ampa = self.syn_ampa_create(self.list_dend[3](0.5))
        self.apicaltuft_nmda = self.syn_nmda_create(self.list_dend[3](0.5))

        self.apicaloblique_ampa = self.syn_ampa_create(self.list_dend[4](0.5))
        self.apicaloblique_nmda = self.syn_nmda_create(self.list_dend[4](0.5))

        self.basal2_ampa = self.syn_ampa_create(self.list_dend[6](0.5))
        self.basal2_nmda = self.syn_nmda_create(self.list_dend[6](0.5))

        self.basal3_ampa = self.syn_ampa_create(self.list_dend[7](0.5))
        self.basal3_nmda = self.syn_nmda_create(self.list_dend[7](0.5))

    # parallel connection function FROM all cell types TO here
    def parconnect(self, gid, gid_dict, pos_dict, p):
        # connections FROM L5Pyr TO here
        for gid_src, pos in it.izip(gid_dict['L5_pyramidal'], pos_dict['L5_pyramidal']):
            # if gid_src != gid:
            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L5Pyr_L5Pyr'],
                'A_delay': 1.,
                'lamtha': 3.
            }

            # ampa connections
            self.ncfrom_L5Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaloblique_ampa))
            self.ncfrom_L5Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.basal2_ampa))
            self.ncfrom_L5Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.basal3_ampa))

            # nmda connections
            self.ncfrom_L5Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaloblique_nmda))
            self.ncfrom_L5Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.basal2_nmda))
            self.ncfrom_L5Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.basal3_nmda))

        # connections FROM L5Basket TO here
        for gid_src, pos in it.izip(gid_dict['L5_basket'], pos_dict['L5_basket']):
            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L5Basket_L5Pyr'],
                # 'A_weight': 2.5e-2,
                'A_delay': 1.,
                'lamtha': 70.
            }

            # soma synapses are defined in Pyr()
            self.ncfrom_L5Basket.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_gabaa))
            self.ncfrom_L5Basket.append(self.parconnect_from_src(gid_src, nc_dict, self.soma_gabab))

        # connections FROM L2Pyr TO here
        for gid_src, pos in it.izip(gid_dict['L2_pyramidal'], pos_dict['L2_pyramidal']):
            # this delay is longer than most
            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L2Pyr_L5Pyr'],
                'A_delay': 3.,
                'lamtha': 3.
            }

            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.basal2_ampa))
            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.basal3_ampa))
            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaltuft_ampa))
            self.ncfrom_L2Pyr.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaloblique_ampa))

        # connections FROM L2Basket TO here
        for gid_src, pos in it.izip(gid_dict['L2_basket'], pos_dict['L2_basket']):
            nc_dict = {
                'pos_src': pos,
                'A_weight': p['gbar_L2Basket_L5Pyr'],
                'A_delay': 1.,
                'lamtha': 50.
            }

            self.ncfrom_L2Basket.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaltuft_gabaa))

    # receive from external inputs
    def parreceive(self, gid, gid_dict, pos_dict, p_ext):
        for gid_src, p_src, pos in it.izip(gid_dict['extinput'], p_ext, pos_dict['extinput']):
            if 'L5Pyr' in p_src.keys():
                nc_dict = {
                    'pos_src': pos,
                    'A_weight': p_src['L5Pyr'][0],
                    'A_delay': p_src['L5Pyr'][1],
                    'lamtha': p_src['lamtha']
                }

                if p_src['loc'] is 'proximal':
                    # print gid_src, nc_dict, self.basal2_ampa
                    # basal2_ampa, basal3_ampa, apicaloblique_ampa
                    self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.basal2_ampa))
                    self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.basal3_ampa))
                    self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaloblique_ampa))

                elif p_src['loc'] is 'distal':
                    # apical tuft
                    self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaltuft_ampa))

                    # nmda only if on the evoked input
                    if not p_src['f_input']:
                        self.ncfrom_extinput.append(self.parconnect_from_src(gid_src, nc_dict, self.apicaltuft_nmda))

    # one parreceive function to handle all types of external parreceives
    # types must be defined explicitly here
    def parreceive_ext(self, type, gid, gid_dict, pos_dict, p_ext):
        if type in ['evprox', 'evdist']:
            if self.celltype in p_ext.keys():
                gid_ev = gid + gid_dict[type][0]

                nc_dict = {
                    'pos_src': pos_dict[type][gid],
                    'A_weight': p_ext[self.celltype][0],
                    'A_delay': p_ext[self.celltype][1],
                    'lamtha': p_ext['lamtha_space']
                }

                self.ncfrom_ev.append(self.parconnect_from_src(gid_ev, nc_dict, self.basal2_ampa))
                self.ncfrom_ev.append(self.parconnect_from_src(gid_ev, nc_dict, self.basal3_ampa))
                self.ncfrom_ev.append(self.parconnect_from_src(gid_ev, nc_dict, self.apicaloblique_ampa))

        elif type == 'extgauss':
            # gid is this cell's gid
            # gid_dict is the whole dictionary, including the gids of the extgauss
            # pos_dict is also the pos of the extgauss (net origin)
            # p_ext_gauss are the params (strength, etc.)
            # doesn't matter if this doesn't do anything

            # gid shift is based on L2_pyramidal cells NOT L5
            # I recognize this is ugly (hack)
            # gid_shift = gid_dict['extgauss'][0] - gid_dict['L2_pyramidal'][0]
            if 'L5_pyramidal' in p_ext.keys():
                gid_extgauss = gid + gid_dict['extgauss'][0]

                nc_dict = {
                    'pos_src': pos_dict['extgauss'][gid],
                    'A_weight': p_ext['L5_pyramidal'][0],
                    'A_delay': p_ext['L5_pyramidal'][1],
                    'lamtha': p_ext['lamtha']
                }

                self.ncfrom_extgauss.append(self.parconnect_from_src(gid_extgauss, nc_dict, self.basal2_ampa))
                self.ncfrom_extgauss.append(self.parconnect_from_src(gid_extgauss, nc_dict, self.basal3_ampa))
                self.ncfrom_extgauss.append(self.parconnect_from_src(gid_extgauss, nc_dict, self.apicaloblique_ampa))

        elif type == 'extpois':
            if self.celltype in p_ext.keys():
                gid_extpois = gid + gid_dict['extpois'][0]

                nc_dict = {
                    'pos_src': pos_dict['extpois'][gid],
                    'A_weight': p_ext[self.celltype][0],
                    'A_delay': p_ext[self.celltype][1],
                    'lamtha': p_ext['lamtha_space']
                }

                self.ncfrom_extpois.append(self.parconnect_from_src(gid_extpois, nc_dict, self.basal2_ampa))
                self.ncfrom_extpois.append(self.parconnect_from_src(gid_extpois, nc_dict, self.basal3_ampa))
                self.ncfrom_extpois.append(self.parconnect_from_src(gid_extpois, nc_dict, self.apicaloblique_ampa))

    # Define 3D shape and position of cell. By default neuron uses xy plane for
    # height and xz plane for depth. This is opposite for model as a whole, but
    # convention is followed in this function for ease use of gui. 
    def __set_3Dshape(self):
        # set 3D shape of soma by calling shape_soma from class Cell
        # print "WARNING: You are setting 3d shape geom. You better be doing"
        # print "gui analysis and not numerical analysis!!"
        self.shape_soma()

        # soma proximal coords
        x_prox = 0
        y_prox = 0

        # soma distal coords
        x_distal = 0
        y_distal = self.soma.L

        # dend 0-3 are major axis, dend 4 is branch
        # deal with distal first along major cable axis
        # the way this is assigning variables is ugly/lazy right now
        for i in range(0, 4):
            nrn.pt3dclear(sec=self.list_dend[i])

            # x_distal and y_distal are the starting points for each segment
            # these are updated at the end of the loop
            nrn.pt3dadd(0, y_distal, 0, self.dend_diam[i], sec=self.list_dend[i])

            # update x_distal and y_distal after setting them
            # x_distal += dend_dx[i]
            y_distal += self.dend_L[i]

            # add next point
            nrn.pt3dadd(0, y_distal, 0, self.dend_diam[i], sec=self.list_dend[i])

        # now deal with dend 4
        # dend 4 will ALWAYS be positioned at the end of dend[0]
        nrn.pt3dclear(sec=self.list_dend[4])

        # activate this section with 'sec=self.list_dend[i]' notation
        x_start = nrn.x3d(1, sec=self.list_dend[0])
        y_start = nrn.y3d(1, sec=self.list_dend[0])

        nrn.pt3dadd(x_start, y_start, 0, self.dend_diam[4], sec=self.list_dend[4])
        # self.dend_L[4] is subtracted because lengths always positive, 
        # and this goes to negative x
        nrn.pt3dadd(x_start-self.dend_L[4], y_start, 0, self.dend_diam[4], sec=self.list_dend[4])

        # now deal with proximal dends
        for i in range(5, 8):
            nrn.pt3dclear(sec=self.list_dend[i])

        # deal with dend 5, ugly. sorry.
        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[i], sec=self.list_dend[5])
        y_prox += -self.dend_L[5]

        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[5],sec=self.list_dend[5])

        # x_prox, y_prox are now the starting points for BOTH of last 2 sections
        # dend 6
        # Calculate x-coordinate for end of dend
        dend6_x = -self.dend_L[6] * np.sqrt(2)/2
        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[6], sec=self.list_dend[6])
        nrn.pt3dadd(dend6_x, y_prox-self.dend_L[6] * np.sqrt(2)/2, 
                    0, self.dend_diam[6], sec=self.list_dend[6])

        # dend 7
        # Calculate x-coordinate for end of dend
        dend7_x = self.dend_L[7] * np.sqrt(2)/2
        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[7], sec=self.list_dend[7])
        nrn.pt3dadd(dend7_x, y_prox-self.dend_L[7] * np.sqrt(2)/2, 
                    0, self.dend_diam[7], sec=self.list_dend[7])

        # set 3D position
        # z grid position used as y coordinate in nrn.pt3dchange() to satisfy
        # gui convention that y is height and z is depth. In nrn.pt3dchange()
        # x and z components are scaled by 100 for visualization clarity
        self.soma.push()
        for i in range(0, int(nrn.n3d())):
            nrn.pt3dchange(i, self.pos[0]*100 + nrn.x3d(i), -self.pos[2] + nrn.y3d(i), 
                           self.pos[1] * 100 + nrn.z3d(i), nrn.diam3d(i))

        nrn.pop_section()
