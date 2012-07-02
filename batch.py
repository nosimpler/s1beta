# from Batch.hoc
# this seems to be an init file

from neuron import h
h.xopen("nrnoc.hoc")
h.xopen("init.hoc")

# orig were X_DIM and Y_DIM
dim_x = 10
dim_y = 10

# orig didn't have _
T_factor = 2e-4
T_tau    = 0.0
H_factor = 1e-6
H_tau    = 3e-3

FSx = 4
FSy = 4

# These are load files for hoc
h(load_file("sj10-cortex.hoc"))
h(load_file("wiring_proc_2Dv2.hoc"))
h(load_file("wiring-SmlFeed-3_7.hoc"))
h(load_file("MuBurst_10.hoc"))
h(load_file("E-FFFBx_fixed_10.hoc"))
