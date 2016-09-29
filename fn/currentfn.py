# currentfn.py - current-based analysis functions
#
# v 1.8.22
# rev 2013-11-19 (SL: added simple convert function)
# last major: (SL: added layers for plot to axis command)

import numpy as np

class SynapticCurrent():
    def __init__(self, fcurrent):
        self.__parse_f(fcurrent)

    # parses the input file
    def __parse_f(self, fcurrent):
        x = np.loadtxt(open(fcurrent, 'r'))
        self.t = x[:, 0]
        self.I_soma = {}
        # this really should be a dictionary - now it is!
        self.I_soma['L2_Pyr'] = x[:, 1]
        self.I_soma['L5_Pyr'] = x[:, 2]
        self.units = 'nA'
  

    def truncate_ext(self, t0, T): 
    # only do this if the limits make sense
        if (t0 >= self.t[0]) & (T <= self.t[-1]):
            I_truncated = dict.fromkeys(self.I_soma)
     # do this for each dpl
        for key in self.I_soma.keys(): 
            I_truncated[key] = self.I_soma[key][(self.t >= t0) & (self.t <= T)]
            t_truncated = self.t[(self.t >= t0) & (self.t <= T)]
        return t_truncated, I_truncated

    #  f to convert to uA
    def convert_nA_to_uA(self):
        self.I_soma['L2_Pyr'] *= 1e-3
        self.I_soma['L5_Pyr'] *= 1e-3
        self.units = 'uA'

    # external plot function
    def plot_to_axis(self, a, layer=None):
        # layer=None is redundant with L5Pyr, but it might be temporary
        if layer is None:
            a.plot(self.t, -self.I_soma['L5_Pyr'])

        elif layer is 'L2':
            a.plot(self.t, -self.I_soma['L2_Pyr'])

        elif layer is 'L5':
            a.plot(self.t, -self.I_soma['L5_Pyr'])

        # set the xlim
        a.set_xlim((50., self.t[-1]))

# external function to use SynapticCurrent() and plot to axis a
def pcurrent(a, fcurrent):
    I_syn = SynapticCurrent(fcurrent)
    I_syn.plot_to_axis(a)
