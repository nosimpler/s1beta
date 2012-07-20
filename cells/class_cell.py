# class_cell.py - establish class def for general cell features
#
# v 0.2.3
# rev 2012-07-17 (MS: Added Basket and Pry classes)
# last rev: (SL: using nrn instead of h)

from neuron import h as nrn
# from neuron import h

# create a cell class
class Cell():
    def __init__(self, L_soma, diam_soma, cm, cell_name='cell_'):
        # make L_soma and diam_soma elements of self
        self.L = L_soma
        self.diam = diam_soma

        # create soma and set geometry
        self.soma = nrn.Section(name = cell_name + 'soma')
        self.soma.insert('hh')
        self.soma.L = self.L
        self.soma.diam = self.diam
        self.soma.Ra = 200
        self.soma.cm = cm

    # creates a receiving inhibitory synapse ONTO secloc
    def syn_gabaa_create(self, secloc):
        self.syn_gabaa = nrn.Exp2Syn(secloc)
        self.syn_gabaa.e = -80
        self.syn_gabaa.tau1 = 1
        self.syn_gabaa.tau2 = 20

    # creates a receiving excitatory synapse ONTO secloc
    def syn_ampa_create(self, secloc):
        self.syn_ampa = nrn.ExpSyn(secloc)
        self.syn_ampa.e = 0
        self.syn_ampa.tau = 2

    # connects instance of Cell() to a postsynaptic target
    # 'r' is range in [0, 1] for self.soma(r)
    def soma_to_target(self, r, postsyn):
    # def connect_to_target(self, secref, postsyn):
        # event generated at _ref_v, to postsyn where delivered
        # netconobj = new NetCon(source section, target section,
        # [threshold, delay, weight])
        nc = nrn.NetCon(self.soma(r)._ref_v, postsyn, sec=self.soma)
        # nc = nrn.NetCon(self.soma(0.5)._ref_v, postsyn, sec=self.soma)

        # event threshold, arbitrarily chosen for now (default is +10)
        nc.threshold = 0
        return nc

    # define 3d shape of soma -- is needed for gui representation of cell
    # DO NOT need to call nrn.define_shape() explicitly!!
    def shape_soma(self):
        # self.soma.push()
        nrn.pt3dclear(sec=self.soma)

        # nrn.ptdadd(x, y, z, diam) -- if this function is run, clobbers 
        # self.soma.diam set above
        nrn.pt3dadd(0, 0, 0, self.diam, sec=self.soma)
        nrn.pt3dadd(0, self.L, 0, self.diam, sec=self.soma)

        # self.soma.push()
        # print nrn.diam3d(0), nrn.diam3d(1)
        # nrn.pop_section()

# Inhibitory cell class
class Basket(Cell):
    def __init__(self):
        # Cell.__init__(self, L, diam, cm)
        Cell.__init__(self, 39, 20, 0.85, 'basket_')

        # excitatory synapse onto this cell
        self.syn_ampa_create(self.soma(0.5))
        # # or something in the future like syn_ampa, etc.
        # self.syn_L5pyr = h.ExpSyn(self.soma(0.5))
        # self.syn_L5pyr.e = 0

        # create lists of connections FROM this cell TO target
        # not all of these will be used necessarily in each cell
        self.ncto_L5Pyr = []
        self.ncto_L2Pyr = []

        # No autapses, right?
        # self.ncto_L5Basket = []
        # self.ncto_L2Basket = []

        # # tau is decay
        # self.syn_L5pyr.tau = 2

# General Pyramidal cell class
class Pyr(Cell):
    def __init__(self, L, diam, cm, cell_name='Pyr'):
        Cell.__init__(self, L, diam, cm, cell_name)

        # store cell_name as self variable for later use
        self.name = cell_name
        
        # preallocate list to store dends
        self.list_dend = []

        # creation of synapses inherited method from Cell()
        # synapse on THIS cell needs to be RECEIVING from Inh
        # segment on the soma specified here
        self.syn_gabaa_create(self.soma(0.5))

    # Creates dendritic sections
    def create_dends(self, dend_L, dend_diam, dend_names,):
        # N_dends: number of dends to be create
        # dend_names: list of strings used as names for sections

        # check lengths for congruity
        # this needs to be figured out
        # should probably be try/except
        if len(self.dend_L) == len(self.dend_diam):
            self.N_dend = len(self.dend_L)
            self.dend_L = dend_L
            self.dend_diam = dend_diam
        else:
            print "self.dend_L and self.dend_diam are not the same length."
            print "Please fix in L5_pyramidal.py"
            exit()

        for i in range(0, self.N_dend):
            self.list_dend.append(nrn.Section(name=self.name+dend_names[i]))

    # set geometry, including nseg
    def geom_set(self, cm):
        # cm: membrane capacitance
        for dend, L, diam in zip(self.list_dend, self.dend_L, self.dend_diam):
            dend.L = L
            dend.diam = diam
            dend.Ra = 200
            dend.cm = cm

        # set nseg for each dendritic section (soma.nseg = 1 by default)
        for dend in self.list_dend:
            if dend.L>100:
                dend.nseg = int(dend.L/50)

            # make dend.nseg odd for all sections
            # if dend.nseg % 2 == 0:
            #     dend.nseg = dend.nseg + 1

    # set biophysics for soma
    def Pyrbiophys_soma(self):
        # set some 'hh' mechanism values
        self.soma.gkbar_hh = 0.01
        self.soma.gl_hh = 4.26e-5
        self.soma.el_hh = -65
        
        # insert 'km' mechanism
        self.soma.insert('km')

    # set biophysics for dendritic sections
    def Pyrbiophys_dends(self):
         for sec in self.list_dend:
            # insert 'hh' mechanism
            sec.insert('hh')
            sec.gkbar_hh = 0.01
            sec.gl_hh = 4.26e-5

            # insert 'km' mechanism
            sec.insert('km')
