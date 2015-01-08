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
from wx.lib.floatcanvas import FloatCanvas
import numpy as np
import random
import time

__author__ = "Douglas Thor"
__version__ = "v0.1.0"


#class ExamplePlot(PlotCanvas.PlotCanvas):
#    """
#    """
#    def __init__(self

class ScrollingListPlot(wx.Panel):
    """
    Plots up data as a list plot

    I need to decide how I want to handle things:

    A.  Does the user enter a data point pair for each value? Meaning that
        they need (x, y) values and, if using as a listplot al-la Mathematica,
        then they need to increment x themselves?

    B.  Or does the user only enter a single data point y and the plot takes
        care of incrementing x with either a number or a timestamp?

    C.  Should option A and B be separate? Can they even be joined into one
        class?

    What if, instead of adding points and lines one-by-one, I just redraw
    the entire buffer on each update? This should still be relatively quick
    even for fairly large buffers.

    Inputs:
    -------

    num_data_sets:
        How many Y data sets to be plotted

    max_pts:
        The number of X points that will be stored in the plot history.

    displayed_pts:
        The number of X points that will be displayed at any given time.

    timestamp_x:
        This defines how the x values are defined. Default is uniform spacing.

        False:
            points are uniformly spaced along the X axis.

        True:
            X values are the timestamp of when the point was added. This could
            cause points to be non-uniformly spaced.
    """
    def __init__(self,
                 parent,
                 num_data_sets=3,
                 max_pts=10,
                 displayed_pts=5,
                 timestamp_x=False,
                 ):
        """
        __init__(self,
                 wx.Window parent,
                 int num_data_sets=1,
                 int max_pts=2048,
                 int displayed_pts=20,
                 ) -> wx.Panel
        """
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.num_data_sets = num_data_sets
        self.max_pts = max_pts
        self.data_shape = (num_data_sets, max_pts)
        self.y_data = None
        if not isinstance(timestamp_x, bool):
            raise ValueError("timestamp_x must be boolean True or False.")
        self.timestamp_x = timestamp_x
        self.colors = {0: wx.RED,
                       1: wx.GREEN,
                       2: wx.CYAN,
                       3: wx.WHITE,
                       }

        self.prev_point = None
        self.x_pt = 0
        self.x_data = np.zeros(self.max_pts, dtype=np.float)
        self.x_data[:] = np.NaN

        self.init_data(self.y_data)

        self.timer = wx.Timer(self)

        self.init_ui()
        self._bind_events()
        self._start_timer()

    def init_ui(self):
        """ Create the panel UI """
        self.canvas = FloatCanvas.FloatCanvas(self,
                                              wx.ID_ANY,
                                              BackgroundColor="BLACK",
                                              )

        self.canvas.InitAll()

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.hbox)

    def _bind_events(self):
        """ Bind events to things """
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def _start_timer(self):
        """
        This is only used in Demo mode.

        Start the timer
        """
        self.timer.Start(750)

    def on_timer(self, event):
        """
        This is only used in Demo mode.

        Normaly the add_point() method is what adds points and lines to the
        plot.
        """
        self.add_point()

    def init_data(self, data=None):
        """ Write the initial dataset to our data handler """
        if data is None:
            # Make a fake data set
            temp = []
            for _i in xrange(self.data_shape[0]):
                temp.append(np.arange(self.data_shape[1], dtype=np.float))
            self.y_data = np.column_stack(tuple(temp)).T
            self.y_data[:] = np.NaN
        else:
            self.y_data = data

    def add_point(self, point=None):
        """ append a data point to the data set """
        if point is None:
            # Make a fake data point to add.
            point = [random.random()+_i for _i in xrange(self.data_shape[0])]

        # convert to a 1d array if it's not already
        if not isinstance(point, np.ndarray):
            point = np.array(point)

        if len(point) != self.y_data.shape[0]:
            raise TypeError("point does not have same shape as data")

        # Move data down via Roll
        self.y_data = np.roll(self.y_data, -1, axis=1)
        self.x_data = np.roll(self.x_data, -1, axis=0)

        # Replace the last item in the list.
        if self.timestamp_x:
            self.x_data[-1] = time.time()
        else:
            self.x_data[-1] = self.x_pt
        for _i, val in enumerate(point):
            self.y_data[_i][-1] = val

#        self.draw_line()
#        self.draw_point(point)
        self._update_plot()

        self.increment_x_pt()
        return point

    def increment_x_pt(self):
        """ Increases our index variable """
        self.x_pt += 1

    def draw_point(self, ys):
        """
        Draws the newly added point(s)
        """
        for _i, _y in enumerate(ys):
            pt = FloatCanvas.Point((self.x_data[-1], _y),
                                   Color=self.colors[_i],
                                   Diameter=4)
            self.canvas.AddObject(pt)

        self.canvas.Update()
        self.canvas.ZoomToBB()

    def draw_line(self):
        """
        Draws the line connecting the previous point(s) and the current one
        """
        if self.x_pt == 0:
            # We can't draw a line because there's no previous point
            return
        for _i in xrange(self.num_data_sets):
            pts = ((self.x_data[-2], self.y_data[_i][-2]),
                   (self.x_data[-1], self.y_data[_i][-1]))
            line = FloatCanvas.Line(pts,
                                    LineColor=self.colors[_i],
                                    LineWidth=1,
                                    )

            self.canvas.AddObject(line)

    def change_point(self, point, index):
        """
        Change the point at index to a new value.

        1. Finds the point in the dataset
        2. Finds the point(s) around it
        3. Removes the point and joining lines from the plot
        4. Updates the point in the data
        5. Adds the new point and joining lines to the plot
        """
        pass

    def _update_plot(self):
        """ Updates the plot with any new data """
        self.canvas.ClearAll()
        for _i in xrange(self.num_data_sets):
            pts = np.column_stack((self.x_data, self.y_data[_i]))

            # Remove rows that have NaN values
            pts = pts[~np.isnan(pts).any(1)]

            # TODO: Add points as well.
            line = FloatCanvas.Line(pts,
                                    LineColor=self.colors[_i],
                                    LineWidth=1,
                                    )
            self.canvas.AddObject(line)

        self.canvas.Update()
        self.canvas.ZoomToBB()


class _TestFrame(wx.Frame):
    """
    A frame made only to test operation of the panel.
    """
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
