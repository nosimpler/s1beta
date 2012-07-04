# This is a non-used function that should be a good file to test other junk on
# this is a conflicting comment

# cells_L5.py

class Cell():
    def __init__(self):
        # 3d position variables for a cell
        self.x = x
        self.y = y
        self.z = z
 
        # list of all sections in a cell
        self.all_sec = []

    # add a compartment
    # needs to both add a compartment and record the name of it
    # def add_comp:

    def calc_area(self):
        # total area
        self.area_cell = 0

        # calculate number of sections
        self.n = 0

        # iterate over all_sec to find sec
        for sec_each in self.all_sec:
            self.total_area += h.area(0.5, sec = sec_each)
            self.n += 1

# Layer 5 pyramidal cell
# inherits Cell class
class pyr_L5(Cell):
    def set_morphology(self):
        # total_area = 10000   # um^2
        self.soma.nseg = 1

class basket(Cell):
    def set_morphology(self):
        self.soma.L = 39
        self.soma.diam = 20
        self.soma.Ra = 200
        self.soma.cm = 0.85

        h.pt3dclear(sec = self.soma)
        h.pt3dadd(self.x, self.y, self.z, diam, sec = self.soma)
        h.pt3dadd(self.x, self.y, self.z + L, diam, sec = self.soma)

    def set_conductances(self):
        self.soma.insert('pas')
