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

from __future__ import print_function, division, absolute_import
#from __future__ import unicode_literals
#from docopt import docopt
import wx
from configobj import ConfigObj
import os

__author__ = "Douglas Thor"
__version__ = "v0.1.0"


CONFIG_WARN = ("High", "Low", "Email Address")
CONFIG_CRIT = ("High", "Low", "Email Address")
CONFIG_MISC = ("A", "B", "C")

SECTIONS = (("Warning Limits", CONFIG_WARN),
            ("Critical Limits", CONFIG_CRIT),
            ("Misc. Options", CONFIG_MISC),
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
                           size=(300, 500),
                           )
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        """ Create the UI """
        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # Upon Init, check to see if there's a config file that we can read
        self.read_config_file()

        # TODO: Come up with a better way to add all these options.
        self.box_crit = wx.StaticBox(self, wx.ID_ANY, "Critical Limits")
        self.svbox_crit = wx.StaticBoxSizer(self.box_crit, wx.VERTICAL)
        self.svbox_crit.Add(PreferencesItem(self, 1, "High", ""))
        self.svbox_crit.Add(PreferencesItem(self, 2, "Low", ""))
        self.svbox_crit.Add(PreferencesItem(self, 3, "Email Address", ""))

        self.box_warn = wx.StaticBox(self, wx.ID_ANY, "Warning Limits")
        self.svbox_warn = wx.StaticBoxSizer(self.box_warn, wx.VERTICAL)
        self.svbox_warn.Add(PreferencesItem(self, 1, "High", ""))
        self.svbox_warn.Add(PreferencesItem(self, 2, "Low", ""))
        self.svbox_warn.Add(PreferencesItem(self, 3, "Email Address", ""))

        self.box_misc = wx.StaticBox(self, wx.ID_ANY, "Misc. Options")
        self.svbox_misc = wx.StaticBoxSizer(self.box_misc, wx.VERTICAL)
        self.svbox_misc.Add(PreferencesItem(self, 1, "A", ""))
        self.svbox_misc.Add(PreferencesItem(self, 2, "B", ""))
        self.svbox_misc.Add(PreferencesItem(self, 3, "C", ""))

        self.vbox.Add(self.svbox_crit)
        self.vbox.Add(self.svbox_warn)
        self.vbox.Add(self.svbox_misc)

        self.btn_box = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_apply = wx.Button(self, wx.ID_ANY, label="Apply")
        self.btn_ok = wx.Button(self, wx.ID_ANY, label="OK")
        self.btn_cancel = wx.Button(self, wx.ID_ANY, label="Cancel")
        self.btn_box.Add(self.btn_apply, 0)
        self.btn_box.Add(self.btn_ok, 0)
        self.btn_box.Add(self.btn_cancel, 0)

        self.vbox.Add(self.btn_box)

        self.SetSizer(self.vbox)

        self._bind_events()

    def _bind_events(self):
        """ Bind various events """
        # Buttons
        self.btn_apply.Bind(wx.EVT_BUTTON, self.on_apply)
        self.btn_ok.Bind(wx.EVT_BUTTON, self.on_ok)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)

    def on_apply(self, event):
        """ Actions to perform when the Apply button is pressed """
        print("Apply pressed")

    def on_ok(self, event):
        """ Actions to perform when the OK button is pressed """
        print("OK pressed")
        self.on_close(event)

    def on_cancel(self, event):
        """ Actions to perform when the Cancel button is pressed """
        print("Cancel pressed")
        self.on_close(event)

    def on_close(self, event):
        """ Close the window """
        self.Close()

    def read_config_file(self, fname=None):
        if fname is None:
            fname = "config.ini"
        if not os.path.exists(fname):
            # then we create the config file, using our parameters
            print("Config file not found")
            self.create_config_file(fname)
        else:
            # read from the config file
            print("Config file found!")
            pass
#        config = ConfigObj(fname)

    def create_config_file(self, fname):
        """ Creates the configuration file """
        print("Creating config file")
        config = ConfigObj()
        config.filename = fname
        
        for sect_name, items in SECTIONS:
            config[sect_name] = {}
            for item in items:
                config[sect_name][item] = ""
        config.write()


class PreferencesItem(wx.Panel):
    """ A Preferences Item """
    def __init__(self, parent, wx_id, label, hovertext):
        wx.Panel.__init__(self, parent)
        self.label = label
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.text = wx.StaticText(self,
                                  label=self.label,
                                  size=(120, -1),
                                  )
        self.edit = wx.TextCtrl(self, wx.ID_ANY, "0")

        self.hbox.Add(self.text, 0, wx.EXPAND)
        self.hbox.Add(self.edit, 0, wx.EXPAND)

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
            pref_dialog.Destroy()

        def OnQuit(self, event):
            self.Destroy()

    app = wx.App()
    frame = ExampleFrame()
#    frame.Show()
    frame.Destroy()
    app.MainLoop()


if __name__ == "__main__":
    main()
