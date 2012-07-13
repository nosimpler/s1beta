# class_cell.py - est calss def for a single compartment cell
#
# v 0.2.0
# rev 2012-07-12 (added Ra and cm as parameters passed to and set by class Cell())
# last rev: (created)
#

from neuron import h

# create a cell class
class Cell():
    def __init__(self, L_soma, diam_soma, cm):
        # make L_soma and diam_soma elements of self
        self.L = L_soma
        self.diam = diam_soma

        # create section and set geomtry
        self.soma = h.Section()
        self.soma.insert('hh')
        # self.shape_soma()
        self.soma.L = self.L
        self.soma.diam = self.diam
        self.soma.Ra = 200
        self.soma.cm = cm

    # this connects an instance of Cell() to a postsynaptic target
    def connect_to_target(self, postsyn):
        # event generated at _ref_v, to postsyn where delivered
        # netconobj = new NetCon(source section, target section,
        # [threshold, delay, weight])
        nc = h.NetCon(self.soma(0.5)._ref_v, postsyn, sec=self.soma)

        # event threshold, arbitrarily chosen for now (default is +10)
        nc.threshold = -10
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
