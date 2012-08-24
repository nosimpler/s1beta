# usage:
# testfig = fig_std()
# testfig.ax0.plot(somedata)
# plt.savefig('testfig.png')
# testfig.close()

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

class fig_std():
    def __init__(self):
        self.f = plt.figure(figsize = (12, 6))
        font_prop = {'size': 10}
        mpl.rc('font', **font_prop)

        gs0 = gridspec.GridSpec(1, 1)
        self.ax0 = self.f.add_subplot(gs0[:])

    def close(self):
        plt.close(self.f)

def testfn():
    testfig = fig_std()

    x = np.random.rand(100)

    testfig.ax0.plot(x)
    plt.savefig('testing.png')
    testfig.close()

if __name__ == '__main__':
    testfn()
