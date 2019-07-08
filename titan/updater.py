"""
    updater.py

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
import re
import sys
import asyncio
import zipfile
import subprocess

from urllib.request import urlopen, urlretrieve
from titan.globals import VERSION, WORKING_DIR


class Updater():
    def __init__(self, parent):
        self.parent = parent

    async def check_for_updates(self):
        try:
            res = urlopen("https://raw.githubusercontent.com/kyoto-shift/titan-py/master/README.md")
        except URLError as err:
            print(f"Unable to retrieve file! Error: {err}")
            return

        raw_file = str(res.read())
        rexpr = re.compile(r".*(v[0-9]{1,}.[0-9]{1,}).*")
        matches = rexpr.match(raw_file)
        if matches is None:
            print("Unable to find version number from readme")
            return

        readme_version = ("%.2f" % float(matches.group(1)[1:]))
        if VERSION != readme_version:
            dialog = wx.MessageDialog(self.parent, f"There's a new update available! Would you like to update now?", "Update Available!", style=wx.YES_NO)

            ok = dialog.ShowModal()
            if ok != wx.ID_YES:
                dialog.Destroy()
                return

            await self._download_update(readme_version)

        await asyncio.sleep(0.5)

    async def _download_update(self, version):
        canonical = version.replace(".", "")
        url = f"https://github.com/kyoto-shift/titan-py/releases/download/v{version}/titan-v{canonical}-win.zip"

        self.parent.SetStatusText("Downloading patch data...")
        urlretrieve(url, os.path.join(WORKING_DIR, "patch.zip"))

        self.parent.SetStatusText("Extracting patch data...")
        with zipfile.ZipFile(os.path.join(WORKING_DIR, "patch.zip"), "r") as zip_fh:
            zip_fh.extractall(os.path.join(WORKING_DIR, f"patch/"))

        self.parent.SetStatusText("Starting patch process! Titan will now close.")
        patcher = subprocess.Popen([os.path.join(WORKING_DIR, "titan_patcher.exe"), "to_titan", version], cwd=WORKING_DIR)
        sys.exit(0)
