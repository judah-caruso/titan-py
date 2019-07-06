"""
    titanentry.py

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
import time
from titan.gui import titaneditmodal as tem


class TitanEntry():
    def __init__(self, title, location="", time_played=0, times_opened=0, pre=[], args=[]):
        self.title = title
        self.location = location
        self.time_played = time_played
        self.times_opened = times_opened
        self.preloads = pre
        self.arguments = args

    def get_time_played(self):
        return time.strftime("%H:%M:%S", time.gmtime(self.time_played))

    def edit(self):
        modal = tem.TitanEditModal(self, None)
        modal.ShowModal()
        modal.Destroy()
