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

from __future__ import print_function, division
from __future__ import absolute_import
#from __future__ import unicode_literals
#from docopt import docopt
import wx
from wx.lib.floatcanvas import FloatCanvas
import numpy as np
import random
import time

__author__ = "Douglas Thor"
__version__ = "v0.1.0"


wx.MAGENTA = wx.Colour(255, 0, 255, 255)
wx.GREY = wx.Colour(192, 192, 192, 255)
wx.GRAY = wx.GREY


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

    moving_avg:
        Display a moving average dashed line for each data set. Boolean

    moving_avg_pts:
        Int. How many data points should be used to calculate the moving
        average

    moving_max:
        Boolean. True displayes a dotted line representing the moving maximum.

    moving_max_pts:
        Int. How many data points should be used to calculate the moving
        maximum. Defaults to the same number as ``moving_avg_pts``.

    lwl:
        Lower Warning Limit. Triggers a warning alarm when any data point is
        above this value.

    uwl:
        Upper Warning Limit. Triggers a warning alarm when any data point is
        above this value.

    lcl:
        Lower Critical Limit. Triggers a critical alarm when any data point is
        above this value.

    ucl:
        Upper Critical Limit. Triggers a critical alarm when any data point is
        above this value.

    End Descr.
    """
    def __init__(self,
                 parent,
                 num_data_sets=3,
                 max_pts=50,
                 displayed_pts=5,
                 timestamp_x=False,
                 moving_avg=False,
                 moving_avg_pts=10,
                 moving_max=False,
                 moving_max_pts=None,
                 lwl=-2,
                 uwl=5,
                 lcl=-5,
                 ucl=10,
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
        self.displayed_pts = displayed_pts
        if not isinstance(timestamp_x, bool):
            raise ValueError("timestamp_x must be boolean True or False.")
        self.timestamp_x = timestamp_x
        if not isinstance(moving_avg, bool):
            raise ValueError("moving_avg must be boolean True or False.")
        self.moving_avg = moving_avg
        self.moving_avg_pts = moving_avg_pts
        self.moving_max = moving_max
        self.moving_max_pts = moving_max_pts
        if moving_max_pts is None:
            self.moving_max_pts = self.moving_avg_pts
        self.lwl = lwl
        self.uwl = uwl
        self.lcl = lcl
        self.ucl = ucl

        self.data_shape = (num_data_sets, max_pts)
        self.y_data = None

        self.colors = {0: wx.WHITE,         # Reading
                       1: wx.YELLOW,        # Lower Warning
                       2: wx.YELLOW,        # Upper Warning
                       3: wx.RED,           # Lower Critical
                       4: wx.RED,           # Upper Critical
                       5: wx.CYAN,          # Moving Average
                       6: wx.MAGENTA,       # Moving Maximum
                       }

        self.linewidths = {0: 1,
                           1: 1,
                           2: 1,
                           3: 1,
                           4: 1,
                           5: 1,
                           6: 1,
                           }

        self.prev_point = None
        self.x_pt = 0
        self.x_data = np.zeros(self.max_pts, dtype=np.float64)
#        self.x_data[:] = np.NaN

        # If using timestamps, fill the x data with n previous seconds
        if self.timestamp_x:
            _now = time.time()
            self.x_data = np.arange(_now - self.max_pts,
                                    _now,
                                    1,
                                    dtype=np.float64)
        else:
            self.x_data = np.arange(-self.max_pts, 0, 1, dtype=np.float64)

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
#        self.canvas.GridUnder = Grid((2, 1),
#                                     Size=4,
#                                     Color="Grey",
#                                     Cross=True
#                                     )
        self.canvas.GridUnder = Grid((5, 6),
                                     num_minor_x_lines=0,
                                     num_minor_y_lines=0,
                                     )

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
        self.timer.Start(500)

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

        self._update_plot()

        self.increment_x_pt()
        return point

    def increment_x_pt(self):
        """ Increases our index variable """
        self.x_pt += 1

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

        # Add the limit lines
        self._add_limit_lines()

        for _i in xrange(self.num_data_sets):
            pts = np.column_stack((self.x_data, self.y_data[_i]))

            # Remove rows that have NaN values
            pts = pts[~np.isnan(pts).any(1)]

            for pt in pts:
                point = FloatCanvas.Point(pt,
                                          Color=self.colors[_i],
                                          Diameter=3,
                                          )

                self.canvas.AddObject(point)

            line = FloatCanvas.Line(pts,
                                    LineColor=self.colors[_i],
                                    LineWidth=self.linewidths[_i],
                                    )

            # Calculate the moving average for this data
#            self.calc_moving_avg(self.y_data[_i])

            # Calculate the moving max for this data
#            self.calc_moving_max(self.y_data[_i])

            self.canvas.AddObject(line)

        self.canvas.Update()
        self.canvas.ZoomToBB()

    def _add_limit_lines(self):
        """ Creates the limit lines and adds them to the plot """
        # TODO: Could probably use FloatCanvas.GridOver to achieve this...
        if self.uwl is not None:
            uwl_pts = ((self.x_data[0], self.uwl),
                       (self.x_data[-1], self.uwl))
            uwl_line = FloatCanvas.Line(uwl_pts,
                                        LineColor=wx.YELLOW,
                                        LineWidth=1,
                                        LineStyle="LongDash"
                                        )

            self.canvas.AddObject(uwl_line)

        if self.lwl is not None:
            lwl_pts = ((self.x_data[0], self.lwl),
                       (self.x_data[-1], self.lwl))
            lwl_line = FloatCanvas.Line(lwl_pts,
                                        LineColor=wx.YELLOW,
                                        LineWidth=1,
                                        LineStyle="LongDash"
                                        )

            self.canvas.AddObject(lwl_line)

        if self.ucl is not None:
            ucl_pts = ((self.x_data[0], self.ucl),
                       (self.x_data[-1], self.ucl))
            ucl_line = FloatCanvas.Line(ucl_pts,
                                        LineColor=wx.RED,
                                        LineWidth=1,
                                        LineStyle="LongDash"
                                        )

            self.canvas.AddObject(ucl_line)

        if self.lcl is not None:
            lcl_pts = ((self.x_data[0], self.lcl),
                       (self.x_data[-1], self.lcl))
            lcl_line = FloatCanvas.Line(lcl_pts,
                                        LineColor=wx.RED,
                                        LineWidth=1,
                                        LineStyle="LongDash"
                                        )

            self.canvas.AddObject(lcl_line)

        return

# TODO: Update this to be lines rather than dots
class DotGrid(object):
    """
    An example of a Grid Object -- it is set on the FloatCanvas with one of:

    FloatCanvas.GridUnder = Grid
    FloatCanvas.GridOver = Grid

    It will be drawn every time, regardless of the viewport.

    In its _Draw method, it computes what to draw, given the ViewPortBB
    of the Canvas it's being drawn on.

    """
    def __init__(self,
                 Spacing,
                 Size=2,
                 Color="Black",
                 Cross=False,
                 CrossThickness=1):

        self.Spacing = np.array(Spacing, np.float)
        self.Spacing.shape = (2,)
        self.Size = Size
        self.Color = Color
        self.Cross = Cross
        self.CrossThickness = CrossThickness

    def CalcPoints(self, Canvas):
        ViewPortBB = Canvas.ViewPortBB

        Spacing = self.Spacing

        minx, miny = np.floor(ViewPortBB[0] / Spacing) * Spacing
        maxx, maxy = np.ceil(ViewPortBB[1] / Spacing) * Spacing

        ##fixme: this could use vstack or something with numpy
        # making sure to get the last point
        x = np.arange(minx, maxx + Spacing[0], Spacing[0])
        # an extra is OK
        y = np.arange(miny, maxy + Spacing[1], Spacing[1])
        Points = np.zeros((len(y), len(x), 2), np.float)
        x.shape = (1, -1)
        y.shape = (-1, 1)
        Points[:, :, 0] += x
        Points[:, :, 1] += y
        Points.shape = (-1, 2)

        return Points

    def _Draw(self, dc, Canvas):
        Points = self.CalcPoints(Canvas)

        Points = Canvas.WorldToPixel(Points)

        dc.SetPen(wx.Pen(self.Color, self.CrossThickness))

        if self.Cross:  # Use cross shaped markers
            # Horizontal lines
            LinePoints = np.concatenate((Points + (self.Size, 0),
                                         Points + (-self.Size, 0)),
                                        1)
            dc.DrawLineList(LinePoints)
            # Vertical Lines
            LinePoints = np.concatenate((Points + (0, self.Size),
                                         Points + (0, -self.Size)),
                                        1)
            dc.DrawLineList(LinePoints)
            pass
        else:   # use dots
            # Note: this code borrowed from Pointset
            # it really shouldn't be repeated here!.
            if self.Size <= 1:
                dc.DrawPointList(Points)
            elif self.Size <= 2:
                dc.DrawPointList(Points + (0, -1))
                dc.DrawPointList(Points + (0, 1))
                dc.DrawPointList(Points + (1, 0))
                dc.DrawPointList(Points + (-1, 0))
            else:
                dc.SetBrush(wx.Brush(self.Color))
                radius = int(round(self.Size / 2))
                ##fixme: I really should add a DrawCircleList to wxPython
                if len(Points) > 100:
                    xy = Points
                    xywh = np.concatenate((xy-radius,
                                           np.ones(xy.shape) * self.Size),
                                          1)
                    dc.DrawEllipseList(xywh)
                else:
                    for xy in Points:
                        dc.DrawCircle(xy[0], xy[1], radius)


# TODO: Update this to be lines rather than dots
class Grid(object):
    """
    An example of a Grid Object -- it is set on the FloatCanvas with one of:

    FloatCanvas.GridUnder = Grid
    FloatCanvas.GridOver = Grid

    It will be drawn every time, regardless of the viewport.

    In its _Draw method, it computes what to draw, given the ViewPortBB
    of the Canvas it's being drawn on.

    """
    def __init__(self,
                 spacing,
                 num_minor_x_lines=0,
                 num_minor_y_lines=0,
                 major_lw=1,
                 major_color=wx.GREY,
                 major_style=wx.SOLID,
                 minor_lw=1,
                 minor_color=wx.GREY,
                 minor_style=wx.SOLID,
                 ):

        self.spacing = np.array(spacing, np.float)
        self.spacing.shape = (2,)
        self.num_minor_x_lines = num_minor_x_lines
        self.num_minor_y_lines = num_minor_y_lines
        self.major_lw = major_lw
        self.major_color = major_color
        self.major_style = major_style
        self.minor_lw = minor_lw
        self.minor_color = minor_color
        self.minor_style = minor_style

    def calc_lines(self, canvas):
        """
        Calculate where the gridlines are.

        Returns 4 lists of 4-tuples (x1, y1, x2, y2) - a pair for major lines
        and a 2nd pair for minor lines - to be used with the dc.DrawLineList()
        method.
        """
        ViewPortBB = canvas.ViewPortBB

        spacing = self.spacing

        minx, miny = np.floor(ViewPortBB[0] / spacing) * spacing
        maxx, maxy = np.ceil(ViewPortBB[1] / spacing) * spacing

        major_x = np.arange(minx, maxx + spacing[0], spacing[0])
        major_y = np.arange(miny, maxy + spacing[1], spacing[1])

        # TODO: calculate the minor gridlines and return those
        minor_x = None
        minor_y = None

        if self.num_minor_x_lines == 0:
            minor_x = None
        if self.num_minor_y_lines == 0:
            minor_y = None

        return major_x, major_y, minor_x, minor_y

    def convert_lines(self, canvas, lines, axis=0):
        """
        Takes the gridlines calcualted by calc_lines and converts them
        from World coordinates to pixel coordinates and formats them in
        lists of (x1, y1, x2, y2) tuples for use with the dc.DrawLineList
        method.

        canvas:
            The canvas that is painted on

        lines:
            1D NumPy array denoting the locations of the gridlines for the
            given axis

        axis:
            0: x-axis, drawing vertical lines
            1: y-axis, drawing horizontal lines
        """
        # Get the BB extents
        bb = canvas.ViewPortBB

        if axis == 0:       # x axis
            min_coord, max_coord = bb[:, 1]     # use y-axis extents
        elif axis == 1:     # y axis
            min_coord, max_coord = bb[:, 0]     # use x-axis extents
        else:
            raise ValueError("axis must be 0 (x) or 1 (y)")

        N = lines.size

        # TODO: Make more NumPythonic
        start_coords = np.zeros((2, N), dtype=np.float64)
        if axis == 1:
            start_coords[:][0] = min_coord
            start_coords[:][1] = lines
        else:
            start_coords[:][0] = lines
            start_coords[:][1] = min_coord

        end_coords = np.zeros((2, N), dtype=np.float64)
        if axis == 1:
            end_coords[:][0] = max_coord
            end_coords[:][1] = lines
        else:
            end_coords[:][0] = lines
            end_coords[:][1] = max_coord

        start_coords = canvas.WorldToPixel(start_coords.T)
        end_coords = canvas.WorldToPixel(end_coords.T)

        # TODO: Make more NumPythonic
        pixel_lines = []
        for start, end in zip(start_coords, end_coords):
            pixel_lines.append((start[0], start[1], end[0], end[1]))

        pixel_lines = np.array(pixel_lines, dtype=np.float64)

        return pixel_lines

    def _Draw(self, dc, canvas):
        """ Actually draw the lines """

        # Calculate the lines
        major_x, major_y, _, _ = self.calc_lines(canvas)

        # Need to convert to Pixel Coordinates to use dc.DrawLineList
        major_x = self.convert_lines(canvas, major_x, 0)
        major_y = self.convert_lines(canvas, major_y, 1)
#        minor_x = self.convert_lines(canvas, minor_y, 0)
#        minor_y = self.convert_lines(canvas, minor_y, 0)

        # Define the pens.
        major_pen = wx.Pen(self.major_color, self.major_lw, self.major_style)
#        minor_pen = wx.Pen(self.minor_color, self.minor_lw, self.minor_style)

        # Draw the lines on the dc.
        dc.DrawLineList(major_x, major_pen)
        dc.DrawLineList(major_y, major_pen)
#        dc.DrawLineList(minor_x, major_pen)
#        dc.DrawLineList(minor_y, major_pen)



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
