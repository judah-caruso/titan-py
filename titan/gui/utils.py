"""
    utils.py

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

import wx
import os
import sys


def warning_dialog(msg):
    dialog = wx.MessageDialog(None, msg, "Warning")
    ok = dialog.ShowModal()
    if ok == wx.ID_OK:
        dialog.Destroy()


def error_dialog(msg):
    dialog = wx.MessageDialog(None, msg, "Error")
    ok = dialog.ShowModal()
    if ok == wx.ID_OK:
        dialog.Destroy()
        sys.exit(-1)
