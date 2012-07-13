# L5_pyramidal.py - est class def for layer 5 pyramidal cells
#
# v 0.1.1
# rev 2012-07-12 (explicitly set Ra and cm for all sections including soma)
# last rev: (added geom_set routine to be tested)

from neuron import h
from class_cell import Cell
from sys import exit
from math import sqrt

class L5Pyr(Cell):
    def __init__(self):
        # Cell.__init__(self, L, diam, Ra, cm)
        Cell.__init__(self, 39, 28.9, 0.85)
        # super(Inherit_L5Pyr, self).__init__()

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

        # synapse on THIS cell needs to be RECEIVING FROM Inh
        # this probably should be done in a fn
        # but best way is unclear unless other synapses are done
        self.syn = h.Exp2Syn(self.soma(0.5))
        self.syn.e = -80
        self.syn.tau1 = 1
        self.syn.tau2 = 20

    # just a dummy test
    # adding biophysics to soma
    def biophys_soma(self):
        # insert 'ca' mechanism
        self.soma.insert('ca')

        # this is new, pythonic syntax, I believe
        # equivalent to gbar_ca = 60
        # having trouble testing the effect of this
        for sec in self.soma:
            sec.ca.gbar = 60
            # print sec.ca.gbar

    # this replicates topol
    # this function will be deprecated in favor of create_sections2 below
    # def create_sections(self, N_dend):
        # Trying to create sections directly
        # for i in range(0, N_dend):
            # self.list_dend.append(h.Section())
            # self.list_dend[i].insert('hh')
            # print self.list_dend[i]

    # Creates dendritic sections and sets lengths and diameters for each section
    # dend lengths and dend diams are hardcoded here
    def create_dends(self):
    # def create_sections(self, N_dend):
        # hard code dend lengths and diams
        self.dend_L = [102, 680, 680, 425, 255, 85, 255, 255]
        self.dend_diam = [10.2, 7.48, 4.93, 3.4, 5.1, 6.8, 8.5, 8.5]

        # check lengths for congruity
        # this needs to be figured out
        if len(self.dend_L) == len(self.dend_diam):
            self.N_dend = len(self.dend_L)
        else:
            print "self.dend_L and self.dend_diam are not the same length. Please fix in L5_pyramidal.py"
            exit()

        # Trying to create sections directly
        for i in range(0, self.N_dend):
            self.list_dend.append(h.Section())
            # self.list_dend[i].L = self.dend_L[i]
            # self.list_dend[i].diam = self.dend_diam[i]
            
            # move to a new function that specifies biophysics for dends
            self.list_dend[i].insert('hh')
            # print self.list_dend[i]
            
    # set the geometry, including the nseg.
    # geom_set separate for future and to get around shape_change
    def geom_set(self):
        # The pythonic way of setting length and diameter 
        for dend, L, diam in zip(self.list_dend, self.dend_L, self.dend_diam):
            dend.L = L
            dend.diam = diam
            dend.Ra = 200
            dend.cm = 0.85
        
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
        self.list_dend[3].connect(self.list_dend[2], 1, 0)

        # dend[4] comes off of dend[0](1)
        self.list_dend[4].connect(self.list_dend[0], 1, 0)

        # Proximal
        self.list_dend[5].connect(self.soma, 0, 0)
        self.list_dend[6].connect(self.list_dend[5], 1, 0)
        self.list_dend[7].connect(self.list_dend[5], 1, 0)

    def print_params(self):
        print "L5 PN Params:"
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
        print "Warning: You are setting 3d shape geom. You better be doing"
        print "gui analysis and not numerical analysis!!"
        self.shape_soma()

        # soma proximal coords
        x_prox = 0
        y_prox = 0

        # soma distal coords
        x_distal = 0
        y_distal = self.soma.L

        # h.pt3dclear(sec=self.soma)
        # h.pt3dadd(x_prox, y_prox, 0, 1, sec=self.soma)
        # h.pt3dadd(x_distal, y_distal, 0, 1, sec=self.soma)

        # changes in x and y pt3d coords
        # dend_dx = [ 0,    0,   0,   0,-150,   0, -106,  106]
        # dend_dy = [60,  250, 400, 400,   0, -50, -106, -106]

        # dend 0-3 are major axis, dend 4 is branch
        # deal with distal first along major cable axis
        # the way this is assigning variables is ugly/lazy right now
        for i in range(0, 4):
            h.pt3dclear(sec=self.list_dend[i])

            # print x_distal, y_distal
            # x_distal and y_distal are the starting points for each segment
            # these are updated at the end of the loop
            h.pt3dadd(0, y_distal, 0, self.dend_diam[i], sec=self.list_dend[i])

            # update x_distal and y_distal after setting them
            # x_distal += dend_dx[i]
            y_distal += self.dend_L[i]

            # print x_distal, y_distal
            # add next point
            h.pt3dadd(0, y_distal, 0, self.dend_diam[i], sec=self.list_dend[i])

        # now deal with dend 4
        # dend 4 will ALWAYS be positioned at the end of dend[0]
        h.pt3dclear(sec=self.list_dend[4])

        # activate this section
        self.list_dend[0].push()
        x_start = h.x3d(1)
        y_start = h.y3d(1)
        h.pop_section()

        h.pt3dadd(x_start, y_start, 0, self.dend_diam[4], sec=self.list_dend[4])
        # self.dend_L[4] is subtracted because lengths always positive, 
        # and this goes to negative x
        h.pt3dadd(x_start-self.dend_L[4], y_start, 0, self.dend_diam[4], sec=self.list_dend[4])
        # print h.n3d(sec=self.list_dend[0])

        # now deal with proximal dends
        for i in range(5, 8):
            h.pt3dclear(sec=self.list_dend[i])

        # deal with dend 5, ugly. sorry.
        h.pt3dadd(x_prox, y_prox, 0, self.dend_diam[i], sec=self.list_dend[5])
        # x_prox += dend_dx[5]
        y_prox += -self.dend_L[5]

        h.pt3dadd(x_prox, y_prox, 0, self.dend_diam[5],sec=self.list_dend[5])

        # x_prox, y_prox are now the starting points for BOTH of the last 2 sections
        # dend 6
        h.pt3dadd(0, y_prox, 0, self.dend_diam[6], sec=self.list_dend[6])
        h.pt3dadd(-self.dend_L[6]*sqrt(2)/2, y_prox-self.dend_L[6]*sqrt(2)/2, 0, self.dend_diam[6], sec=self.list_dend[6])

        # dend 7
        h.pt3dadd(0, y_prox, 0, self.dend_diam[7], sec=self.list_dend[7])
        h.pt3dadd(self.dend_L[7]*sqrt(2)/2, y_prox-self.dend_L[7]*sqrt(2)/2, 0, self.dend_diam[7], sec=self.list_dend[7])

        # print "before L: ", self.list_dend[i].L
        # self.list_dend[i].L = 150
        # print "after L: ", self.list_dend[i].L

        # print type(h.x3d(1.0))
        # h.pop_section()
        # h.pt3dadd(x_distal, y_distal)

        # h.pt3dclear(sec=self.list_dend[0])
        # h.pt3dadd(0, 23, 0, 1, sec=self.list_dend[0])
        # h.pt3dadd(0, 83, 0, 1, sec=self.list_dend[0])
