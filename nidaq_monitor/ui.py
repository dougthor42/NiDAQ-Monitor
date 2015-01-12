# -*- coding: utf-8 -*-
"""
@name:          new_program.py
@vers:          0.1.0
@author:        dthor
@created:       Tue Dec 30 11:56:58 2014
@descr:         A new file

Usage:
    new_program.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.
"""

from __future__ import print_function, division
#from __future__ import unicode_literals
#from docopt import docopt
import wx
import preferences_dialog as prefs
import plot

__author__ = "Douglas Thor"
__version__ = "v0.1.0"


class MonitorApp(object):
    """ The Application """
    def __init__(self,
                 ):
        self.app = wx.App()
        self.frame = MonitorFrame()
        self.frame.Show()
        self.app.MainLoop()


class MonitorFrame(wx.Frame):
    """ This is the main frame of the monitor application """
    def __init__(self,
                 ):
        wx.Frame.__init__(self,
                          None,
                          wx.ID_ANY,
                          title="Monitor",
                          size=(640, 480),
                          )

        self.taskbar_icon = MonitorTaskBarIcon(self)

        self.init_ui()

    def init_ui(self,):
        """ Create the UI elements """
        # Create menu bar
        self.menu_bar = wx.MenuBar()

        self._create_menus()
        self._create_menu_items()
        self._add_menu_items()
        self._add_menus()
        self._bind_events()

        # Set Default Menu States
        self.me_run.Check(True)

        # Set the MenuBar and create a status bar (easy thanks to wx.Frame)
        self.SetMenuBar(self.menu_bar)
        self.CreateStatusBar()

        # Add our Main Panel
        self.panel = MonitorPanel(self)

    def _create_menus(self):
        """ Create each menu for the menu bar """
        self.mfile = wx.Menu()
        self.medit = wx.Menu()
        self.mview = wx.Menu()
        self.mopts = wx.Menu()

    def _create_menu_items(self):
        """ Create each item for each menu """
        ### Menu: File (mf_) ###
        self.mf_close = wx.MenuItem(self.mfile,
                                    wx.ID_ANY,
                                    "&Close Window",
                                    "Minimize to the system tray",
                                    )

        self.mf_exit = wx.MenuItem(self.mfile,
                                   wx.ID_ANY,
                                   "&Exit\tCtrl+Q",
                                   "Exit the application",
                                   )

        ### Menu: Edit (me_) ###
        self.me_redraw = wx.MenuItem(self.medit,
                                     wx.ID_ANY,
                                     "&Redraw",
                                     "Force Redraw",
                                     )

        self.me_pref = wx.MenuItem(self.medit,
                                   wx.ID_ANY,
                                   "&Preferences",
                                   "Edit various program parameters",
                                   )

        self.me_run = wx.MenuItem(self.medit,
                                  wx.ID_ANY,
                                  "&Run\tR",
                                  "Start monitoring",
                                  kind=wx.ITEM_CHECK,
                                  )

        ### Menu: View (mv_) ###
        self.mv_zoomfit = wx.MenuItem(self.mview,
                                      wx.ID_ANY,
                                      "Zoom &Fit\tHome",
                                      "Zoom to fit",
                                      )

        # Menu: Options (mo_) ###
        limits_sb_text = "Edit the upper and lower warning and critical limits"
        self.mo_limits = wx.MenuItem(self.mopts,
                                     wx.ID_ANY,
                                     "&Limits",
                                     limits_sb_text,
                                     )
        self.mo_emails = wx.MenuItem(self.mopts,
                                     wx.ID_ANY,
                                     "Email &Addresses",
                                     "Edit the email recipient addresses",
                                     )

        self.mo_update_int = wx.MenuItem(self.mopts,
                                         wx.ID_ANY,
                                         "&Read Interval",
                                         "Set the Read interval",
                                         )

    def _add_menu_items(self):
        """ Appends MenuItems to each menu """
        self.mfile.AppendItem(self.mf_close)
        self.mfile.AppendItem(self.mf_exit)

        self.medit.AppendItem(self.me_redraw)
        self.medit.AppendItem(self.me_pref)
        self.medit.AppendSeparator()
        self.medit.AppendItem(self.me_run)

        self.mview.AppendItem(self.mv_zoomfit)
        self.mview.AppendSeparator()

        self.mopts.AppendItem(self.mo_limits)
        self.mopts.AppendItem(self.mo_emails)

    def _add_menus(self):
        """ Appends each menu to the menu bar """
        self.menu_bar.Append(self.mfile, "&File")
        self.menu_bar.Append(self.medit, "&Edit")
        self.menu_bar.Append(self.mview, "&View")
#        self.menu_bar.Append(self.mopts, "&Options")

    def _bind_events(self):
        """ Binds events """
        # Global Events
        self.Bind(wx.EVT_ICONIZE, self.on_minimize)
        self.Bind(wx.EVT_CLOSE, self.on_close_to_tray)

        # File Menu Events
        self.Bind(wx.EVT_MENU, self.on_quit, self.mf_exit)
        self.Bind(wx.EVT_MENU, self.on_close_to_tray, self.mf_close)

        # Edit Menu Events
        self.Bind(wx.EVT_MENU, self.on_pref, self.me_pref)
        self.Bind(wx.EVT_MENU, self.on_run, self.me_run)

        # View Menu Events
#        self.Bind(wx.EVT_MENU, self.zoom_fit, self.mv_zoomfit)

        # If I define an ID to the menu item, then I can use that instead of
        #   and event source:
        #self.mo_test = wx.MenuItem(self.mopts, 402, "&Test", "Nothing")
        #self.Bind(wx.EVT_MENU, self.zoom_fit, id=402)

    def on_quit(self, event):
        """
        Remove the taskbar icon, destroy it, and then close the window.
        """
        self.taskbar_icon.RemoveIcon()
        self.taskbar_icon.Destroy()
        self.Destroy()

    def on_run(self, event):
        """
        Start or stop monitoring
        """
        self.panel.graph.toggle_run()

    def on_minimize(self, event):
        """ Minimize Application """
#        self.Hide()
        pass

    def on_close_to_tray(self, event):
        """ Minimize to the system tray """
        self.Hide()

    def on_pref(self, event):
        """ """
        print("clicked!")
        pref_dialog = prefs.MonitorPreferences(self)
        pref_dialog.ShowModal()
        pref_dialog.Destroy()


class MonitorTaskBarIcon(wx.TaskBarIcon):
    """ Stuff """

    def __init__(self, parent):
        """ The task bar icon for the monitor """
        wx.TaskBarIcon.__init__(self)
        self.parent = parent

        img = wx.Image("24x24.png", wx.BITMAP_TYPE_ANY)
        bmp = wx.BitmapFromImage(img)
        self.icon = wx.EmptyIcon()
        self.icon.CopyFromBitmap(bmp)

        self.SetIcon(self.icon, "Monitor")
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_taskbar_left_click)

#    def OnTaskBarActivate(self, event):
#        """ Override the default OnTaskBarActivate method """
#        pass
#
#    def OnTaskBarClose(self, event):
#        """
#        Destroy the taskbar icon and frame from the taskbar icon itself
#        """
#        self.parent.Close()

    def on_taskbar_left_click(self, event):
        """
        Create the right-click menu
        """
        self.parent.Show()
        self.parent.Restore()


class MonitorPanel(wx.Panel):
    """
    Main Panel of the NiDAQ Monitor.

    Contains... well I haven't decided yet
    """
    def __init__(self,
                 parent,
                 ):
        """ """
        wx.Panel.__init__(self, parent)
        self.init_ui()

    def init_ui(self):
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.graph = plot.ScrollingListPlot(self,
                                            )
        self.hbox.Add(self.graph, 1, wx.EXPAND)

        self.SetSizer(self.hbox)


def main():
    """ Main Code """
#    docopt(__doc__, version=__version__)
    MonitorApp()


if __name__ == "__main__":
    main()
