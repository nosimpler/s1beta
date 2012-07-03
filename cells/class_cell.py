from neuron import h

# create a cell class
class Cell():
    def __init__(self, diam_soma, L_soma):
        self.soma = h.Section()
        self.soma.insert('hh')
        self.soma.diam = diam_soma
        # self.soma.L = L_soma
        self.shape_soma(L_soma)

    # this connects an instance of Cell() to a postsynaptic target
    def connect_to_target(self, postsyn):
        # event generated at _ref_v, to postsyn where delivered
        nc = h.NetCon(self.soma(0.5)._ref_v, postsyn, sec=self.soma)

        # event threshold, arbitrarily chosen for now
        nc.threshold = -10
        return nc

    # define shape of soma
    # need to find out whether or not we need to call h.define_shape() explicitly!!
    def shape_soma(self, L_soma):
        # self.soma.push()
        h.pt3dclear(sec=self.soma)
        h.pt3dadd(0, 0, 0, 1, sec=self.soma)
        h.pt3dadd(0, L_soma, 0, 1, sec=self.soma)
        # h.pop_section()
