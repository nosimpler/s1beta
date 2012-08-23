# L5_pyramidal.py - establish class def for layer 5 pyramidal cells
#
# v 0.4.3
# rev 2012-08-22 (MS: shape_change() renamed set_3Dshape())
# last rev: (MS: Activate self.set_3Dshape() for 3d shape)

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
        # Pyr.__init__(self, pos, L, diam, Ra, cm, {prefix})
        Pyr.__init__(self, pos, 39, 28.9, 0.85, 'L5Pyr')

        # preallocate namespaces for dend properties
        # set in dend_props()
        self.dend_names = []
        self.dend_L = []
        self.dend_diam = []
        self.cm = 0.85

        # create lists of connections FROM this cell TO target
        self.ncto_L5Pyr_apicaloblique_ampa = []
        self.ncto_L5Pyr_apicaloblique_nmda = []

        self.ncto_L5Pyr_basal2_ampa = []
        self.ncto_L5Pyr_basal2_nmda = []

        self.ncto_L5Pyr_basal3_ampa = []
        self.ncto_L5Pyr_basal3_nmda = []

        self.ncto_L5Basket = []

        self.ncto_L2Pyr = []
        self.ncto_L2Basket = []

        # Geometry
        self.set_dend_props()
        self.create_dends(self.dend_props, self.cm)
        self.connect_sections()
        self.set_3Dshape()

        # biophysics
        self.biophys_soma()
        self.biophys_dends()

        # dipole_insert() comes from Cell()
        self.dipole_insert()

        # create synapses
        self.synapse_create()

    def synapse_create(self):
        # creates synapses onto this cell in distal sections unique to this cell type
        # print self.soma(0.5), self.list_dend[3](0.5)
        self.apicaltuft_gabaa = self.syn_gabaa_create(self.list_dend[3](0.5))
        self.apicaltuft_ampa = self.syn_ampa_create(self.list_dend[3](0.5))
        self.apicaltuft_nmda = self.syn_nmda_create(self.list_dend[3](0.5))

        self.apicaloblique_ampa = self.syn_ampa_create(self.list_dend[4](0.5))
        self.apicaloblique_nmda = self.syn_nmda_create(self.list_dend[4](0.5))

        self.basal2_ampa = self.syn_ampa_create(self.list_dend[6](0.5))
        self.basal2_nmda = self.syn_nmda_create(self.list_dend[6](0.5))

        self.basal3_ampa = self.syn_ampa_create(self.list_dend[7](0.5))
        self.basal3_nmda = self.syn_nmda_create(self.list_dend[7](0.5))

    # Connects this cell to a synapse 'soma_ampa' on the supplied L5Basket cell
    # uses 'soma_to_target' from class 'Cell()' inheritance
    # Doing this here gives us easy access to position properties
    # essentially identical to connect_to_L2Basket in L2_pyramidal.py
    def connect_to_L5Basket(self, L5Basket):
        self.ncto_L5Basket.append(self.sec_to_target(self.soma, 0.5, L5Basket.soma_ampa))

        d = self.distance(L5Basket)
        lamtha = 3.

        # set the weights using syn_weight() from Cell()
        self.syn_weight(self.ncto_L5Basket[-1], 5e-4, d, lamtha)

        # set the delay using syn_delay() from Cell()
        self.syn_delay(self.ncto_L5Basket[-1], 1., d, lamtha)

    def connect_to_L5Pyr(self, L5Pyr_post):
        # ampa connections
        self.ncto_L5Pyr_apicaloblique_ampa.append(self.sec_to_target(self.soma, 0.5, L5Pyr_post.apicaloblique_ampa))
        self.ncto_L5Pyr_basal2_ampa.append(self.sec_to_target(self.soma, 0.5, L5Pyr_post.basal2_ampa))
        self.ncto_L5Pyr_basal3_ampa.append(self.sec_to_target(self.soma, 0.5, L5Pyr_post.basal3_ampa))

        # nmda connections
        self.ncto_L5Pyr_apicaloblique_nmda.append(self.sec_to_target(self.soma, 0.5, L5Pyr_post.apicaloblique_nmda))
        self.ncto_L5Pyr_basal2_nmda.append(self.sec_to_target(self.soma, 0.5, L5Pyr_post.basal2_nmda))
        self.ncto_L5Pyr_basal3_nmda.append(self.sec_to_target(self.soma, 0.5, L5Pyr_post.basal3_nmda))

        d = self.distance(L5Pyr_post)
        lamtha = 3.

        # set the weights using syn_weight() from Cell()
        self.syn_weight(self.ncto_L5Pyr_apicaloblique_ampa[-1], 5e-4, d, lamtha)
        self.syn_weight(self.ncto_L5Pyr_basal2_ampa[-1], 5e-4, d, lamtha)
        self.syn_weight(self.ncto_L5Pyr_basal3_ampa[-1], 5e-4, d, lamtha)

        self.syn_weight(self.ncto_L5Pyr_apicaloblique_nmda[-1], 5e-4, d, lamtha)
        self.syn_weight(self.ncto_L5Pyr_basal2_nmda[-1], 5e-4, d, lamtha)
        self.syn_weight(self.ncto_L5Pyr_basal3_nmda[-1], 5e-4, d, lamtha)

        # set the delay using syn_delay() from Cell()
        self.syn_delay(self.ncto_L5Pyr_apicaloblique_ampa[-1], 1., d, lamtha)
        self.syn_delay(self.ncto_L5Pyr_basal2_ampa[-1], 1., d, lamtha)
        self.syn_delay(self.ncto_L5Pyr_basal3_ampa[-1], 1., d, lamtha)

        self.syn_delay(self.ncto_L5Pyr_apicaloblique_nmda[-1], 1., d, lamtha)
        self.syn_delay(self.ncto_L5Pyr_basal2_nmda[-1], 1., d, lamtha)
        self.syn_delay(self.ncto_L5Pyr_basal3_nmda[-1], 1., d, lamtha)

    # writes to self.dend_props list of tuples
    def set_dend_props(self):
        # Hard coded dend properties
        self.dend_names = ['apical_trunk', 'apical_1', 'apical_2',
                           'apical_tuft', 'apical_oblique', 'basal_1', 
                           'basal_2', 'basal_3'
        ]

        self.dend_L = [102, 680, 680, 425, 255, 85, 255, 255]
        self.dend_diam = [10.2, 7.48, 4.93, 3.4, 5.1, 6.8, 8.5, 8.5]

        # check lengths for congruity
        if len(self.dend_L) == len(self.dend_diam):
            # Zip above lists together
            self.dend_props = it.izip(self.dend_names, self.dend_L, self.dend_diam) 
        else:
            print "self.dend_L and self.dend_diam are not the same length"
            print "please fix in L5_pyramidal.py"
            sys.exit()

    # connects sections of this cell together
    def connect_sections(self):
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
    def biophys_soma(self):
        # set soma biophysics specified in Pyr
        self.pyr_biophys_soma()

        # set hh params not set in Pyr()
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

        # set gbar_km
        # Units: pS/um^2
        self.soma.gbar_km = 200 

        # insert 'cat' mechanism
        self.soma.insert('cat')
        self.soma.gbar_cat = 2e-4

        # insert 'ar' mechanism
        self.soma.insert('ar')
        self.soma.gbar_ar = 1e-6
        
    def biophys_dends(self):
        # set dend biophysics specified in Pyr()
        self.pyr_biophys_dends()

        # set dend biophysics not specified in Pyr()
        for sec in self.list_dend:
            # set hh params not set in Pyr()
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

            # set gbar_km
            # Units: pS/um^2
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
                # print nrn.distance(seg.x)
                # seg.gbar_cat = 2e-4*exp(0.0*nrn.distance(seg.x))
                seg.gbar_ar = 1e-6 * np.exp(3e-3 * nrn.distance(seg.x))
                # print nrn.distance(seg.x), seg.gbar_ar 

            nrn.pop_section()

    # Define 3D shape and position of cell. By default neuron uses xy plane for
    # height and xz plane for depth. This is opposite for model as a whole, but
    # convention is followed in this function for ease use of gui. 
    def set_3Dshape(self):
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
