# L5_pyramidal.py - establish class def for layer 5 pyramidal cells
#
# v 0.2.8
# rev 2012-07_23 (MS: added units
# last rev: (MS: L5Pyr inherits props from Pyr())

from neuron import h as nrn
from class_cell import Pyr
import sys 
from math import sqrt, exp
import itertools as it

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted
# units for taur: ms

class L5Pyr(Pyr):
    def __init__(self):
        # Pyr.__init__(self, L, diam, Ra, cm)
        Pyr.__init__(self, 39, 28.9, 0.85, 'L5_')

        # preallocate namespaces for dend properties
        # set in dend_props()
        self.dend_names = []
        self.dend_L = []
        self.dend_diam = []
        self.cm = 0.85

        # create lists of connections FROM this cell TO target
        self.ncto_L5Basket = []
        self.ncto_L2Pyr = []
        self.ncto_L2Basket = []

        # geometry
        self.set_dend_props()
        self.create_dends(self.dend_props, self.cm)
        # self.create_dends(self.dend_L, self.dend_diam, self.dend_names)
        self.connect_sections()
        # self.shape_change()
        # self.geom_set(self.cm)

        # biophysics
        self.biophys_soma()
        self.biophys_dends()

    def set_dend_props(self):
        # Hardcode dend properties
        self.dend_names = ['apical_trunk', 'apical_1', 'apical_2',
                           'apical_tuft', 'apical_obliq', 'basal_1', 
                           'basal_2', 'basal_3']
        self.dend_L = [102, 680, 680, 425, 255, 85, 255, 255]
        self.dend_diam = [10.2, 7.48, 4.93, 3.4, 5.1, 6.8, 8.5, 8.5]
        # self.cm = 0.85

        # check lengths for congruity
        if len(self.dend_L) == len(self.dend_diam):
            # Zip above lists together
            self.dend_props = it.izip(self.dend_names, self.dend_L, self.dend_diam) 
        else:
            print "self.dend_L and self.dend_diam are not the same length"
            print "please fix in L5_pyramidal.py"
            sys.exit()

    def connect_sections(self):
        # connect(parent, parent_end, {child_start=0})
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
            
    # adding biophysics to soma
    def biophys_soma(self):
        # set soma biophysics specified in Pyr
        self.Pyrbiophys_soma()

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
        # set dend biophysics specified in Pyr
        self.Pyrbiophys_dends()

        # set dend biophysics not specified in Pyr
        for sec in self.list_dend:
            # set hh params not set in Pyr
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
                # seg.gbar_cat = 0.0002*exp(0.0*nrn.distance(seg.x))
                seg.gbar_ar = 0.000001*exp(0.003*nrn.distance(seg.x))
                # print nrn.distance(seg.x), seg.gbar_ar 
            nrn.pop_section()

    def shape_change(self):
        # set 3d shape of soma by calling shape_soma from class Cell
        print "Warning: You are setting 3d shape geom. You better be doing"
        print "gui analysis and not numerical analysis!!"
        self.shape_soma()

        # soma proximal coords
        x_prox = 0
        y_prox = 0

        # soma distal coords
        x_distal = 0
        y_distal = self.soma.L

        # nrn.pt3dclear(sec=self.soma)
        # nrn.pt3dadd(x_prox, y_prox, 0, 1, sec=self.soma)
        # nrn.pt3dadd(x_distal, y_distal, 0, 1, sec=self.soma)

        # changes in x and y pt3d coords
        # dend_dx = [ 0,    0,   0,   0,-150,   0, -106,  106]
        # dend_dy = [60,  250, 400, 400,   0, -50, -106, -106]

        # dend 0-3 are major axis, dend 4 is branch
        # deal with distal first along major cable axis
        # the way this is assigning variables is ugly/lazy right now
        for i in range(0, 4):
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
        nrn.pt3dclear(sec=self.list_dend[4])

        # activate this section
        self.list_dend[0].push()
        x_start = nrn.x3d(1)
        y_start = nrn.y3d(1)
        nrn.pop_section()

        nrn.pt3dadd(x_start, y_start, 0, self.dend_diam[4], sec=self.list_dend[4])
        # self.dend_L[4] is subtracted because lengths always positive, 
        # and this goes to negative x
        nrn.pt3dadd(x_start-self.dend_L[4], y_start, 0, self.dend_diam[4], sec=self.list_dend[4])
        # print nrn.n3d(sec=self.list_dend[0])

        # now deal with proximal dends
        for i in range(5, 8):
            nrn.pt3dclear(sec=self.list_dend[i])

        # deal with dend 5, ugly. sorry.
        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[i], sec=self.list_dend[5])
        # x_prox += dend_dx[5]
        y_prox += -self.dend_L[5]

        nrn.pt3dadd(x_prox, y_prox, 0, self.dend_diam[5],sec=self.list_dend[5])

        # x_prox, y_prox are now the starting points for BOTH of the last 2 sections
        # dend 6
        nrn.pt3dadd(0, y_prox, 0, self.dend_diam[6], sec=self.list_dend[6])
        nrn.pt3dadd(-self.dend_L[6]*sqrt(2)/2, y_prox-self.dend_L[6]*sqrt(2)/2, 0, self.dend_diam[6], sec=self.list_dend[6])

        # dend 7
        nrn.pt3dadd(0, y_prox, 0, self.dend_diam[7], sec=self.list_dend[7])
        nrn.pt3dadd(self.dend_L[7]*sqrt(2)/2, y_prox-self.dend_L[7]*sqrt(2)/2, 0, self.dend_diam[7], sec=self.list_dend[7])
