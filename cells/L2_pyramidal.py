# L2_pyramidal.py - est class def for layer 2 pyramidal cells
#
# v 0.2.24
# rev 2012-08-07 (SL: Added connections to relevant apical sections of L5Pyr)
# last rev: (SL: Removed one incorrect connection to basilar section)

from neuron import h as nrn
from class_cell import Pyr
import sys
import itertools as it
from math import sqrt

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted

class L2Pyr(Pyr):
    def __init__(self, pos):
        # Pyr.__init__(self, pos, L, diam, Ra, cm)
        Pyr.__init__(self, pos, 22.1, 23.4, 0.6195, 'L2Pyr')

        # prealloc namespace for dend properties
        # set in dend_props()
        self.dend_names = []
        self.dend_L = []
        self.dend_diam = []
        self.cm = 0.6195

        # create lists of connections FROM this cell TO target
        self.ncto_L2Basket = []
        self.ncto_L5Basket = []
        self.ncto_L5Pyr_apicaltuft = []
        self.ncto_L5Pyr_apicaloblique = []
        self.ncto_L5Pyr_basal2 = []
        self.ncto_L5Pyr_basal3 = []

        # geometry
        self.set_dend_props()
        self.create_dends(self.dend_props, self.cm)
        self.connect_sections()
        # self.shape_change()
        # self.geom_set(self.cm)

        # biophysics
        self.biophys_soma()
        self.biophys_dends()

    # connects this cell to L2Basket
    # essentially identical to connect_to_L5Basket in L5Pyramidal.py
    def connect_to_L2Basket(self, L2Basket):
        self.ncto_L2Basket.append(self.sec_to_target(self.soma, 0.5, L2Basket.soma_ampa))

        d = self.distance(L2Basket)
        tau = 3.

        # set the weights using syn_weight() from Cell()
        self.syn_weight(self.ncto_L2Basket[-1], 5e-4, d, tau)

        # set the delay using syn_delay() from Cell()
        self.syn_delay(self.ncto_L2Basket[-1], 1, d, tau)

    def connect_to_L5Basket(self, L5Basket):
        self.ncto_L5Basket.append(self.sec_to_target(self.soma, 0.5, L5Basket.soma_ampa))

        d = self.distance(L5Basket)
        tau = 3.

        # set the weights using syn_weight() from Cell()
        self.syn_weight(self.ncto_L5Basket[-1], 2.5e-4, d, tau)

        # set the delay using syn_delay() from Cell()
        self.syn_delay(self.ncto_L5Basket[-1], 1, d, tau)

    def connect_to_L5Pyr(self, L5Pyr):
        self.ncto_L5Pyr_basal2.append(self.sec_to_target(self.soma, 0.5, L5Pyr.basal2_ampa))
        self.ncto_L5Pyr_basal3.append(self.sec_to_target(self.soma, 0.5, L5Pyr.basal3_ampa))
        self.ncto_L5Pyr_apicaltuft.append(self.sec_to_target(self.soma, 0.5, L5Pyr.apicaltuft_ampa))
        self.ncto_L5Pyr_apicaloblique.append(self.sec_to_target(self.soma, 0.5, L5Pyr.apicaloblique_ampa))

        d = self.distance(L5Pyr)
        tau = 3.

        # set the weights using syn_weight() from Cell()
        self.syn_weight(self.ncto_L5Pyr_apicaltuft[-1], 2.5e-4, d, tau)
        self.syn_weight(self.ncto_L5Pyr_apicaloblique[-1], 2.5e-4, d, tau)
        self.syn_weight(self.ncto_L5Pyr_basal2[-1], 2.5e-4, d, tau)
        self.syn_weight(self.ncto_L5Pyr_basal3[-1], 2.5e-4, d, tau)

        # set the delay using syn_delay() from Cell()
        self.syn_delay(self.ncto_L5Pyr_apicaltuft[-1], 3, d, tau)
        self.syn_delay(self.ncto_L5Pyr_apicaloblique[-1], 3, d, tau)
        self.syn_delay(self.ncto_L5Pyr_basal2[-1], 3, d, tau)
        self.syn_delay(self.ncto_L5Pyr_basal3[-1], 3, d, tau)

    # Sets dendritic properties
    def set_dend_props(self):
        # Hardcode dend properties
        self.dend_names = ['apical_trunk', 'apical_1', 'apical_tuft',
                           'apical_obliq', 'basal_1', 'basal_2', 'basal_3'
        ]

        self.dend_L = [59.5, 306, 238, 340, 85, 255, 255]
        self.dend_diam = [4.25, 4.08, 3.40, 3.91, 4.25, 2.72, 2.72]
        
        # check lengths for congruity
        if len(self.dend_L) == len(self.dend_diam):
            # Zip above lists together
            self.dend_props = it.izip(self.dend_names, self.dend_L, self.dend_diam)        
        else:   
            print "self.dend_L and self.dend_diam are not the same length"
            print "please fix in L5_pyramidal.py"
            sys.exit()

    # Connects sections of THIS cell together
    def connect_sections(self):
        # connect(parent, parent_end, {child_start=0})
        # Distal
        self.list_dend[0].connect(self.soma, 1, 0)
        self.list_dend[1].connect(self.list_dend[0], 1, 0)

        self.list_dend[2].connect(self.list_dend[1], 1, 0)

        # dend[4] comes off of dend[0](1)
        self.list_dend[3].connect(self.list_dend[0], 1, 0)

        # Proximal
        self.list_dend[4].connect(self.soma, 0, 0)
        self.list_dend[5].connect(self.list_dend[4], 1, 0)
        self.list_dend[6].connect(self.list_dend[4], 1, 0)

    # Adds biophysics to soma
    def biophys_soma(self):
        # set soma biophysics specified in Pyr
        self.pyr_biophys_soma()

        # set 'hh' mechanism values not specified in Pyr
        self.soma.gnabar_hh = 0.18
                
        # set gbar_km
        # Units: pS/um^2
        self.soma.gbar_km = 250

    # Defining biophysics for dendrites
    def biophys_dends(self):
        # set dend biophysics specified in Pyr()
        self.pyr_biophys_dends()

        # set dend biophysics not specidied in Pyr()
        for sec in self.list_dend:
            # neuron syntax is used to set values for mechanisms
            # sec.gbar_mech = x sets value of gbar for mech to x for all segs
            # in a section. This method is significantlt faster than using
            # a for loop to iterate over all segments to set mech values

            # set 'hh' mechanisms not set in Pyr()
            sec.gnabar_hh = 0.15
            sec.el_hh = -65

            # set gbar_km 
            # Units: pS/um^2
            sec.gbar_km = 250

    def shape_change(self):
        # set 3d shape of soma by calling shape_soma from class Cell
        print "Warning: You are setiing 3d shape geom. You better be doing"
        print "gui analysis and not numerical analysis!!"
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

            # print x_distal, y_distal
            # x_distal and y_distal are the starting points for each segment
            # these are updated at the end of the loop
            nrn.pt3dadd(0, y_distal, 0, self.dend_diam[i], sec=self.list_dend[i])

            # update x_distal and y_distal after setting them
            # x_distal += dend_dx[i]
            y_distal += self.dend_L[i]

            # print x_distal, y_distal
            # add next point
            nrn.pt3dadd(0, y_distal, 0, self.dend_diam[i], sec=self.list_dend[i])

        # now deal with dend 4
        # dend 4 will ALWAYS be positioned at the end of dend[0]
        nrn.pt3dclear(sec=self.list_dend[3])

        # activate this section
        self.list_dend[0].push()
        x_start = nrn.x3d(1)
        y_start = nrn.y3d(1)
        nrn.pop_section()

        nrn.pt3dadd(x_start, y_start, 0, self.dend_diam[3], sec=self.list_dend[3])
        # self.dend_L[3] is subtracted because lengths always positive, 
        # and this goes to negative x
        nrn.pt3dadd(x_start-self.dend_L[3], y_start, 0, self.dend_diam[3], sec=self.list_dend[3])
        # print nrn.n3d(sec=self.list_dend[0])

        # now deal with proximal dends
        for i in range(4, 7):
            nrn.pt3dclear(sec=self.list_dend[i])

        # deal with dend 5, ugly. sorry.
        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[i], sec=self.list_dend[4])
        # x_prox += dend_dx[4]
        y_prox += -self.dend_L[4]

        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[4],sec=self.list_dend[4])

        # x_prox, y_prox are now the starting points for BOTH of the last 2 sections
        # dend 6
        nrn.pt3dadd(0, y_prox, 0, self.dend_diam[5], sec=self.list_dend[5])
        nrn.pt3dadd(-self.dend_L[5]*sqrt(2)/2, y_prox-self.dend_L[5]*sqrt(2)/2, 0, self.dend_diam[5], sec=self.list_dend[5])

        # dend 7
        nrn.pt3dadd(0, y_prox, 0, self.dend_diam[6], sec=self.list_dend[6])
        nrn.pt3dadd(self.dend_L[6]*sqrt(2)/2, y_prox-self.dend_L[6]*sqrt(2)/2, 0, self.dend_diam[6], sec=self.list_dend[6])
