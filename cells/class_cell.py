# class_cell.py - establish class def for general cell features
#
# v 0.4.6
# rev 2012-08-24 (SL: Fixed dipole based on y3d)
# last rev: (MS: Functions only used in class_cell.py made private)

import numpy as np
import itertools as it
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

    # two things need to happen here for nrn:
    # 1. dipole needs to be inserted into each section
    # 2. a list needs to be created with a Dipole (Point Process) in each section at position 1
    # In Cell() and not Pyr() for future possibilities
    def dipole_insert(self):
        # insert dipole into each section of this cell
        # dends must have already been created!!
        # it's easier to use wholetree here, this includes soma
        seclist = nrn.SectionList()
        seclist.wholetree(self.soma)

        # create a python section list list_all
        self.list_all = [sec for sec in seclist]

        for sect in self.list_all:
            sect.insert('dipole')

        # Dipole is defined in dipole_pp.mod
        self.dipole_pp = [nrn.Dipole(1, sec=sect) for sect in self.list_all]

        # setting pointers and ztan values
        for sect, dpp in it.izip(self.list_all, self.dipole_pp):
            # assign internal resistance values to dipole point process (dpp)
            dpp.ri = nrn.ri(1, sec=sect)

            # not sure of the python syntax for setpointer
            nrn.setpointer(sect(0.99)._ref_v, 'pv', dpp)

            # gives INTERNAL segments of the section, non-endpoints
            # creating this because need multiple values simultaneously
            loc = np.array([seg.x for seg in sect])

            # these are the positions, including 0 but not L
            pos = np.insert(loc, 0, 0)

            # diff in yvals, scaled against the pos np.array. y_long as in longitudinal
            y_long = (nrn.y3d(1, sec=sect) - nrn.y3d(0, sec=sect)) * pos

            # diff values calculate length between successive section points
            y_diff = np.diff(y_long)

            # doing range to index multiple values of the same np.array simultaneously
            for i in range(len(loc)):
                # assign the ri value to the dipole
                sect(loc[i]).dipole.ri = nrn.ri(loc[i], sec=sect)

                # range variable 'dipole'
                if i:
                    nrn.setpointer(sect(loc[i-1])._ref_v, 'pv', sect(loc[i]).dipole)

                else:
                    nrn.setpointer(sect(0)._ref_v, 'pv', sect(loc[i]).dipole)

                nrn.setpointer(dpp._ref_Qsum, 'Qsum', sect(loc[i]).dipole)

                # add ztan values
                sect(loc[i]).dipole.ztan = y_diff[i]

            # set the pp dipole's ztan value to the last value from y_diff
            dpp.ztan = y_diff[-1]

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
    # inputs: NetCon() object 'nc', amplitude 'A', distance 'd', space const 'lamtha'
    def syn_weight(self, nc, A, d, lamtha):
        nc.weight[0] = A * np.exp(-(d**2) / (lamtha**2))

    # calculate synaptic delay
    # inputs: NetCon() object 'nc', amplitude 'A', distance 'd', space const 'lamtha'
    def syn_delay(self, nc, A, d, lamtha):
        nc.delay = A / (np.exp(-(d**2) / (lamtha**2)))

    # Define 3D shape of soma -- is needed for gui representation of cell
    # DO NOT need to call nrn.define_shape() explicitly!!
    def shape_soma(self):
        nrn.pt3dclear(sec=self.soma)

        # nrn.ptdadd(x, y, z, diam) -- if this function is run, clobbers 
        # self.soma.diam set above
        nrn.pt3dadd(0, 0, 0, self.diam, sec=self.soma)
        nrn.pt3dadd(0, self.L, 0, self.diam, sec=self.soma)

# Inhibitory cell class
class Basket(Cell):
    def __init__(self, pos, cell_name='Basket'):
        # Cell.__init__(self, L, diam, Cm, {name_prefix})
        # self.soma_props = {'name_prefix': 'basket', 'L': 39, 'diam': 20, 'cm': 0.85}
        Cell.__init__(self, pos, 39, 20, 0.85, cell_name)

        # store cell name for later
        self.name = cell_name

        # set 3D shape - unused for now but a prototype
        # self.__shape_change()        

        # Creating synapses onto this cell
        self.soma_ampa = self.syn_ampa_create(self.soma(0.5))
        self.soma_gabaa = self.syn_gabaa_create(self.soma(0.5))

    # Define 3D shape and position of cell. By default neuron uses xy plane for
    # height and xz plane for depth. This is opposite for model as a whole, but
    # convention is followed in this function ease use of gui. 
    def __shape_change(self):
        self.shape_soma()
        
        self.soma.push()
        for i in range(0, int(nrn.n3d())):
            nrn.pt3dchange(i, self.pos[0]*100 + nrn.x3d(i), -self.pos[2] + nrn.y3d(i), 
                           self.pos[1] * 100 + nrn.z3d(i), nrn.diam3d(i))

        nrn.pop_section()

# General Pyramidal cell class
class Pyr(Cell):
    def __init__(self, pos, L, diam, cm, cell_name='Pyr'):
        Cell.__init__(self, pos, L, diam, cm, cell_name)

        # store cell_name as self variable for later use
        self.name = cell_name
        
        # preallocate list to store dends
        self.list_dend = []

        # creates synapses using inherited method from Cell()
        # synapse on THIS cell needs to be RECEIVING from Inh
        # segment on the soma specified here
        self.soma_gabaa = self.syn_gabaa_create(self.soma(0.5))
        self.soma_gabab = self.syn_gabab_create(self.soma(0.5))

    # return a single cell's dipole calc
    def dipole_calc(self):
        # internal variable here for the dipole
        dp = 0

        for sect in self.list_all:
            dp += sect.Qsum_dipole

        return dp

    # Creates dendritic sections
    def create_dends(self, dend_props, cm):
        # create dends and set dend props
        for sec_name, L, diam in dend_props:
            self.list_dend.append(nrn.Section(name=self.name+'_'+sec_name))
            self.list_dend[-1].L = L
            self.list_dend[-1].diam = diam
            self.list_dend[-1].Ra = 200
            self.list_dend[-1].cm = cm

            # set nseg for each dend
            if L > 100:
                self.list_dend[-1].nseg = int(L / 50)
                
                # make dend.nseg odd for all sections
                # if dend.nseg % 2 == 0:
                #     dend.nseg += 1

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
