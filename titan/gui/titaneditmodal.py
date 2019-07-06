"""
    titandeditmodal.py

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
"""

import os
import wx
from wx.adv import EditableListBox


class TitanEditModal(wx.Dialog):
    def __init__(self, entry, *args, **kwargs):
        super(TitanEditModal, self).__init__(*args, **kwargs)
        self.entry = entry
        self.hasEdited = False

        self.init_modal()
        self.SetSize((350, 450))
        self.SetTitle(f"Editing: {self.entry.title}")

    def init_modal(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Information box
        panel = wx.Panel(self)
        box_info = wx.StaticBox(panel, label="Information")
        box_info_sizer = wx.StaticBoxSizer(box_info, orient=wx.VERTICAL)

        self.textbox_title = wx.TextCtrl(panel, value=self.entry.title, size=(200, -1))
        self.textbox_location = wx.TextCtrl(panel, value=self.entry.location, size=(200, -1))

        title_box = wx.BoxSizer(wx.HORIZONTAL)
        title_box.Add(wx.StaticText(panel, label="Title:", size=(60, -1)), flag=wx.EXPAND | wx.TOP | wx.RIGHT, border=5)
        title_box.Add(self.textbox_title, flag=wx.RIGHT | wx.EXPAND, border=5)

        location_box = wx.BoxSizer(wx.HORIZONTAL)
        location_box.Add(wx.StaticText(panel, label="Location:", size=(60, -1)), flag=wx.EXPAND | wx.TOP | wx.RIGHT, border=5)
        location_box.Add(self.textbox_location, flag=wx.RIGHT, border=5)

        location_btn = wx.Button(panel, wx.ID_ANY, "...", size=(60, 0))
        location_box.Add(location_btn, flag=wx.EXPAND | wx.TOP | wx.RIGHT)

        box_info_sizer.Add(title_box)
        box_info_sizer.Add((-1, 5))
        box_info_sizer.Add(location_box)

        panel.SetSizer(box_info_sizer)

        # Argument editor
        arguments = wx.Panel(self)
        arg_vbox = wx.BoxSizer(wx.VERTICAL)
        box_arg = wx.StaticBox(arguments, label="Arguments (Command Line)")
        box_arg_sizer = wx.StaticBoxSizer(box_arg, orient=wx.HORIZONTAL)

        self.arg_listbox = EditableListBox(arguments, size=(-1, 80))
        if len(self.entry.arguments) > 0:
            self.arg_listbox.SetStrings(self.entry.arguments)

        box_arg_sizer.Add(self.arg_listbox, wx.ID_ANY, flag=wx.EXPAND | wx.ALL, border=5)
        arguments.SetSizer(box_arg_sizer)

        # Process editor
        editor = wx.Panel(self)
        proc_vbox = wx.BoxSizer(wx.VERTICAL)
        box_proc = wx.StaticBox(editor, label="External Programs/Entries")
        box_proc_sizer = wx.StaticBoxSizer(box_proc, orient=wx.HORIZONTAL)

        self.proc_listbox = EditableListBox(editor, size=(-1, -1))
        if len(self.entry.preloads) > 0:
            self.proc_listbox.SetStrings(self.entry.preloads)

        box_proc_sizer.Add(self.proc_listbox, wx.ID_ANY, flag=wx.EXPAND | wx.ALL, border=5)
        editor.SetSizer(box_proc_sizer)

        # Buttons
        button_save = wx.Button(self, label="Save")
        button_cancel = wx.Button(self, label="Cancel")

        hbox.Add(button_save)
        hbox.Add(button_cancel, flag=wx.RIGHT, border=5)

        vbox.Add(panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(arguments, proportion=2, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(editor, proportion=3, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        # Textbox binds
        self.textbox_title.Bind(wx.EVT_TEXT, self.OnEdit)
        self.textbox_location.Bind(wx.EVT_TEXT, self.OnEdit)

        # Listbox binds
        self.proc_listbox.Bind(wx.EVT_LIST_INSERT_ITEM, self.OnEdit)
        self.proc_listbox.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnEdit)
        self.proc_listbox.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnEdit)
        self.arg_listbox.Bind(wx.EVT_LIST_INSERT_ITEM, self.OnEdit)
        self.arg_listbox.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnEdit)
        self.arg_listbox.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnEdit)

        # Button binds
        location_btn.Bind(wx.EVT_BUTTON, self.OnOpenDir)
        button_save.Bind(wx.EVT_BUTTON, self.OnSave)
        button_cancel.Bind(wx.EVT_BUTTON, self.OnClose)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnEdit(self, event):
        # wx.PostEvent(self.GetEventHandler(), event)
        self.hasEdited = True

    def OnOpenDir(self, event):
        default_dir = os.path.dirname(os.path.normpath(self.textbox_location.GetValue()))

        with wx.FileDialog(self, "Choose executable", defaultDir=default_dir, wildcard="Excecutables (*.exe; *.ink; *.url)|*.exe;*.ink;*.url", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_CANCEL:
                return

            exe_path = os.path.normpath(dialog.GetPath())
            self.textbox_location.SetValue(exe_path)

    def OnSave(self, event):
        cur_title = self.textbox_title.GetValue()
        cur_location = self.textbox_location.GetValue()
        cur_preloads = self.proc_listbox.GetStrings()
        cur_arguments = self.arg_listbox.GetStrings()

        if self.entry.title != cur_title:
            self.entry.title = cur_title

        if self.entry.location != cur_location:
            self.entry.location = cur_location

        if len(cur_arguments) > 0:
            self.entry.arguments = cur_arguments
        else:
            self.entry.arguments = []

        if len(cur_preloads) > 0:
            self.entry.preloads = cur_preloads
        else:
            self.entry.preloads = []

        self.hasEdited = False
        self.OnClose(event)

    def OnClose(self, event):
        if self.hasEdited:
            dialog = wx.MessageDialog(self, f"Are you sure you want to cancel? You have unsaved changes.", "Confirmation", style=wx.YES_NO)
            ok = dialog.ShowModal()
            if ok == wx.ID_YES:
                self.Destroy()
            return

        self.Destroy()
