# class_basket_multi.py - establish TEMP class def for multi-compartmental basket cell
#
# v 0.3.1
# rev 2012-08-13 (SL: created)
# last rev:

from neuron import h as nrn
from class_cell import Basket

# Units for e: mV
# Units for gbar: S/cm^2 unless otherwise noted
class BasketMulti():
    def __init__(self):
        self.set_biophys_soma()
        self.create_sections()
        self.connect_sections()

    def set_biophys_soma(self):
        print "set soma biophysics"

    def create_sections(self):
        print "create sections"
        
    def connect_sections(self):
        print "connect sections"

if __name__ == '__main__':
    # creates object myBasketMulti of class BasketMulti()
    myBasketMulti = BasketMulti()
