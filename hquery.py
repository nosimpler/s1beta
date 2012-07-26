# Eventual function to query properties
from neuron import h

# assumes that something is in h already.
lsec = [sec for sec in h.allsec()]
Nsec = length(  
lseg = [seg for seg in lsec]

# recording states from synapses
g_ampa = nrn.Vector()
g_ampa.record(net.cells_L5Basket[0].soma_ampa._ref_g)

test_file = nrn.File()
test_file.wopen("ampa.dat")
