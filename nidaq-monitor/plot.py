# -*- coding: utf-8 -*-
"""
@name:          new_program.py
@vers:          0.1.0
@author:        dthor
@created:       Mon Jan 05 10:30:01 2015
@descr:         A new file

Usage:
    new_program.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.
"""

from __future__ import print_function, division#, absolute_import
#from __future__ import unicode_literals
#from docopt import docopt
import wx
import numpy as np
import random

__author__ = "Douglas Thor"
__version__ = "v0.1.0"


class ScrollingListPlot(wx.Panel):
    """
    Plot things.
    """
    def __init__(self,
                 parent,
                 data_shape=(1, 6),
                 data=None
                 ):
        wx.Panel.__init__(self, parent)

        self.data_shape = data_shape
        self.data = None

        self.init_data(data)

        print(self.data)

        self.add_point(None)
        print(self.data)

    def init_ui(self):
        """ Create the panel UI """
        pass

    def init_data(self, data):
        """ Write the initial dataset to our data handler """
        if data is None:
            # Make a fake data set
            temp = []
            for _i in xrange(self.data_shape[0]):
                temp.append(np.arange(self.data_shape[1], dtype=np.float))
            self.data = np.column_stack(tuple(temp)).T
        else:
            self.data = data

    def add_point(self, point):
        """ append a data point to the data set """
        if point is None:
            # Make a fake data point to add.
            point = [random.random() for _i in xrange(self.data_shape[0])]
            print(point)

        # convert to a 1d array if it's not already
        if not isinstance(point, np.ndarray):
            print("converting to numpy array")
            point = np.array(point)

        if len(point) != self.data.shape[0]:
            raise TypeError("point does not have same shape as data")

        # Move data down via Roll
        self.data = np.roll(self.data, -1, axis=1)

        # Replace the last item in the list.
        for _i, val in enumerate(point):
            self.data[_i][-1] = val

    def change_point(self, point, index):
        """ Change the point at index to a new value """
        pass

    def _update_plot(self):
        """ Updates the plot with any new data """
        pass


class _TestFrame(wx.Frame):
    """ a Frame made only to test operation of the panel """
    def __init__(self):
        wx.Frame.__init__(self, None)
        self.panel = ScrollingListPlot(self)


def main():
    """ Main Code """
#    docopt(__doc__, version=__version__)
    app = wx.App()
    frame = _TestFrame()
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
