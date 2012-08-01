# class_cell.py - establish class def for general cell features
#
# v 0.2.18
# rev 2012-08-01 (SL: added distance, weight, delay to Cell())
# last rev: (SL: passing pos to Cell())

import numpy as np
from neuron import h as nrn

# Units for e: mV
# Units for gbar: S/cm^2

# Create a cell class
class Cell():
    def __init__(self, pos, L_soma, diam_soma, cm, cell_name='cell'):
    # def __init__(self, L_soma, diam_soma, cm, cell_name='cell'):
        # make L_soma and diam_soma elements of self
        # Used in shape_change() b/c func clobbers self.soma.L, self.soma.diam 
        self.L = L_soma
        self.diam = diam_soma
        self.pos = pos

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

        # event threshold, arbitrarily chosen for now (default is +10)
        nc.threshold = 0

        # returns nc object
        return nc

    # general distance function calculates from pos of post_cell
    def distance(self, post_cell):
        # print "positions:", self.pos, post_cell.pos
        dx = abs(self.pos[0] - post_cell.pos[0])
        dy = abs(self.pos[1] - post_cell.pos[1])
        dz = abs(self.pos[2] - post_cell.pos[2])

        return np.sqrt(dx**2 + dy**2)

    # calculate synaptic weight
    # inputs: NetCon() object 'nc', amplitude 'A', distance 'd', time const 'tau'
    def syn_weight(self, nc, A, d, tau):
        nc.weight[0] = A * np.exp(-(d**2) / (tau**2))
        # print "in syn_weight:", nc, nc.weight[0]

    # calculate synaptic delay
    # inputs: NetCon() object 'nc', amplitude 'A', distance 'd', time const 'tau'
    def syn_delay(self, nc, A, d, tau):
        nc.delay = A / (np.exp(-(d**2) / (tau**2)))
        # print "in syn_delay:", nc, nc.delay

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
    def __init__(self, pos):
        # Cell.__init__(self, L, diam, Cm, {name_prefix})
        # self.soma_props = {'name_prefix': 'basket_', 'L': 39, 'diam': 20, 'cm': 0.85}
        Cell.__init__(self, pos, 39, 20, 0.85, 'basket_')

        # Creating synapses onto this cell
        self.soma_ampa = self.syn_ampa_create(self.soma(0.5))
        self.soma_gabaa = self.syn_gabaa_create(self.soma(0.5))

        # Create lists of connections FROM this cell TO target
        # not all of these will be used necessarily in each cell
        self.ncto_L5Pyr_gabaa = []
        self.ncto_L5Pyr_gabab = []
        self.ncto_L2Pyr = []
        # self.ncto_L5Basket = []
        # self.ncto_L2Basket = []

    # connects both the GABAa and GABAb synapses
    def connect_to_L5Pyr(self, L5Pyr):
        self.ncto_L5Pyr_gabaa.append(self.sec_to_target(self.soma, 0.5, L5Pyr.soma_gabaa))
        self.ncto_L5Pyr_gabab.append(self.sec_to_target(self.soma, 0.5, L5Pyr.soma_gabab))

        # get distance and calculate weight
        d = self.distance(L5Pyr)
        tau = 70.

        # set the weights
        self.syn_weight(self.ncto_L5Pyr_gabaa[-1], 0.025, d, tau)
        self.syn_weight(self.ncto_L5Pyr_gabab[-1], 0.025, d, tau)
        # self.ncto_L5Pyr_gabab[-1].weight[0] = 0.025 * exp(-(d**2) / (70**2))

        # delay in ms
        self.syn_delay(self.ncto_L5Pyr_gabaa[-1], 1, d, tau)
        self.syn_delay(self.ncto_L5Pyr_gabab[-1], 1, d, tau)
        # self.ncto_L5Pyr_gabaa[-1].delay = 1
        # self.ncto_L5Pyr_gabab[-1].delay = 1

# General Pyramidal cell class
class Pyr(Cell):
    def __init__(self, pos, L, diam, cm, cell_name='Pyr'):
        Cell.__init__(self, pos, L, diam, cm, cell_name)

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
    # def create_dends(self, dend_L, dend_diam, dend_names)
    def create_dends(self, dend_props, cm):
        # create dends and set dend props
        for sec_name, L, diam in dend_props:
            self.list_dend.append(nrn.Section(name=self.name+sec_name))
            self.list_dend[-1].L = L
            self.list_dend[-1].diam = diam
            self.list_dend[-1].Ra = 200
            self.list_dend[-1].cm = cm

            # set nseg for each dend
            if L > 100:
                self.list_dend[-1].nseg = int(L / 50)
                
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
    
    # set geometry, including nseg
    # def geom_set(self, cm):
    #     # cm: membrane capacitance
    #     for dend, L, diam in zip(self.list_dend, self.dend_L, self.dend_diam):
    #         dend.L = L
    #         dend.diam = diam
    #         dend.Ra = 200
    #         dend.cm = cm
