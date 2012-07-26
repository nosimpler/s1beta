# class_cell.py - establish class def for general cell features
#
# v 0.2.14
# rev 2012-07-26 (SL: new synapses created)
# last rev: (MS: added units)

from neuron import h as nrn

# Units for e: mV
# Units for gbar: S/cm^2

# create a cell class
class Cell():
    def __init__(self, L_soma, diam_soma, cm, cell_name='cell'):
        # make L_soma and diam_soma elements of self
        # Used in shape_change() b/c func clobbers self.soma.L, self.soma.diam 
        self.L = L_soma
        self.diam = diam_soma

        # create soma and set geometry
        self.soma = nrn.Section(name = cell_name + '_soma')
        self.soma.insert('hh')
        self.soma.L = L_soma
        self.soma.diam = diam_soma
        self.soma.Ra = 200
        self.soma.cm = cm

    ## For all synapses, section location 'secloc' is being explicitly supplied 
    ## for clarity, even though they are (right now) always 0.5. Might change in future
    # creates a RECEIVING inhibitory synapse at secloc
    def syn_gabaa_create(self, secloc):
        syn_gabaa = nrn.Exp2Syn(secloc)
        syn_gabaa.e = -80
        syn_gabaa.tau1 = 0.5
        syn_gabaa.tau2 = 5

        return syn_gabaa

    # creates a RECEIVING slow inhibitory synapse at secloc
    # called: self.soma_gabab = syn_gabab_create(self.soma(0.5))
    def syn_gabab_create(self, secloc):
        syn_gabab = nrn.Exp2Syn(secloc)
        syn_gabab.e = -80
        syn_gabab.tau1 = 1
        syn_gabab.tau2 = 20

        return syn_gabab

    # creates a RECEIVING excitatory synapse at secloc
    def syn_ampa_create(self, secloc):
        syn_ampa = nrn.Exp2Syn(secloc)
        syn_ampa.e = 0
        syn_ampa.tau1 = 0.5
        syn_ampa.tau2 = 5

        return syn_ampa

    # creates a RECEIVING nmda synapse at secloc
    # this is a pretty fast NMDA, no?
    def syn_nmda_create(self, secloc):
        syn_nmda = nrn.Exp2Syn(secloc)
        syn_nmda.tau1 = 1
        syn_nmda.tau2 = 20

        return syn_nmda

    # connects instance of Cell() to a postsynaptic target
    # 'r_soma' is range in [0, 1] for self.soma(r_soma)
    # extremely general function to hide nrn.netCon
    def sec_to_target(self, sec_presyn, r_sec, postsyn):
        # event generated at _ref_v, to postsyn where delivered
        # netconobj = new NetCon(source section, target section,
        # [threshold, delay, weight])
        nc = nrn.NetCon(sec_presyn(r_sec)._ref_v, postsyn, sec=sec_presyn)
        # nc = nrn.NetCon(self.soma(r_soma)._ref_v, postsyn, sec=self.soma)

        # event threshold, arbitrarily chosen for now (default is +10)
        nc.threshold = 0

        # returns nc object
        return nc

    # Define 3D shape of soma -- is needed for gui representation of cell
    # DO NOT need to call nrn.define_shape() explicitly!!
    def shape_soma(self):
        # self.soma.push()
        nrn.pt3dclear(sec=self.soma)

        # nrn.ptdadd(x, y, z, diam) -- if this function is run, clobbers 
        # self.soma.diam set above
        nrn.pt3dadd(0, 0, 0, self.diam, sec=self.soma)
        nrn.pt3dadd(0, self.L, 0, self.diam, sec=self.soma)

# Inhibitory cell class
class Basket(Cell):
    def __init__(self):
        # Cell.__init__(self, L, diam, Cm, {name_prefix})
        Cell.__init__(self, 39, 20, 0.85, 'basket_')

        # Creating synapses onto this cell
        self.soma_ampa = self.syn_ampa_create(self.soma(0.5))
        self.soma_gabaa = self.syn_gabaa_create(self.soma(0.5))

        # Create lists of connections FROM this cell TO target
        # not all of these will be used necessarily in each cell
        # self.ncto_L5Pyr = []
        self.ncto_L5Pyr_gabaa = []
        self.ncto_L5Pyr_gabab = []
        self.ncto_L2Pyr = []

        # No autapses, right?
        # self.ncto_L5Basket = []
        # self.ncto_L2Basket = []

    # connects both the GABAa and GABAb synapses
    def connect_to_L5Pyr(self, L5Pyr):
        self.ncto_L5Pyr_gabaa.append(self.sec_to_target(self.soma, 0.5, L5Pyr.soma_gabaa))
        self.ncto_L5Pyr_gabab.append(self.sec_to_target(self.soma, 0.5, L5Pyr.soma_gabab))

        self.ncto_L5Pyr_gabaa[-1].weight[0] = 0.01
        self.ncto_L5Pyr_gabab[-1].weight[0] = 0.01

        # delay in ms
        self.ncto_L5Pyr_gabaa[-1].delay = 1
        self.ncto_L5Pyr_gabab[-1].delay = 1

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
        self.soma_gabaa = self.syn_gabaa_create(self.soma(0.5))
        self.soma_gabab = self.syn_gabab_create(self.soma(0.5))

    # Creates dendritic sections
    def create_dends(self, dend_L, dend_diam, dend_names):
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
    def pyr_biophys_soma(self):
        # set some 'hh' mechanism values
        self.soma.gkbar_hh = 0.01
        self.soma.gl_hh = 4.26e-5
        self.soma.el_hh = -65
        
        # insert 'km' mechanism
        self.soma.insert('km')

    # set biophysics for dendritic sections
    def pyr_biophys_dends(self):
         for sec in self.list_dend:
            # insert 'hh' mechanism
            sec.insert('hh')
            sec.gkbar_hh = 0.01
            sec.gl_hh = 4.26e-5

            # insert 'km' mechanism
            sec.insert('km')
