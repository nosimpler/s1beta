# L5_pyramidal.py - establish class def for layer 5 pyramidal cells
#
# v 0.2.5
# rev 2012-07-18 (SL: Clean up)
# last rev: (MS: Correct biophysics and mechanisms added)

from neuron import h as nrn
from class_cell import Cell
from sys import exit
from math import sqrt, exp

class L5Pyr(Cell):
    def __init__(self):
        # Cell.__init__(self, L, diam, Ra, cm)
        Cell.__init__(self, 39, 28.9, 0.85)

        # sections of these cells
        self.list_dend = []

        # prealloc namespace for dend properties
        # props be set in create_dends()
        self.dend_L = []
        self.dend_diam = []

        # create lists of connections FROM this cell TO target
        self.ncto_L5Basket = []
        self.ncto_L2Pyr = []
        self.ncto_L2Basket = []

        # N_dend is an int
        # we expect this will be overwritten!!
        # SL doesn't like this necessarily
        self.N_dend = 0

        # geometry
        self.create_dends()
        self.connect_sections()
        self.geom_set()

        # biophysics
        self.biophys_soma()
        self.biophys_dends()

        # creation of synapses inherited method from Cell()
        # synapse on THIS cell needs to be RECEIVING FROM Inh
        # segment on soma specified here
        self.syn_gabaa_create(self.soma(0.5))
        # self.synapses_create()

    # Creates dendritic sections and sets lengths and diameters for each section
    # dend lengths and dend diams are hardcoded here
    def create_dends(self):
    # def create_sections(self, N_dend):
        # hard code dend lengths and diams
        self.dend_L = [102, 680, 680, 425, 255, 85, 255, 255]
        self.dend_diam = [10.2, 7.48, 4.93, 3.4, 5.1, 6.8, 8.5, 8.5]

        # check lengths for congruity
        # this needs to be figured out
        # should probably be try/except
        if len(self.dend_L) == len(self.dend_diam):
            self.N_dend = len(self.dend_L)
        else:
            print "self.dend_L and self.dend_diam are not the same length. Please fix in L5_pyramidal.py"
            exit()

        # Trying to create sections directly
        for i in range(0, self.N_dend):
            self.list_dend.append(nrn.Section())

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
            
    # set the geometry, including the nseg.
    # geom_set separate for future and to get around shape_change
    def geom_set(self):
        # The pythonic way of setting length and diameter 
        for dend, L, diam in zip(self.list_dend, self.dend_L, self.dend_diam):
            dend.L = L
            dend.diam = diam
            dend.Ra = 200
            dend.cm = 0.85

        # set nseg for each dendritic section (soma.nseg = 1 by default)
        for dend in self.list_dend:
            if dend.L > 50:
                dend.nseg = int(dend.L / 50)

    # adding biophysics to soma
    def biophys_soma(self):
        # set hh params
        self.soma.gnabar_hh = 0.16
        self.soma.gkbar_hh = 0.01
        self.soma.gl_hh = 0.0000426
        # units for above are S/cm^2?
        self.soma.el_hh = -65 
        # by default: ena = 50, ek = -77

        # insert 'ca' mechanism
        self.soma.insert('ca')
        self.soma.gbar_ca = 60
        # units are pS/um^2?????? CHECK WITH SJ!!!

        # insert 'cad' mechanism
        # units of tau are ms
        self.soma.insert('cad')
        self.soma.taur_cad = 20

        # insert 'kca' mechanism
        # units are S/cm^2?
        self.soma.insert('kca')
        self.soma.gbar_kca = 0.0002

        # insert 'km' mechanism
        # units are pS/um^2
        self.soma.insert('km')
        self.soma.gbar_km = 200 

        # insert 'cat' mechanism
        self.soma.insert('cat')
        self.soma.gbar_cat = 2e-4
        # self.soma.gbar_cat = 0.0002
        # units S/cm^2?

        # insert 'ar' mechanism
        self.soma.insert('ar')
        self.soma.gbar_ar = 1e-6
        # self.soma.gbar_ar = 0.000001
        
    def biophys_dends(self):
        for sec in self.list_dend:
            # insert 'hh' mechanism
            sec.insert('hh')
            sec.gnabar_hh = 0.14
            sec.gkbar_hh = 0.01
            sec.gl_hh = 0.0000426

            # units: mV
            sec.el_hh = -71

            # Insert 'ca' mechanims
            # units pS/um^2
            sec.insert('ca')
            sec.gbar_ca = 60

            # Insert 'cad' mechanism
            # units ms
            sec.insert('cad')
            sec.taur_cad = 20

            # Insert 'kca' mechanism
            # units S/cm^2
            sec.insert('kca')
            sec.gbar_kca = 0.0002

            # Insert 'km' mechansim
            # units pS/cm^2
            sec.insert('km')
            sec.gbar_km = 200

            # insert 'cat' and 'ar' mechanisms
            sec.insert('cat')
            sec.gbar_cat = 0.0002
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

    # At some point, a function like this should be a property of a class and then generalized
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
