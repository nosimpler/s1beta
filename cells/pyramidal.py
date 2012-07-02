from neuron import h
from class_cell import Cell

class Pyr(Cell):
    def __init__(self):
        Cell.__init__(self, 28.9, 39)
        # super(Inherit_Pyr, self).__init__()

        # sections of these cells
        self.list_dend = []
        self.list_dend_prox = []
        self.list_dend_dist = []
        self.create_sections(8)
        self.shape_change()
        self.connect_sections()

        # synapse on THIS cell needs to be RECEIVING FROM Inh
        self.syn = h.Exp2Syn(self.soma(0.5))
        self.syn.e = -80
        self.syn.tau1 = 1
        self.syn.tau2 = 20

    # this replicates topol
    def create_sections(self, N_dend):
        # Trying to create sections directly
        for i in range(0, N_dend):
            self.list_dend.append(h.Section())
            self.list_dend[i].insert('hh')
            # print self.list_dend[i]

    def shape_change(self):
        # soma proximal coords
        x_prox = 0
        y_prox = 0

        # soma distal coords
        x_distal = 0
        y_distal = 23

        h.pt3dclear(sec=self.soma)
        h.pt3dadd(x_prox, y_prox, 0, 1, sec=self.soma)
        h.pt3dadd(x_distal, y_distal, 0, 1, sec=self.soma)

        # changes in x and y pt3d coords
        dend_dx = [60,    0, 400, 400, 250, -50, -106, -106]
        dend_dy = [ 0, -150,   0,   0,   0,   0, -106, -106]

        # dend 0-3 are major axis, dend 4 is branch
        # deal with distal first along major cable axis
        for i in range(0, 4):
            h.pt3dclear(sec=self.list_dend[i])

            # x_distal and y_distal are the starting points for each segment
            # these are updated at the end of the loop
            h.pt3dadd(x_distal, y_distal, 0, 1, sec=self.list_dend[i])

            # update x_distal and y_distal after setting them
            x_distal += dend_dx[i]
            y_distal += dend_dy[i]

            # add next point
            h.pt3dadd(x_distal, y_distal, 0, 1, sec=self.list_dend[i])

        # now deal with dend 4
        h.pt3dclear(sec=self.list_dend[4])
        # h.pt3dadd(x_distal, y_distal)
        # dend 5-7 are proximal

        # h.pt3dclear(sec=self.list_dend[0])
        # h.pt3dadd(0, 23, 0, 1, sec=self.list_dend[0])
        # h.pt3dadd(0, 83, 0, 1, sec=self.list_dend[0])

        print "testing"

    def connect_sections(self):
        # connect(parent, parent_end, child_start)
        # Distal
        self.list_dend[0].connect(self.soma, 1, 0)
        self.list_dend[1].connect(self.list_dend[0], 1, 0)

        self.list_dend[2].connect(self.list_dend[0], 1, 0)
        self.list_dend[3].connect(self.list_dend[2], 1, 0)
        self.list_dend[4].connect(self.list_dend[3], 1, 0)

        # Proximal
        self.list_dend[5].connect(self.soma, 1, 1)
        self.list_dend[6].connect(self.list_dend[5], 1, 0)
        self.list_dend[7].connect(self.list_dend[0], 1, 0)

        # for dend in self.list_dend:
