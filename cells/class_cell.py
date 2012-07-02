from neuron import h

# create a cell class
class Cell():
    def __init__(self, diam_soma, L_soma):
        self.soma = h.Section()
        self.soma.insert('hh')
        self.soma.diam = diam_soma
        self.soma.L = L_soma
        # self.soma.diam = 10
        # self.soma.L = 10

    def connect_to_target(self, synapse):
        # event generated, to where delivered
        nc = h.NetCon(self.soma(0.5)._ref_v, synapse, sec = self.soma)
        nc.threshold = -10
        return nc

    def shape_soma(self):
        self.soma.push()
        h.pt3dclear()
        h.pt3dadd(0, 0, 0, 1)
        h.pt3dadd(0, 23, 0, 1)
        h.pop_section()
        # self.soma.pop()
