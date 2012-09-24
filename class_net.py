# class_net.py - establishes the Network class and related methods
#
# v 1.1.0
# rev 2012-09-24 (SL: Records spikes, also has debug record voltage capability)
# last major: (SL: lots of clean up)

import itertools as it
import numpy as np

from neuron import h as nrn
from fn.class_feed import ParFeedExt
from cells.L5_pyramidal import L5Pyr
from cells.L2_pyramidal import L2Pyr
from cells.L2_basket import L2Basket
from cells.L5_basket import L5Basket
from params_extinput import p_ext

# create Network class
class Network():
    def __init__(self, gridpyr_x, gridpyr_y):
        # int variables for grid of pyramidal cells (for now in both L2 and L5)
        self.gridpyr = {'x': gridpyr_x, 'y': gridpyr_y}

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
        self.p_ext = p_ext
        self.N_extinput = len(self.p_ext)

        # cell position lists, also will give counts
        # extinput positions are all located at origin. This is sort of a hack bc of redundancy
        self.pos_list = []
        self.L2_pyr_pos = []
        self.L5_pyr_pos = []
        self.L2_basket_pos = []
        self.L5_basket_pos = []
        self.extinput_pos = []

        # create coords and counts in self.N_{celltype} variables
        self.__create_coords_pyr()
        self.__create_coords_basket()
        self.__create_coords_extinput()

        # ugly for now
        self.src_counts = (self.N_L2_pyr, self.N_L5_pyr, self.N_L2_basket, self.N_L5_basket, self.N_extinput)

        # create dictionary of GIDs according to cell type
        # global dictionary of gid and cell type
        self.__create_gid_dict()

        # assign gid to hosts, creates list of gids for this node in __gid_list
        # __gid_list length is number of cells assigned to this id()
        self.__gid_list = []
        self.__gid_assign()

        # create cells (and create self.origin in create_cells_pyr())
        self.cells_list = []
        self.extinput_list = []
        self.__create_all_src()

        # parallel network connector
        self.__parnet_connect()

        # set to record spikes
        self.spiketimes = nrn.Vector()
        self.spikegids = nrn.Vector()
        self.__record_spikes()

    # setup spike recording for this node
    def __record_spikes(self):
        # iterate through gids on this node and set to record spikes in spike time vec and id vec
        # agnostic to type of source, will sort that out later
        for gid in self.__gid_list:
            if self.pc.gid_exists(gid):
                self.pc.spike_record(gid, self.spiketimes, self.spikegids)

    # creates gid dicts and pos_lists
    def __create_gid_dict(self):
        # initialize gid index gid_ind to start at 0
        gid_ind = [0]

        # append a new gid_ind based on previous and next cell count
        for i in range(len(self.src_counts)):
            gid_ind.append(gid_ind[i]+self.src_counts[i])

        self.gid_dict = {
            'L2_pyramidal': range(gid_ind[0], gid_ind[1]),
            'L5_pyramidal': range(gid_ind[1], gid_ind[2]),
            'L2_basket': range(gid_ind[2], gid_ind[3]),
            'L5_basket': range(gid_ind[3], gid_ind[4]),
            'extinput': range(gid_ind[4], gid_ind[5])
        }

        # total position list in order of gid
        self.pos_list = self.L2_pyr_pos + self.L5_pyr_pos + self.L2_basket_pos + self.L5_basket_pos + self.extinput_pos

        for count in self.src_counts:
            self.N_src += count

    # this happens on EACH node
    # creates self.__gid_list for THIS node
    def __gid_assign(self):
        # round robin assignment of gids
        # if gids are created here for the inputs, the N_cells will be changed to N_src
        for gid in range(self.rank, self.N_src, self.n_hosts):
            self.pc.set_gid2node(gid, self.rank)
            self.__gid_list.append(gid)

    # reverse lookup of gid to type
    # there may be a better, more general way to do this
    def gid_to_type(self, gid):
        if gid in self.gid_dict['L2_pyramidal']:
            return 'L2_pyramidal'

        if gid in self.gid_dict['L5_pyramidal']:
            return 'L5_pyramidal'

        if gid in self.gid_dict['L2_basket']:
            return 'L2_basket'

        if gid in self.gid_dict['L5_basket']:
            return 'L5_basket'

        if gid in self.gid_dict['extinput']:
            return 'extinput'

    # Creates cells and grid
    # pyr grid is the immutable grid, origin now calculated in relation to feed
    def __create_coords_pyr(self):
        xrange = np.arange(self.gridpyr['x'])
        yrange = np.arange(self.gridpyr['y'])

        # create list of tuples/coords, (x, y, z)
        self.L2_pyr_pos = [pos for pos in it.product(xrange, yrange, [0])]
        self.L5_pyr_pos = [pos for pos in it.product(xrange, yrange, [self.zdiff])]

        self.N_L2_pyr = len(self.L2_pyr_pos)
        self.N_L5_pyr = len(self.L5_pyr_pos)

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
        self.L2_basket_pos = [pos_xy + (0,) for pos_xy in coords_sorted]
        self.L5_basket_pos = [pos_xy + (self.zdiff,) for pos_xy in coords_sorted]

        # number of cells
        self.N_L2_basket = len(self.L2_basket_pos)
        self.N_L5_basket = len(self.L5_basket_pos)

    # creates origin AND creates external input coords (same thing)
    def __create_coords_extinput(self):
        xrange = np.arange(self.gridpyr['x'])
        yrange = np.arange(self.gridpyr['y'])

        # origin's z component isn't really used in calculating distance functions from origin
        # these must be ints!
        origin_x = xrange[(len(xrange)-1)/2]
        origin_y = yrange[(len(yrange)-1)/2]
        origin_z = np.floor(self.zdiff/2)
        self.origin = (origin_x, origin_y, origin_z)

        self.extinput_pos = [self.origin for i in range(self.N_extinput)]

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
                pos = self.pos_list[gid]

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

                elif type == 'extinput':
                    # to find param index, take difference between REAL gid here and gid start point of the items
                    p_ind = gid - self.gid_dict['extinput'][0]

                    # now use the param index in the params and create the cell and artificial NetCon
                    self.t_evoked = nrn.Vector([10.])
                    self.extinput_list.append(ParFeedExt(self.origin, self.p_ext[p_ind]))
                    self.pc.cell(gid, self.extinput_list[-1].connect_to_target(None))

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
        # print "in parnetcon", self.p_ext
        # loop over target zipped gids and cells
        for gid, cell in it.izip(self.__gid_list, self.cells_list):
            # ignore iteration over inputs, since they are NOT targets
            if self.pc.gid_exists(gid) and self.gid_to_type(gid) is not 'extinput':
                # print "rank:", self.rank, "gid:", gid, cell, self.gid_to_type(gid)

                # for each gid, find all the other cells connected to it, based on gid
                # this MUST be defined in EACH class of cell in self.cells_list
                cell.parconnect(gid, self.gid_dict, self.pos_list)
                cell.parreceive(gid, self.gid_dict, self.pos_list, self.p_ext)

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
