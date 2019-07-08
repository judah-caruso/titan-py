"""
    titan_gui.py

    Copyright (C) 2019  Judah Caruso Rodriguez

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    See NOTICE.txt for third-party license information.
"""

import wx
import sys
import time
import asyncio
import datetime

from titan import runner
from titan import updater
from titan.globals import CONFIG_FILE, VERSION, NAME, NAME_LOW
from titan.gui import utils
from titan.gui import filehandler
from titan.gui.titanentry import TitanEntry
from titan.gui.titanentrylist import TitanEntryList

from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
from asyncio.events import get_event_loop


class TitanFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(TitanFrame, self).__init__(*args, **kwargs)
        self.SetIcon(wx.Icon("titan_logo.ico"))
        self.SetMinSize((500, 250))
        self.entry_is_running = False

        update_manager = updater.Updater(self)
        StartCoroutine(update_manager.check_for_updates, self)

        self.init_gui()

    def init_gui(self):
        panel = wx.Panel(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.entrylist = TitanEntryList(panel)

        filehandler.init_files()
        self.GAMES = filehandler.load_file(CONFIG_FILE)

        for game in self.GAMES:
            if game == f"{NAME_LOW}_info":
                continue

            title = game
            loc = self.GAMES[game]["location"]
            args = self.GAMES[game]["arguments"]
            preloads = self.GAMES[game]["preloads"]
            time_played = self.GAMES[game]["time_played"]
            times_opened = self.GAMES[game]["times_opened"]

            self.entrylist.add_entry(TitanEntry(
                    title,
                    loc,
                    time_played,
                    times_opened,
                    preloads,
                    args))

        hbox.Add(self.entrylist, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)

        btn_size = (90, 30)
        buttons_panel = wx.Panel(panel)
        self.btn_start = wx.Button(buttons_panel, wx.ID_ANY, "Start", size=btn_size)
        self.btn_add = wx.Button(buttons_panel, wx.ID_ANY, "Add", size=btn_size)
        self.btn_edit = wx.Button(buttons_panel, wx.ID_ANY, "Edit", size=btn_size)
        self.btn_delete = wx.Button(buttons_panel, wx.ID_ANY, "Delete", size=btn_size)

        self.Bind(wx.EVT_BUTTON, self.OnStart, id=self.btn_start.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnAdd, id=self.btn_add.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnEdit, id=self.btn_edit.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=self.btn_delete.GetId())
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)

        # disable unusable buttons on start
        self.DisableEditButtons()

        vbox.Add((-1, 20))
        vbox.Add(self.btn_start)
        vbox.Add((-1, 10))
        vbox.Add(self.btn_add, 0, wx.TOP, 5)
        vbox.Add(self.btn_edit, 0, wx.TOP, 5)
        vbox.Add(self.btn_delete, 0, wx.TOP, 5)

        buttons_panel.SetSizer(vbox)
        hbox.Add(buttons_panel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)

        self.Centre()
        self.CreateStatusBar()

        if len(sys.argv) >= 2 and sys.argv[1] == "updated":
            self.SetStatusText(f"{NAME} updated successfully!")
        else:
            self.SetStatusText("Initialized successfully!")

    def _save_data(self):
        if len(self.entrylist.entries) <= 0:
            filehandler.delete_file(CONFIG_FILE)
            filehandler.init_files()

        filehandler.save_entries(self.entrylist.entries)

    def EnableEditButtons(self):
        self.btn_start.Enable()
        self.btn_edit.Enable()
        self.btn_delete.Enable()

    def DisableEditButtons(self):
        self.btn_start.Disable()
        self.btn_edit.Disable()
        self.btn_delete.Disable()

    def OnSelect(self, event):
        selection = self.entrylist.GetFocusedItem()
        if selection != -1:
            self.EnableEditButtons()

    async def _disable_if_running(self):
        while True:
            if self.entry_runner.running:
                self.btn_start.Disable()
            else:
                self.btn_start.Enable()
                break
            await asyncio.sleep(1)

    def OnStart(self, event):
        selection = self.entrylist.GetFocusedItem()
        entry = self.entrylist.entries[selection]

        if selection == -1:
            utils.warning_dialog(f"Unable to load selection! Does it exist?")

        self.SetStatusText(f"Starting {entry.title}...")
        self.entry_is_running = True

        self.entry_runner = runner.Runner(self, entry)
        self.entry_runner._log(f"\n[{NAME} Run - {datetime.datetime.now()}]", False)
        self.entry_runner.run()

    def OnAdd(self, event):
        self.entrylist.add_entry(TitanEntry("New Game"))
        newest_index = len(self.entrylist.entries) - 1
        self.entrylist.edit_entry(newest_index)
        self._save_data()

    def OnEdit(self, event):
        selection = self.entrylist.GetFocusedItem()
        if selection != -1:
            self.entrylist.edit_entry(selection)
            self.EnableEditButtons()
            self._save_data()

    def OnDelete(self, event):
        self.entrylist.delete_entry(event)

        if len(self.entrylist.entries) <= 0:
            self.DisableEditButtons()

        self._save_data()

    def OnExit(self, event):
        self._save_data()
        self.Close(True)

    def OnAbout(self, event):
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)


def main():
    app = WxAsyncApp()
    frame = TitanFrame(None, title=f"{NAME} {VERSION}")
    frame.Show()
    app.SetTopWindow(frame)
    loop = get_event_loop()
    loop.run_until_complete(app.MainLoop())


if __name__ == "__main__":
    main()
