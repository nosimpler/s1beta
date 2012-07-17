# class_cell.py - establish class def for general cell features
#
# v 0.2.1
# rev 2012-07-17 (SL: general synapse prototypes)
# last rev: (added Ra and cm as parameters passed to and set by class Cell())

from neuron import h

# create a cell class
class Cell():
    def __init__(self, L_soma, diam_soma, cm):
        # make L_soma and diam_soma elements of self
        self.L = L_soma
        self.diam = diam_soma

        # create soma and set geometry
        self.soma = h.Section()
        self.soma.insert('hh')
        self.soma.L = self.L
        self.soma.diam = self.diam
        self.soma.Ra = 200
        self.soma.cm = cm

    # creates a receiving inhibitory synapse ONTO secloc
    def syn_gabaa_create(self, secloc):
        self.syn_gabaa = h.Exp2Syn(secloc)
        self.syn_gabaa.e = -80
        self.syn_gabaa.tau1 = 1
        self.syn_gabaa.tau2 = 20

    # creates a receiving excitatory synapse ONTO secloc
    def syn_ampa_create(self, secloc):
        self.syn_ampa = h.ExpSyn(secloc)
        self.syn_ampa.e = 0
        self.syn_ampa.tau = 2

    # connects instance of Cell() to a postsynaptic target
    # 'r' is range in [0, 1] for self.soma(r)
    def soma_to_target(self, r, postsyn):
    # def connect_to_target(self, secref, postsyn):
        # event generated at _ref_v, to postsyn where delivered
        # netconobj = new NetCon(source section, target section,
        # [threshold, delay, weight])
        nc = h.NetCon(self.soma(r)._ref_v, postsyn, sec=self.soma)
        # nc = h.NetCon(self.soma(0.5)._ref_v, postsyn, sec=self.soma)

        # event threshold, arbitrarily chosen for now (default is +10)
        nc.threshold = 0
        return nc

    # define 3d shape of soma -- is needed for gui representation of cell
    # DO NOT need to call h.define_shape() explicitly!!
    def shape_soma(self):
        # self.soma.push()
        h.pt3dclear(sec=self.soma)

        # h.ptdadd(x, y, z, diam) -- if this function is run, clobbers 
        # self.soma.diam set above
        h.pt3dadd(0, 0, 0, self.diam, sec=self.soma)
        h.pt3dadd(0, self.L, 0, self.diam, sec=self.soma)

        # self.soma.push()
        # print h.diam3d(0), h.diam3d(1)
        # h.pop_section()
