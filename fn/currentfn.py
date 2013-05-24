# currentfn.py - current-based analysis functions
#
# v 1.7.54
# rev 2013-05-24 (SL: added layers for plot to axis command)
# last major: (SL: added L2Pyr somatic current)

import numpy as np

class SynapticCurrent():
    def __init__(self, fcurrent):
        self.__parse_f(fcurrent)

    # parses the input file
    def __parse_f(self, fcurrent):
        x = np.loadtxt(open(fcurrent, 'r'))
        self.t = x[:, 0]
        self.I_soma_L2Pyr = x[:, 1]
        self.I_soma_L5Pyr = x[:, 2]

    # external plot function
    def plot_to_axis(self, a, layer=None):
        # layer=None is redundant with L5Pyr, but it might be temporary
        if layer is None:
            a.plot(self.t, -self.I_soma_L5Pyr)
        elif layer is 'L2':
            a.plot(self.t, -self.I_soma_L2Pyr)
        elif layer is 'L5':
            a.plot(self.t, -self.I_soma_L5Pyr)

        # set the xlim
        a.set_xlim((50., self.t[-1]))

# external function to use SynapticCurrent() and plot to axis a
def pcurrent(a, fcurrent):
    I_syn = SynapticCurrent(fcurrent)
    I_syn.plot_to_axis(a)
