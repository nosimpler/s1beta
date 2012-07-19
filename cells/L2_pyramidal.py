# L2_pyramidal.py - est class def for layer 2 pyramidal cells
#
# v 0.2.0
# rev 2012-07-18 (correct biophysics and mechanisms added
# last rev:(created)
#

from neuron import h as nrn
from class_cell import Cell
from sys import exit
from math import sqrt
# from topol import L5_pyr_shape

class L2Pyr(Cell):
    def __init__(self):
        # Cell.__init__(self, L, diam, Ra, cm)
        Cell.__init__(self, 22.1, 23.4, 0.6195)
        # super(Inherit_L2Pyr, self).__init__()

        # sections of these cells
        self.list_dend = []
        # self.list_dend_prox = []
        # self.list_dend_dist = []

        # prealloc namespace for dend properties
        # props be set in create_dends()
        self.dend_L = []
        self.dend_diam = []

        # N_dend is an int
        # we expect this will be overwritten!!
        # SL doesn't like this necessarily
        self.N_dend = 0

        # geometry
        # self.create_sections(8)
        self.create_dends()
        self.connect_sections()
        # self.shape_change()
        self.geom_set()

        # biophysics
        self.biophys_soma()
        self.biophysics_dends()
       
        # creation of synapses inherited method from Cell()
        # synapse on THIS cell needs to be RECEIVING FROM Inh
        # segment on soma specified here
        self.syn_gabaa_create(self.soma(0.5))
        # self.synapses_create()

    # just a dummy test
    # adding biophysics to soma
    def biophys_soma(self):
        # set 'hh' mechanism values
        self.soma.gnabar_hh = 0.18
        self.soma.gkbar_hh = 0.01
        self.soma.gl_hh = 0.0000426
        #units: S/cm^2?
        self.soma.el_hh = -65
                
        # insert 'km' mechanism
        self.soma.insert('km')
        self.soma.gbar_km = 250
        # units pS/um^2

        # insert 'cat' mechanism
        # self.soma.insert('cat')
        # self.soma.gbar_cat = 0.0
        
        # insert 'ar' mechanism
        # self.soma.insert('ar')
        # self.soma.gbar_ar= 0.0
       
        # this is new, pythonic syntax, I believe
        # equivalent to gbar_ca = 60
        # having trouble testing the effect of this
        # for sec in self.soma:
        #     sec.ca.gbar = 60
        #     # print sec.ca.gbar

    def biophysics_dends(self):
        for sec in self.list_dend:
            # nueron syntax is used to set values for mechanisms
            # sec.gbar_mech = x sets value of gbar for mech to x for all segs
            # in a section. This method is significantlt faster than using
            # a for loop to iterate over all segments to set mech values

            # insert 'hh' mechanism    
            sec.insert('hh')    
            sec.gnabar_hh = 0.15
            sec.gkbar_hh = 0.01 
            sec.gl_hh = 0.0000426
            # units S/cm^2?
            sec.el_hh = -65

            # insert 'km' mechanism
            sec.insert('km')
            sec.gbar_km = 250
            # units pS/um^2

            # # insert 'cat' mechansim
            # sec.insert('cat')
            # sec.gbar_cat = 0.0

            # # insert 'ar' mechanism
            # sec.insert('ar')
            # sec.gbar_ar = 0.0            

    # Create dendritic sections and sets lengths and diameters for each section
    # dend lengths and dend diams are hardcoded here
    def create_dends(self):
    # def create_sections(self, N_dend):
        # hard code dend lengths and diams
        # dend order: [ap trunk, ap #1, ap tuft, obliq, bas trunk, bas, bas]
        self.dend_L = [59.5, 306, 238, 340, 85, 255, 255]
        self.dend_diam = [4.25, 4.08, 3.40, 3.91, 4.25, 2.72, 2.72]

        # check lengths for congruity
        # this needs to be figured out
        if len(self.dend_L) == len(self.dend_diam):
            self.N_dend = len(self.dend_L)
        else:
            print "self.dend_L and self.dend_diam are not the same length. Please fix in L5_pyramidal.py"
            exit()

        # Trying to create sections directly
        for i in range(0, self.N_dend):
            self.list_dend.append(nrn.Section())
            # self.list_dend[i].L = self.dend_L[i]
            # self.list_dend[i].diam = self.dend_diam[i]
            
            # move to a new function that specifies biophysics for dends
            # self.list_dend[i].insert('hh')
            # print self.list_dend[i]
            
    # set the geometry, including the nseg.
    # geom_set separate for future and to get around shape_change
    def geom_set(self):
        # Check with SL: set soma geom here too?
        # The pythonic way of setting length and diameter 
        for dend, L, diam in zip(self.list_dend, self.dend_L, self.dend_diam):
            dend.L = L
            dend.diam = diam
            dend.Ra = 200
            dend.cm = 0.6195
        
        # set nseg for each dendritic section (soma.nseg = 1 by default)
        for dend in self.list_dend:
            if dend.L>50:
                dend.nseg = int(dend.L/50)
            # print dend.nseg
 
        # set length and diameter of dends
        # for i in range (0, len(self.dend_L)):
        #     self.list_dend[i].L = self.dend_L[i]
        #     self.list_dend[i].diam = self.dend_diam[i]

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

    def print_params(self):
        print "L2 PN Params:"
        print "Soma length:", self.soma.L
        print "Soma diam:", self.soma.diam
        print "Soma Ra:", self.soma.Ra
        print "Soma cm:", self.soma.cm

        print "\ndendritic lengths:"
        for i in range(0, self.N_dend):
            print self.list_dend[i].L

        print "\ndendritic diameters:"
        for i in range(0, self.N_dend):
            print self.list_dend[i].diam

        print "\ndendritic axial resistance:"
        for i in range(0, self.N_dend):
            print self.list_dend[i].Ra

        print "\ndendritic capitance:"
        for i in range(0, self.N_dend):
            print self.list_dend[i].cm

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

        # nrn.pt3dclear(sec=self.soma)
        # nrn.pt3dadd(x_prox, y_prox, 0, 1, sec=self.soma)
        # nrn.pt3dadd(x_distal, y_distal, 0, 1, sec=self.soma)

        # changes in x and y pt3d coords
        # dend_dx = [ 0,    0,   0,   0,-150,   0, -106,  106]
        # dend_dy = [60,  250, 400, 400,   0, -50, -106, -106]

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

        # print "before L: ", self.list_dend[i].L
        # self.list_dend[i].L = 150
        # print "after L: ", self.list_dend[i].L

        # print type(nrn.x3d(1.0))
        # nrn.pop_section()
        # nrn.pt3dadd(x_distal, y_distal)

        # nrn.pt3dclear(sec=self.list_dend[0])
        # nrn.pt3dadd(0, 23, 0, 1, sec=self.list_dend[0])
        # nrn.pt3dadd(0, 83, 0, 1, sec=self.list_dend[0])
