# class_net.py - establishes the Network class and related methods
#
# v 1.7.17
# rev 2013-01-23 (SL: Removed ParFeedExt in favor of ParFeedAll)
# last major: (SL: minor)

import itertools as it
import numpy as np
import sys

from neuron import h as nrn
from fn.class_feed import ParFeedAll
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

        # seed debugging
        # for key, val in self.p.iteritems():
        #     if key.startswith('prng_seedcore_'):
        #         print "in net: %i, %s, %i" % (self.rank, key, val)

        # numbers of sources
        self.N = {}

        # zdiff is expressed as a positive DEPTH of L5 relative to L2
        # this is a deviation from the original, where L5 was defined at 0
        # this should not change interlaminar weight/delay calculations
        self.zdiff = 1307.4 

        # params of external inputs in p_ext
        # Global number of external inputs ... automatic counting makes more sense
        # p_unique represent ext inputs that are going to go to each cell
        self.p_ext, self.p_unique = paramrw.create_pext(self.p, nrn.tstop)
        self.N_extinput = len(self.p_ext)

        # Source list of names
        # in particular order (cells, extinput, alpha names of unique inputs)
        self.src_list_new = self.__create_src_list()

        # cell position lists, also will give counts: must be known by ALL nodes
        # extinput positions are all located at origin.
        # sort of a hack bc of redundancy
        self.pos_dict = dict.fromkeys(self.src_list_new)

        # create coords in pos_dict for all cells first
        self.__create_coords_pyr()
        self.__create_coords_basket()
        self.__count_cells()

        # create coords for all other sources
        self.__create_coords_extinput()

        # count external sources
        self.__count_extsrcs()

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

        # external unique input list dictionary
        self.ext_list = dict.fromkeys(self.p_unique)

        # initialize the lists in the dict
        for key in self.ext_list.keys():
            self.ext_list[key] = []

        # create sources and init
        self.__create_all_src()
        self.__state_init()

        # parallel network connector
        self.__parnet_connect()

        # set to record spikes
        self.spiketimes = nrn.Vector()
        self.spikegids = nrn.Vector()
        self.__record_spikes()

    # creates the immutable source list along with corresponding numbers of cells
    def __create_src_list(self):
        # base source list of tuples, name and number, in this order
        self.cellname_list = [
            'L2_basket',
            'L2_pyramidal',
            'L5_basket',
            'L5_pyramidal',
        ]

        # add the legacy extinput here
        self.extname_list = []
        self.extname_list.append('extinput')

        # grab the keys for the unique set of inputs and sort the names
        # append them to the src list along with the number of cells
        unique_keys = sorted(self.p_unique.keys())
        self.extname_list += unique_keys

        # return one final source list
        src_list = self.cellname_list + self.extname_list
        return src_list

    # Creates cells and grid
    # pyr grid is the immutable grid, origin now calculated in relation to feed
    def __create_coords_pyr(self):
        xrange = np.arange(self.gridpyr['x'])
        yrange = np.arange(self.gridpyr['y'])

        # create list of tuples/coords, (x, y, z)
        self.pos_dict['L2_pyramidal'] = [pos for pos in it.product(xrange, yrange, [0])]
        self.pos_dict['L5_pyramidal'] = [pos for pos in it.product(xrange, yrange, [self.zdiff])]

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

    # creates origin AND creates external input coords 
    # (same thing for now but won't fix because could change)
    def __create_coords_extinput(self):
        xrange = np.arange(self.gridpyr['x'])
        yrange = np.arange(self.gridpyr['y'])

        # origin's z component isn't really used in calculating distance functions from origin
        # these must be ints!
        origin_x = xrange[(len(xrange)-1)/2]
        origin_y = yrange[(len(yrange)-1)/2]
        origin_z = np.floor(self.zdiff/2)
        self.origin = (origin_x, origin_y, origin_z)

        # debugging override
        # self.origin = (0.5, 0.5, 653.)

        self.pos_dict['extinput'] = [self.origin for i in range(self.N_extinput)]

        # at this time, each of the unique inputs is per cell
        for key in self.p_unique.keys():
            # create the pos_dict for all the sources
            self.pos_dict[key] = [self.origin for i in range(self.N_cells)]

    # cell counting routine
    def __count_cells(self):
        # init self.N_cells
        self.N_cells = 0

        # cellname list is used *only* for this purpose for now
        for src in self.cellname_list:
            # if it's a cell, then add the number to total number of cells
            self.N[src] = len(self.pos_dict[src])
            self.N_cells += self.N[src]

    # general counting method requires pos_dict is correct for each source
    # and that all sources are represented
    def __count_extsrcs(self):
        # all src numbers are based off of length of pos_dict entry
        # generally done here in lieu of upstream changes

        for src in self.extname_list:
            self.N[src] = len(self.pos_dict[src])

    # creates gid dicts and pos_lists
    def __create_gid_dict(self):
        # initialize gid index gid_ind to start at 0
        gid_ind = [0]

        # append a new gid_ind based on previous and next cell count
        # order is guaranteed by self.src_list_new
        for i in range(len(self.src_list_new)):
            # N = self.src_list_new[i][1]
            # grab the src name in ordered list src_list_new
            src = self.src_list_new[i]
            
            # query the N dict for that number and append here to gid_ind, based on previous entry
            gid_ind.append(gid_ind[i]+self.N[src])

            # accumulate total source count
            self.N_src += self.N[src]

        # dictionary of gids for each source
        self.gid_dict = {}

        # now actually assign the ranges
        for i in range(len(self.src_list_new)):
            src = self.src_list_new[i]
            self.gid_dict[src] = range(gid_ind[i], gid_ind[i+1])

    # this happens on EACH node
    # creates self.__gid_list for THIS node
    def __gid_assign(self):
        # round robin assignment of gids
        for gid in range(self.rank, self.N_cells, self.n_hosts):
            # set the cell gid
            self.pc.set_gid2node(gid, self.rank)
            self.__gid_list.append(gid)

            # now to do the cell-specific external input gids on the same proc
            # these are guaranteed to exist because all of these inputs were created
            # for each cell
            for key in self.p_unique.keys():
                gid_input = gid + self.gid_dict[key][0]
                self.pc.set_gid2node(gid_input, self.rank)
                self.__gid_list.append(gid_input)

        # legacy handling of the external inputs
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
    def gid_to_type(self, gid):
        for gidtype, gids in self.gid_dict.iteritems():
            if gid in gids:
                return gidtype

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

                elif type == 'extinput':
                    # to find param index, take difference between REAL gid
                    # here and gid start point of the items
                    p_ind = gid - self.gid_dict['extinput'][0]

                    # now use the param index in the params and create
                    # the cell and artificial NetCon
                    self.extinput_list.append(ParFeedAll(type, None, self.p_ext[p_ind], gid))
                    # self.extinput_list.append(ParFeedExt(self.origin, self.p_ext[p_ind], gid))
                    self.pc.cell(gid, self.extinput_list[-1].connect_to_target())

                elif type in self.p_unique.keys():
                    gid_post = gid - self.gid_dict[type][0]
                    cell_type = self.gid_to_type(gid_post)

                    # create dictionary entry, append to list
                    self.ext_list[type].append(ParFeedAll(type, cell_type, self.p_unique[type], gid))
                    self.pc.cell(gid, self.ext_list[type][-1].connect_to_target())

                else:
                    print "None of these types in Net()"
                    exit()

            else:
                print "GID does not exist. See Cell()"
                exit()

    # connections:
    # this NODE is aware of its cells as targets
    # for each syn, return list of source GIDs.
    # for each item in the list, do a:
    # nc = pc.gid_connect(source_gid, target_syn), weight,delay
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

                # now do the unique inputs specific to these cells
                for type in self.p_unique.keys():
                    p_type = self.p_unique[type]
                    cell.parreceive_ext(type, gid, self.gid_dict, self.pos_dict, p_type)

    # setup spike recording for this node
    def __record_spikes(self):
        # iterate through gids on this node and
        # set to record spikes in spike time vec and id vec
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
