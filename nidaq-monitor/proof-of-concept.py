# -*- coding: utf-8 -*-
"""
@name:          monitor.py
@vers:          0.1.0
@author:        dthor
@created:       Fri Sep 26 15:57:32 2014
@descr:         A new file

Usage:
    monitor.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.
"""

from __future__ import (print_function, division,
                        absolute_import, unicode_literals)
from docopt import docopt
import ctypes
import random
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

# Try loading the NIDAQ nicaiu DLL
global nidaq
try:
    dll_load_error = False
    nidaq = ctypes.windll.nicaiu
except WindowsError as _e:
    print("NIDAQ DLL not loaded!")
    nidaq = None
    dll_load_error = True

__author__ = "Douglas Thor"
__version__ = "v0.1.0"

# define c variable types:
int32 = ctypes.c_long
uint32 = ctypes.c_ulong
uint64 = ctypes.c_uint64
float32 = ctypes.c_float
float64 = ctypes.c_double
task_handle = ctypes.c_ulong(0)

#DAQmx_Val_Voltage = ctypes.c_long(10322)        # 10322 bad?
DAQmx_Val_Voltage = ctypes.c_long(10348)
DAQmx_Val_RSE = ctypes.c_long(10083)


def chk(err):
    """
    Error checking for the nidaq DLL calls.

    Raises error if the return value of the call is less than 0.
    Prints warning if the return value of the call is greater than 0.
    """
    if err != 0:
        buf_size = 200
        buf = ctypes.create_string_buffer("\000", buf_size)
        nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
        if err > 0:
            err_str = "nidaq call passed with warning {}: {}"
            print(err_str.format(err, repr(buf.value)))
        else:
            err_str = "nidaq call failed with error {}: {}"
            raise RuntimeError(err_str.format(err, repr(buf.value)))


def setup_meas():
    """ Set up the measurement conditions """
    if dll_load_error:
        return -1

    print(nidaq)
    nidaq.DAQmxCreateTask
    nidaq.DAQmxCreateAIVoltageChan
    nidaq.DAQmxStartTask
    nidaq.DAQmxGetDevAIPhysicalChans
    nidaq.DAQmxGetDevSerialNum

    chk(nidaq.DAQmxResetDevice(ctypes.c_char_p("Dev1")))
    chk(nidaq.DAQmxCreateTask(ctypes.c_char_p(str(random.randint(0, 100000))),
                              ctypes.byref(task_handle)))

    try:
        chk(nidaq.DAQmxCreateAIVoltageChan(
            task_handle,                    # handle
            ctypes.c_char_p("Dev1/ai0"),    # physical chan name
            ctypes.c_char_p(""),            # custom chan name
            DAQmx_Val_RSE,                  # input config
            float64(-10),                   # min value
            float64(10),                    # max value
            DAQmx_Val_Voltage,              # unit: voltage
            None,                           # scale name
            )
            )
    except RuntimeError as _e:
        print("fail: {}".format(_e))

    chk(nidaq.DAQmxStartTask(task_handle))
    return task_handle


def teardown_meas(task_handle):
    """ Stop and Clear DAQmx tasks when done """
    if dll_load_error:
        return

    chk(nidaq.DAQmxStopTask(task_handle))
    chk(nidaq.DAQmxClearTask(task_handle))


def read_point(task_handle):
    """ Read a single data point """
    if dll_load_error:
        return random.gauss(5, 1)

    data = float64(0)
    try:
        chk(nidaq.DAQmxReadAnalogScalarF64(
            task_handle,               # handle
            float64(0.01),             # timeout in seconds
            ctypes.byref(data),        # measured value
            None,                      # Reserved, pass NULL
            ))
    except RuntimeError as _e:
        print("fail: {}".format(_e))
#    print("{}: {}".format("Point", float(data.value)))
    return data.value


def main():
    """ Main Code """
    docopt(__doc__, version=__version__)

    app = QtGui.QApplication([])
    win = pg.GraphicsWindow(title="Basic plotting examples")
    win.resize(1000, 600)
    win.setWindowTitle('pyqtgraph example: Plotting')
    pg.setConfigOptions(antialias=True)

    max_history = 500

    global listplot
    listplot = win.addPlot(title="Updating plot")

    global curve
    curve = listplot.plot(pen='y')

    global data
    data = np.empty(max_history, dtype=np.float)
    data[:] = np.NaN

    global time_data
    time_data = np.zeros(max_history, dtype=np.float)

    global ptr
    ptr = 0

    global _i
    _i = 0

    task = setup_meas()

    def update():
        global curve, data, ptr, listplot, _i, time_data, hist
        data = np.roll(data, -1)
        data[-1] = read_point(task)
        time_data = np.roll(time_data, -1)
        time_data[-1] = time_data[-2] + 1
        plot_data = np.vstack((time_data, data))
        curve.setData(plot_data.T)
#        max_pts = 100
#        if len(data) > max_pts:
#            listplot.setXRange(len(data) - max_pts, len(data), update=False)
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(20)

    task = setup_meas()

    QtGui.QApplication.instance().exec_()
    teardown_meas(task)
    print()


if __name__ == "__main__":
    main()
