#!/bin/bash

mpiexec -n 1 /opt/local/bin/python ./s1run.py ./param/jones_law.param
/opt/local/bin/python ./fn/plotfn_beta_event.py
