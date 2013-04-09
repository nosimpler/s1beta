# class_cell.py - establish class def for general cell features
#
# v 1.7.40
# rev 2013-04-09 (SL: separated L2 and L5 dipoles)
# last rev: (MS: method for adding IClamps to segs)

import numpy as np
import itertools as it
from neuron import h as nrn

# Units for e: mV
# Units for gbar: S/cm^2

# Create a cell class
class Cell():
    def __init__(self, soma_props):
        # Parallel methods
        self.pc = nrn.ParallelContext()

        # make L_soma and diam_soma elements of self
        # Used in shape_change() b/c func clobbers self.soma.L, self.soma.diam 
        self.L = soma_props['L']
        self.diam = soma_props['diam']
        self.pos = soma_props['pos']

        # create soma and set geometry
        self.soma = nrn.Section(cell=self, name=soma_props['name']+'_soma')
        self.soma.L = soma_props['L']
        self.soma.diam = soma_props['diam']
        self.soma.Ra = soma_props['Ra']
        self.soma.cm = soma_props['cm']

        # par: create arbitrary lists of connections FROM other cells TO this cell instantiation
        # these lists are allowed to be empty
        self.ncfrom_L2Pyr = []
        self.ncfrom_L2Basket = []
        self.ncfrom_L5Pyr = []
        self.ncfrom_L5Basket = []
        self.ncfrom_extinput = []
        self.ncfrom_extgauss = []
        self.ncfrom_extpois = []
        self.ncfrom_ev = []

    # two things need to happen here for nrn:
    # 1. dipole needs to be inserted into each section
    # 2. a list needs to be created with a Dipole (Point Process) in each section at position 1
    # In Cell() and not Pyr() for future possibilities
    def dipole_insert(self, yscale):
        # insert dipole into each section of this cell
        # dends must have already been created!!
        # it's easier to use wholetree here, this includes soma
        seclist = nrn.SectionList()
        seclist.wholetree(sec=self.soma)

        # create a python section list list_all
        self.list_all = [sec for sec in seclist]

        for sect in self.list_all:
            sect.insert('dipole')

        # Dipole is defined in dipole_pp.mod
        self.dipole_pp = [nrn.Dipole(1, sec=sect) for sect in self.list_all]

        # setting pointers and ztan values
        for sect, dpp in it.izip(self.list_all, self.dipole_pp):
            # assign internal resistance values to dipole point process (dpp)
            dpp.ri = nrn.ri(1, sec=sect)

            # sets pointers in dipole mod file to the correct locations
            # nrn.setpointer(ref, ptr, obj)
            nrn.setpointer(sect(0.99)._ref_v, 'pv', dpp)
            if self.celltype.startswith('L2'):
                nrn.setpointer(nrn._ref_dp_total_L2, 'Qtotal', dpp)

            elif self.celltype.startswith('L5'):
                nrn.setpointer(nrn._ref_dp_total_L5, 'Qtotal', dpp)

            # gives INTERNAL segments of the section, non-endpoints
            # creating this because need multiple values simultaneously
            loc = np.array([seg.x for seg in sect])

            # these are the positions, including 0 but not L
            pos = np.array([seg.x for seg in sect.allseg()])

            # diff in yvals, scaled against the pos np.array. y_long as in longitudinal
            y_scale = (yscale[sect.name()] * sect.L) * pos
            # y_long = (nrn.y3d(1, sec=sect) - nrn.y3d(0, sec=sect)) * pos

            # diff values calculate length between successive section points
            y_diff = np.diff(y_scale)
            # y_diff = np.diff(y_long)

            # doing range to index multiple values of the same np.array simultaneously
            for i in range(len(loc)):
                # assign the ri value to the dipole
                sect(loc[i]).dipole.ri = nrn.ri(loc[i], sec=sect)

                # range variable 'dipole'
                # set pointers to previous segment's voltage, with boundary condition
                if i:
                    nrn.setpointer(sect(loc[i-1])._ref_v, 'pv', sect(loc[i]).dipole)

                else:
                    nrn.setpointer(sect(0)._ref_v, 'pv', sect(loc[i]).dipole)

                # set aggregate pointers
                nrn.setpointer(dpp._ref_Qsum, 'Qsum', sect(loc[i]).dipole)

                if self.celltype.startswith('L2'):
                    nrn.setpointer(nrn._ref_dp_total_L2, 'Qtotal', sect(loc[i]).dipole)

                elif self.celltype.startswith('L5'):
                    nrn.setpointer(nrn._ref_dp_total_L5, 'Qtotal', sect(loc[i]).dipole)

                # add ztan values
                sect(loc[i]).dipole.ztan = y_diff[i]

            # set the pp dipole's ztan value to the last value from y_diff
            dpp.ztan = y_diff[-1]

    # Add IClamp to a segment
    def insert_iclamp(self, sect_name, seg_loc, tstart, tstop, weight):
        # gather list of all sections
        seclist = nrn.SectionList()
        seclist.wholetree(sec=self.soma)

        # find specified sect in section list, insert IClamp, set props
        for sect in seclist:
            if sect_name in sect.name():
                stim = nrn.IClamp(sect(seg_loc))
                stim.delay = tstart
                stim.dur = tstop - tstart
                stim.amp = weight

        return stim

    ## For all synapses, section location 'secloc' is being explicitly supplied 
    ## for clarity, even though they are (right now) always 0.5. Might change in future
    # creates a RECEIVING inhibitory synapse at secloc
    def syn_gabaa_create(self, secloc):
        syn_gabaa = nrn.Exp2Syn(secloc)
        syn_gabaa.e = -80
        syn_gabaa.tau1 = 0.5
        syn_gabaa.tau2 = 5

        return syn_gabaa

    # creates a RECEIVING slow inhibitory synapse at secloc
    # called: self.soma_gabab = syn_gabab_create(self.soma(0.5))
    def syn_gabab_create(self, secloc):
        syn_gabab = nrn.Exp2Syn(secloc)
        syn_gabab.e = -80
        syn_gabab.tau1 = 1
        syn_gabab.tau2 = 20

        return syn_gabab

    # creates a RECEIVING excitatory synapse at secloc
    def syn_ampa_create(self, secloc):
        syn_ampa = nrn.Exp2Syn(secloc)
        syn_ampa.e = 0.
        syn_ampa.tau1 = 0.5
        syn_ampa.tau2 = 5.

        return syn_ampa

    # creates a RECEIVING nmda synapse at secloc
    # this is a pretty fast NMDA, no?
    def syn_nmda_create(self, secloc):
        syn_nmda = nrn.Exp2Syn(secloc)
        syn_nmda.e = 0.
        syn_nmda.tau1 = 1.
        syn_nmda.tau2 = 20.

        return syn_nmda

    # connect_to_target created for pc, used in Network()
    # these are SOURCES of spikes
    def connect_to_target(self, target):
        nc = nrn.NetCon(self.soma(0.5)._ref_v, target, sec=self.soma)
        nc.threshold = 0

        return nc

    # parallel receptor-centric connect FROM presyn TO this cell, based on GID
    def parconnect_from_src(self, gid_presyn, nc_dict, postsyn):
        # nc_dict keys are: {pos_src, A_weight, A_delay, lamtha}
        nc = self.pc.gid_connect(gid_presyn, postsyn)

        # calculate distance between cell positions with pardistance()
        d = self.__pardistance(nc_dict['pos_src'])

        # set props here
        nc.threshold = 0
        nc.weight[0] = nc_dict['A_weight'] * np.exp(-(d**2) / (nc_dict['lamtha']**2))
        nc.delay = nc_dict['A_delay'] / (np.exp(-(d**2) / (nc_dict['lamtha']**2)))

        return nc

    # pardistance function requires pre position, since it is calculated on POST cell
    def __pardistance(self, pos_pre):
        dx = abs(self.pos[0] - pos_pre[0])
        dy = abs(self.pos[1] - pos_pre[1])
        dz = abs(self.pos[2] - pos_pre[2])

        return np.sqrt(dx**2 + dy**2)

    # Define 3D shape of soma -- is needed for gui representation of cell
    # DO NOT need to call nrn.define_shape() explicitly!!
    def shape_soma(self):
        nrn.pt3dclear(sec=self.soma)

        # nrn.ptdadd(x, y, z, diam) -- if this function is run, clobbers 
        # self.soma.diam set above
        nrn.pt3dadd(0, 0, 0, self.diam, sec=self.soma)
        nrn.pt3dadd(0, self.L, 0, self.diam, sec=self.soma)

# Inhibitory cell class
class BasketSingle(Cell):
    def __init__(self, pos, cell_name='Basket'):
        self.props = self.__set_props(cell_name, pos)

        # Cell.__init__(self, properties)
        Cell.__init__(self, self.props)
        # Cell.__init__(self, pos, 39, 20, 0.85, cell_name)

        # store cell name for later
        self.name = cell_name

        # set 3D shape - unused for now but a prototype
        # self.__shape_change()        

    def __set_props(self, cell_name, pos):
        return {
            'pos': pos,
            'L': 39.,
            'diam': 20.,
            'cm': 0.85,
            'Ra': 200.,
            'name': cell_name,
        }

    # Define 3D shape and position of cell. By default neuron uses xy plane for
    # height and xz plane for depth. This is opposite for model as a whole, but
    # convention is followed in this function ease use of gui. 
    def __shape_change(self):
        self.shape_soma()
        
        self.soma.push()
        for i in range(0, int(nrn.n3d())):
            nrn.pt3dchange(i, self.pos[0]*100 + nrn.x3d(i), -self.pos[2] + nrn.y3d(i), 
                self.pos[1] * 100 + nrn.z3d(i), nrn.diam3d(i))

        nrn.pop_section()

# General Pyramidal cell class
class Pyr(Cell):
    def __init__(self, soma_props):
    # def __init__(self, pos, L, diam, cm, cell_name='Pyr'):
        Cell.__init__(self, soma_props)

        # store cell_name as self variable for later use
        self.name = soma_props['name']
        
        # preallocate list to store dends
        self.list_dend = []

    # Create dictionary of section names with entries to scale section lengths to length along z-axis
    def get_sectnames(self):
        seclist = nrn.SectionList()
        seclist.wholetree(sec=self.soma)
     
        d = dict((sect.name(), 1.) for sect in seclist)

        for key in d.keys():
            # basal_2 and basal_3 at 45 degree angle to z-axis.
            if 'basal_2' in key:
                d[key] = np.sqrt(2) / 2 
 
            elif 'basal_3' in key:
                d[key] = np.sqrt(2) / 2 

            # apical_oblique at 90 perpendicular to z-axis
            elif 'apical_oblique' in key:
                d[key] = 0.

            # All basalar dendrites extend along negative z-axis
            if 'basal' in key:
                d[key] = -d[key]

        return d

    # Creates dendritic sections
    def create_dends(self, list_names, dend_props, soma_props):
        # create dends and set dend props
        for sect_name in list_names:
            self.list_dend.append(nrn.Section(name=self.name+'_'+sect_name))
            self.list_dend[-1].L = dend_props[sect_name]['L']
            self.list_dend[-1].diam = dend_props[sect_name]['diam']

            # same values for soma
            self.list_dend[-1].Ra = soma_props['Ra']
            self.list_dend[-1].cm = soma_props['cm']

            # set nseg for each dend
            if dend_props[sect_name]['L'] > 100:
                self.list_dend[-1].nseg = int(dend_props[sect_name]['L'] / 50)

                # make dend.nseg odd for all sections
                if not self.list_dend[-1].nseg % 2:
                    self.list_dend[-1].nseg += 1
