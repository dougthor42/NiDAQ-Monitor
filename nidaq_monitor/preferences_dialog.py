# -*- coding: utf-8 -*-
"""
@name:          new_program.py
@vers:          0.1.0
@author:        dthor
@created:       Tue Dec 30 12:46:46 2014
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
from configobj import ConfigObj
import os

__author__ = "Douglas Thor"
__version__ = "v0.1.0"


# Section, Item, Hovertext, Default Value
# Note that this is in display order
OPTIONS = (("Warning Limits", "High", "", 30),
           ("Warning Limits", "Low", "", 10),
           ("Warning Limits", "Email Address", "", ""),
           ("Critical Limits", "High", "", 50),
           ("Critical Limits", "Low", "", 40),
           ("Critical Limits", "Email Address", "", ""),
           ("Misc. Options", "Read Frequency (s)", "", 10),
           ("Misc. Options", "Data Path", "", ""),
           ("Misc. Options", "Display Length (hr)", "", 30),
           ("Misc. Options", "Moving Average Length (pts)", "", 60),
           ("Misc. Options", "Email Interval (s)", "", 3600),
           ("Misc. Options", "Calculate Maximum over X points", "", 60),
           )


class MonitorPreferences(wx.Dialog):
    """ The main panel for the Monitor Preferences """
    def __init__(self,
                 parent
                 ):
        wx.Dialog.__init__(self,
                           parent,
                           wx.ID_ANY,
                           title="Preferences",
                           size=(500, 500),
                           )
        self.parent = parent
        self.controls = {}
        self.init_ui()

    def init_ui(self):
        """ Create the UI """
        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        prev_sect_name = ""
        for sect_name, item, hovertext, _ in OPTIONS:
            # I don't know if I like this, but it works.
            if prev_sect_name != sect_name:
                self.controls[sect_name] = {}
                prev_sect_name = sect_name
                sbox = wx.StaticBox(self, wx.ID_ANY, sect_name)
                svbox = wx.StaticBoxSizer(sbox, wx.VERTICAL)
                self.vbox.Add(svbox)
            control = PreferencesItem(self, wx.ID_ANY, item)
            svbox.Add(control)
            self.controls[sect_name][item] = control

        self.read_config_file()

        self.btn_box = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_apply = wx.Button(self, wx.ID_APPLY)
        self.btn_ok = wx.Button(self, wx.ID_OK)
        self.btn_cancel = wx.Button(self, wx.ID_CANCEL)
        self.btn_box.Add((20, -1), 1, wx.EXPAND)
        self.btn_box.Add(self.btn_apply, 0)
        self.btn_box.Add(self.btn_ok, 0)
        self.btn_box.Add(self.btn_cancel, 0)

        self.vbox.Add(self.btn_box)

        self.SetSizer(self.vbox)

        self._bind_events()

    def _bind_events(self):
        """ Bind various events """
        # Buttons
        # Since I use the wx.ID_OK (and other) ids for the buttons, they
        # are automatically bound to various events. All I need to do is
        # override those events. However, it seems that both ID_OK and
        # ID_CANCEL just call the EVT_CLOSE event, so I guess I need to
        # override them anyway. I also don't know what ID_APPLY calls.
        self.btn_apply.Bind(wx.EVT_BUTTON, self.on_apply)
        self.btn_ok.Bind(wx.EVT_BUTTON, self.on_ok)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)

    def on_apply(self, event):
        """ Actions to perform when the Apply button is pressed """
        print("Apply pressed")
        self.update_config_file("config.ini")

    def on_ok(self, event):
        """ Actions to perform when the OK button is pressed """
        print("OK pressed")
        self.update_config_file("config.ini")
        self.on_close(event)

    def on_cancel(self, event):
        """ Actions to perform when the Cancel button is pressed """
        print("Cancel pressed")
        self.on_close(event)

    def on_close(self, event):
        """ Close the window """
        print("close called")
        self.Destroy()

    def read_config_file(self, fname=None):
        if fname is None:
            fname = "config.ini"
        if not os.path.exists(fname):
            # then we create the config file, using our parameters
            print("Config file not found")
            self.update_config_file(fname)
        else:
            # read from the config file
            print("Config file found!")
            config = ConfigObj(fname)
            for sect_name, item, hovertext, _ in OPTIONS:
                val = config[sect_name][item]
                self.controls[sect_name][item].ctrl.SetValue(val)

    def create_config_file(self, fname):
        """ Creates the configuration file """
        print("Creating config file")
        config = ConfigObj()
        config.filename = fname

        prev_sect_name = ""
        for sect_name, item, _, default in OPTIONS:
            # I don't know if I like this, but it works.
            if prev_sect_name != sect_name:
                config[sect_name] = {}
                prev_sect_name = sect_name
            config[sect_name][item] = default
            self.controls[sect_name][item].ctrl.SetValue(str(default))
        config.write()

    def update_config_file(self, fname):
        """ Update the configuration file with current control values """
        print("Updating config file")
        config = ConfigObj()
        config.filename = fname

        prev_sect_name = ""
        for sect_name, item, _, _ in OPTIONS:
            # I don't know if I like this, but it works.
            if prev_sect_name != sect_name:
                config[sect_name] = {}
                prev_sect_name = sect_name
            val = self.controls[sect_name][item].ctrl.GetValue()
            config[sect_name][item] = val
        config.write()


class PreferencesItem(wx.Panel):
    """ A Preferences Item """
    def __init__(self, parent, wx_id, label, hovertext=""):
        wx.Panel.__init__(self, parent)
        self.label = label
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox.Add((30, -1), 0, wx.EXPAND)

        self.lbl = wx.StaticText(self,
                                 label=self.label,
                                 size=(220, -1),
                                 )
        self.ctrl = wx.TextCtrl(self, wx.ID_ANY, "0", size=(300, -1))

        self.hbox.Add(self.lbl, 0, wx.EXPAND)
        self.hbox.Add(self.ctrl, 0, wx.EXPAND)

        self.SetSizer(self.hbox)


def main():
    """ Main Code """
#    docopt(__doc__, version=__version__)
    class ExampleFrame(wx.Frame):
        """ Base Frame """
        def __init__(self):
            wx.Frame.__init__(self,
                              None,                         # Window Parent
                              wx.ID_ANY,                    # id
                              )

            self.Bind(wx.EVT_CLOSE, self.OnQuit)

            # Create the wafer map
            pref_dialog = MonitorPreferences(self)
            pref_dialog.ShowModal()
#            pref_dialog.Destroy()

        def OnQuit(self, event):
            self.Destroy()

    app = wx.App()
    frame = ExampleFrame()
#    frame.Show()
    frame.Destroy()
    app.MainLoop()


if __name__ == "__main__":
    main()
