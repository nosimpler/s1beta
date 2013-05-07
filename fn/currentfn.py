# currentfn.py - current-based analysis functions
#
# v 1.7.52
# rev 2013-05-07 (SL: added L2Pyr somatic current)
# last major: (SL: created)

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
    def plot_to_axis(self, a):
        a.plot(self.t, self.I_soma_L5Pyr)

        # set the xlim
        a.set_xlim((50., self.t[-1]))

# external function to use SynapticCurrent() and plot to axis a
def pcurrent(a, fcurrent):
    I_syn = SynapticCurrent(fcurrent)
    I_syn.plot_to_axis(a)
