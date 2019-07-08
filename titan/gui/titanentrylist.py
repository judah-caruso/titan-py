"""
    titanentrylist.py

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
import wx.lib.mixins.listctrl as listctrlmixins


class TitanEntryList(wx.ListCtrl, listctrlmixins.ListCtrlAutoWidthMixin):
    def __init__(self, parent, *args, **kwargs):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        listctrlmixins.ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(0)
        self.InsertColumn(0, "Title", width=110)
        self.InsertColumn(1, "Time Played", width=100)
        self.InsertColumn(2, "Times Opened", width=100)
        self.entries = []

    def get_entry(self, name):
        for entry in self.entries:
            if name == entry.title:
                return entry

        return None

    def add_entry(self, entry):
        self.entries.append(entry)
        self.Append((entry.title, entry.get_time_played(), entry.times_opened))

    def refresh_entries(self):
        i = 0
        for entry in self.entries:
            self.SetItem(i, 0, str(entry.title))
            self.SetItem(i, 1, str(entry.get_time_played()))
            self.SetItem(i, 2, str(entry.times_opened))
            i += 1


    def edit_entry(self, entry):
        self.entries[entry].edit()
        ent = self.entries[entry]
        self.SetItem(entry, 0, str(ent.title))
        self.SetItem(entry, 1, str(ent.get_time_played()))
        self.SetItem(entry, 2, str(ent.times_opened))

    def delete_entry(self, event):
        selection = self.GetFocusedItem()
        if selection != -1:
            dialog = wx.MessageDialog(self, f"Are you sure you want to delete '{self.entries[selection].title}'? All stats will be removed.\nThis cannot be undone.", "Confirmation", style=wx.YES_NO)
            ok = dialog.ShowModal()

            if ok == wx.ID_YES:
                del self.entries[selection]
                self.DeleteItem(selection)
