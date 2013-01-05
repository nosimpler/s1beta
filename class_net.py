# class_net.py - establishes the Network class and related methods
#
# v 1.5.12
# rev 2013-01-05 (SL: makes evprox input per cell for randomness)
# last major: (SL: cleanup)

import itertools as it
import numpy as np
import sys

from neuron import h as nrn
from fn.class_feed import ParFeedExt, ParFeedExtGauss, ParFeedExtPois, ParFeedEvoked
from fn.cells.L5_pyramidal import L5Pyr
from fn.cells.L2_pyramidal import L2Pyr
from fn.cells.L2_basket import L2Basket
from fn.cells.L5_basket import L5Basket
import fn.paramrw as paramrw

# create Network class
class Network():
    def __init__(self, p):
        # set the params internally for this net
        # better than passing it around like ...
        self.p = p

        # int variables for grid of pyramidal cells (for now in both L2 and L5)
        self.gridpyr = {'x': self.p['N_pyr_x'], 'y': self.p['N_pyr_y']}

        # Parallel stuff
        self.pc = nrn.ParallelContext()
        self.n_hosts = int(self.pc.nhost())
        self.rank = int(self.pc.id())
        self.N_src = 0

        # zdiff is expressed as a positive DEPTH of L5 relative to L2
        # this is a deviation from the original, where L5 was defined at 0
        # this should not change interlaminar weight/delay calculations
        self.zdiff = 1307.4 

        # all params of external inputs in p_ext
        # Global number of external inputs ... automatic counting makes more sense
        self.p_ext, self.p_unique = paramrw.create_pext(self.p, nrn.tstop)
        # self.p_ext, self.p_ext_gauss, self.p_ext_pois = paramrw.create_pext(self.p, nrn.tstop)
        self.N_extinput = len(self.p_ext)

        # absolute source list of keys on which everything gets created
        # alpha order HERE matters but cannot in dicts
        self.src_list = [
            'L2_basket',
            'L2_pyramidal',
            'L5_basket',
            'L5_pyramidal',
            'extinput',
        ]

        # adds inputs to the self.src_list
        self.__append_inputs_unique()

        # cell position lists, also will give counts: must be known by ALL nodes
        # extinput positions are all located at origin. This is sort of a hack bc of redundancy
        self.pos_dict = dict.fromkeys(self.src_list)

        # create coords and counts in self.N_{celltype} variables
        self.__create_coords_pyr()
        self.__create_coords_basket()

        # also creates coords for the extgauss
        self.N_cells = self.N_L2_pyr + self.N_L5_pyr + self.N_L2_basket + self.N_L5_basket
        self.N_evprox = self.N_extgauss = self.N_extpois = self.N_cells
        # self.N_extgauss = self.N_cells
        # self.N_extpois = self.N_cells
        self.__create_coords_extinput()

        # ugly for now
        self.src_counts = (
            self.N_L2_basket,
            self.N_L2_pyr,
            self.N_L5_basket,
            self.N_L5_pyr,
            self.N_evprox,
            self.N_extinput,
            self.N_extgauss,
            self.N_extpois,
        )

        # create dictionary of GIDs according to cell type
        # global dictionary of gid and cell type
        self.__create_gid_dict()

        # assign gid to hosts, creates list of gids for this node in __gid_list
        # __gid_list length is number of cells assigned to this id()
        self.__gid_list = []
        self.__gid_assign()

        # create cells (and create self.origin in create_cells_pyr())
        self.cells_list = []
        self.evprox_list = []
        self.extinput_list = []
        self.extgauss_list = []
        self.extpois_list = []
        self.__create_all_src()
        self.__state_init()

        # parallel network connector
        self.__parnet_connect()

        # set to record spikes
        self.spiketimes = nrn.Vector()
        self.spikegids = nrn.Vector()
        self.__record_spikes()

    # appends an alpha sorted list of inputs
    def __append_inputs_unique(self):
        list_keys = self.p_unique.keys()

        # lamba sort and append to src_list
        self.src_list += sorted(list_keys, key=lambda pos: pos[0])

    # Creates cells and grid
    # pyr grid is the immutable grid, origin now calculated in relation to feed
    def __create_coords_pyr(self):
        xrange = np.arange(self.gridpyr['x'])
        yrange = np.arange(self.gridpyr['y'])

        # create list of tuples/coords, (x, y, z)
        self.pos_dict['L2_pyramidal'] = [pos for pos in it.product(xrange, yrange, [0])]
        self.pos_dict['L5_pyramidal'] = [pos for pos in it.product(xrange, yrange, [self.zdiff])]

        self.N_L2_pyr = len(self.pos_dict['L2_pyramidal'])
        self.N_L5_pyr = len(self.pos_dict['L5_pyramidal'])

    def __create_coords_basket(self):
        # define relevant x spacings for basket cells
        xzero = np.arange(0, self.gridpyr['x'], 3)
        xone = np.arange(1, self.gridpyr['x'], 3)

        # split even and odd y vals
        yeven = np.arange(0, self.gridpyr['y'], 2)
        yodd = np.arange(1, self.gridpyr['y'], 2)

        # create general list of x,y coords and sort it
        coords = [pos for pos in it.product(xzero, yeven)] + [pos for pos in it.product(xone, yodd)]
        coords_sorted = sorted(coords, key=lambda pos: pos[1])

        # append the z value for position for L2 and L5
        # print len(coords_sorted)
        self.pos_dict['L2_basket'] = [pos_xy + (0,) for pos_xy in coords_sorted]
        self.pos_dict['L5_basket'] = [pos_xy + (self.zdiff,) for pos_xy in coords_sorted]

        # number of cells
        self.N_L2_basket = len(self.pos_dict['L2_basket'])
        self.N_L5_basket = len(self.pos_dict['L5_basket'])

    # creates origin AND creates external input coords (same thing for now but won't fix because could change)
    def __create_coords_extinput(self):
        xrange = np.arange(self.gridpyr['x'])
        yrange = np.arange(self.gridpyr['y'])

        # origin's z component isn't really used in calculating distance functions from origin
        # these must be ints!
        origin_x = xrange[(len(xrange)-1)/2]
        origin_y = yrange[(len(yrange)-1)/2]
        origin_z = np.floor(self.zdiff/2)
        self.origin = (origin_x, origin_y, origin_z)

        self.pos_dict['extinput'] = [self.origin for i in range(self.N_extinput)]
        self.pos_dict['evprox'] = [self.origin for i in range(self.N_evprox)]
        self.pos_dict['extgauss'] = [self.origin for i in range(self.N_extgauss)]
        self.pos_dict['extpois'] = [self.origin for i in range(self.N_extpois)]

    # creates gid dicts and pos_lists
    def __create_gid_dict(self):
        # initialize gid index gid_ind to start at 0
        gid_ind = [0]

        # append a new gid_ind based on previous and next cell count
        for i in range(len(self.src_counts)):
            gid_ind.append(gid_ind[i]+self.src_counts[i])

        # gid order is guaranteed HERE
        # alpha order here but NOT guaranteed for dict
        self.gid_dict = {
            'L2_basket': range(gid_ind[0], gid_ind[1]),
            'L2_pyramidal': range(gid_ind[1], gid_ind[2]),
            'L5_basket': range(gid_ind[2], gid_ind[3]),
            'L5_pyramidal': range(gid_ind[3], gid_ind[4]),
            'evprox': range(gid_ind[4], gid_ind[5]),
            'extinput': range(gid_ind[5], gid_ind[6]),
            'extgauss': range(gid_ind[6], gid_ind[7]),
            'extpois': range(gid_ind[7], gid_ind[8]),
        }

        for count in self.src_counts:
            self.N_src += count

    # this happens on EACH node
    # creates self.__gid_list for THIS node
    def __gid_assign(self):
        # round robin assignment of gids
        for gid in range(self.rank, self.N_cells, self.n_hosts):
        # for gid in range(self.rank, self.N_src, self.n_hosts):
            # set the cell gid
            self.pc.set_gid2node(gid, self.rank)
            self.__gid_list.append(gid)

            # calculate gid for the evprox and assign to same rank
            gid_evprox = self.gid_dict['evprox'][0] + gid
            self.pc.set_gid2node(gid_evprox, self.rank)
            self.__gid_list.append(gid_evprox)

            # calculate gid for the extgauss and assign to same rank
            gid_extgauss = self.gid_dict['extgauss'][0] + gid
            self.pc.set_gid2node(gid_extgauss, self.rank)
            self.__gid_list.append(gid_extgauss)

            # calculate gid for the extpois and assign to same rank
            gid_extpois = self.gid_dict['extpois'][0] + gid
            self.pc.set_gid2node(gid_extpois, self.rank)
            self.__gid_list.append(gid_extpois)

        # NOT perfectly balanced for now
        for gid_base in range(self.rank, self.N_extinput, self.n_hosts):
            # shift the gid_base to the extinput gid
            gid = gid_base + self.gid_dict['extinput'][0]

            # set as usual
            self.pc.set_gid2node(gid, self.rank)
            self.__gid_list.append(gid)

        # extremely important to get the gids in the right order
        self.__gid_list.sort()

    # reverse lookup of gid to type
    # there may be a better, more general way to do this
    def gid_to_type(self, gid):
        for gidtype, gids in self.gid_dict.iteritems():
            if gid in gids:
                return gidtype

    # attempting to make a general function for all evoked params
    def __create_ev_params(self, gid_ev):
        gid_post = gid_ev - self.gid_dict['evprox'][0]
        cell_type = self.gid_to_type(gid_post)

        # return the first 2 values (values through value 2)
        return (self.p_unique['evprox']['t0'], self.p_unique['evprox'][cell_type][2])

    # creates the external feed appropriate for this gid
    # only mu and sigma really get read here, dependent upon postsynaptic cell type
    def __create_extgauss_params(self, gid_extgauss):
        # linear shift from corresponding cell gid
        gid_post = gid_extgauss - self.gid_dict['extgauss'][0]
        type = self.gid_to_type(gid_post)

        # should only return a cell type
        # return values 2 and 3 of the tuple of this cell type and assign to mu and sigma
        return self.p_unique['ext_gauss'][type][2:4]

    # returns the lamtha related to the postsynaptic cell type
    def __create_extpois_params(self, gid_extpois):
        # linear shift from corresponding cell gid
        gid_post = gid_extpois - self.gid_dict['extpois'][0]
        type = self.gid_to_type(gid_post)

        # return the lamtha related to this celltype
        return self.p_unique['ext_pois'][type][2]

    # parallel create cells AND external inputs (feeds)
    # these are spike SOURCES but cells are also targets
    # external inputs are not targets
    def __create_all_src(self):
        # loop through gids on this node
        for gid in self.__gid_list:
            # check existence of gid with Neuron
            if self.pc.gid_exists(gid):
                # get type of cell and pos via gid
                # now should be valid for ext inputs
                type = self.gid_to_type(gid)
                type_pos_ind = gid - self.gid_dict[type][0]
                pos = self.pos_dict[type][type_pos_ind]

                # figure out which cell type is assoc with the gid
                # create cells based on loc property
                # creates a NetCon object internally to Neuron
                if type == 'L2_pyramidal':
                    self.cells_list.append(L2Pyr(pos))
                    self.pc.cell(gid, self.cells_list[-1].connect_to_target(None))

                elif type == 'L5_pyramidal':
                    self.cells_list.append(L5Pyr(pos))
                    self.pc.cell(gid, self.cells_list[-1].connect_to_target(None))
                    
                elif type == 'L2_basket':
                    self.cells_list.append(L2Basket(pos))
                    self.pc.cell(gid, self.cells_list[-1].connect_to_target(None))
                    
                elif type == 'L5_basket':
                    self.cells_list.append(L5Basket(pos))
                    self.pc.cell(gid, self.cells_list[-1].connect_to_target(None))

                elif type == 'evprox':
                    # use self.p_evprox to create these gids
                    mu, sigma = self.__create_ev_params(gid)
                    self.evprox_list.append(ParFeedEvoked(mu, sigma))
                    self.pc.cell(gid, self.evprox_list[-1].connect_to_target())

                elif type == 'extinput':
                    # to find param index, take difference between REAL gid here and gid start point of the items
                    p_ind = gid - self.gid_dict['extinput'][0]

                    # now use the param index in the params and create the cell and artificial NetCon
                    # what is self.t_evoked?
                    # self.t_evoked = nrn.Vector([10.])
                    self.extinput_list.append(ParFeedExt(self.origin, self.p_ext[p_ind]))
                    self.pc.cell(gid, self.extinput_list[-1].connect_to_target())

                elif type == 'extgauss':
                    # use self.p_ext_gauss to create these gids
                    mu, sigma = self.__create_extgauss_params(gid)
                    self.extgauss_list.append(ParFeedExtGauss(mu, sigma))
                    self.pc.cell(gid, self.extgauss_list[-1].connect_to_target())

                elif type == 'extpois':
                    lamtha = self.__create_extpois_params(gid)
                    # lamtha = self.p_ext_pois['lamtha']
                    t_interval = self.p_unique['ext_pois']['t_interval']

                    self.extpois_list.append(ParFeedExtPois(lamtha, t_interval))
                    self.pc.cell(gid, self.extpois_list[-1].connect_to_target())

                else:
                    print "None of these types in Net()"
                    exit()

            else:
                print "GID does not exist. See Cell()"
                exit()

    # connections:
    # this NODE is aware of its cells as targets
    # for each syn, return list of source GIDs.
    # for each item in the list, do a: nc = pc.gid_connect(source_gid, target_syn), weight,delay
    # Both for synapses AND for external inputs
    def __parnet_connect(self):
        # loop over target zipped gids and cells
        # cells_list has NO extinputs anyway. also no extgausses
        for gid, cell in it.izip(self.__gid_list, self.cells_list):
            # ignore iteration over inputs, since they are NOT targets
            if self.pc.gid_exists(gid) and self.gid_to_type(gid) is not 'extinput':
                # print "rank:", self.rank, "gid:", gid, cell, self.gid_to_type(gid)

                # for each gid, find all the other cells connected to it, based on gid
                # this MUST be defined in EACH class of cell in self.cells_list
                cell.parconnect(gid, self.gid_dict, self.pos_dict, self.p)
                cell.parreceive(gid, self.gid_dict, self.pos_dict, self.p_ext)

                # now do the gaussian inputs specific to these cells
                cell.parreceive_evprox(gid, self.gid_dict, self.pos_dict, self.p_unique['evprox'])
                cell.parreceive_gauss(gid, self.gid_dict, self.pos_dict, self.p_unique['ext_gauss'])
                cell.parreceive_pois(gid, self.gid_dict, self.pos_dict, self.p_unique['ext_pois'])

    # setup spike recording for this node
    def __record_spikes(self):
        # iterate through gids on this node and set to record spikes in spike time vec and id vec
        # agnostic to type of source, will sort that out later
        for gid in self.__gid_list:
            if self.pc.gid_exists(gid):
                self.pc.spike_record(gid, self.spiketimes, self.spikegids)

    # recording debug function
    def rec_debug(self, rank_exec, gid):
        # only execute on this rank, make sure called properly
        if rank_exec == self.rank:
            # only if the gid exists here
            # this will break if non-cell source is attempted
            if gid in self.__gid_list:
                n = self.__gid_list.index(gid)
                v = nrn.Vector()
                v.record(self.cells_list[n].soma(0.5)._ref_v)

                return v

    # initializes the state closer to baseline
    def __state_init(self):
        for cell in self.cells_list:
           seclist = nrn.SectionList()
           seclist.wholetree(sec=cell.soma)
           
        for sect in seclist:
            for seg in sect:
                if cell.celltype == 'L2_pyramidal':
                    seg.v = -71.46

                elif cell.celltype == 'L5_pyramidal':
                    if sect.name() == 'L5Pyr_apical_1':
                        seg.v = -71.32

                    elif sect.name() == 'L5Pyr_apical_2':
                        seg.v = -69.08

                    elif sect.name() == 'L5Pyr_apical_tuft':
                        seg.v = -67.30

                    else:
                        seg.v = -72.

                elif cell.celltype == 'L2_basket':
                    seg.v = -64.9737

                elif cell.celltype == 'L5_basket':
                    seg.v = -64.9737
                 
