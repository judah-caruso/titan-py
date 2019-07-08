"""
    patcher.py

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

import os
import wx
import sys
import time
import toml
import psutil
import shutil
import asyncio
import subprocess

from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
from asyncio.events import get_event_loop


def is_process_running(name):
    for process in psutil.process_iter():
        try:
            if name in process.name():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # ignore any errors
    return False


class TitanPatcherFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(TitanPatcherFrame, self).__init__(style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX, *args, **kwargs)
        self.progress_bar = wx.GenericProgressDialog(message=f"Applying patch...", title="Titan Patcher")
        self.progress_msg = []
        self.patch_is_finished = False
        self.width = 350
        self.height = 80
        self.progress = 0
        self.working_dir = "./"
        self.patch_parent_dir = os.path.join(self.working_dir, "patch")
        self.patch_dir = os.path.join(self.patch_parent_dir, "titan")
        self.patch_zip = os.path.join(self.working_dir, "patch.zip")
        self.config_file = os.path.join(self.working_dir, "titan_games.toml")

        if len(sys.argv) < 3 or sys.argv[1] != "to_titan":
            self.progress_bar.Pulse("Paused...")
            self._error_dialog(title="Incorrect Usage!", msg=f"Titan's patcher is not supposed to be opened manually!")
            return

        self.new_version = sys.argv[2]

        self.pre_check()
        self.start_patching()

    async def _update_progress_bar(self):
        while not self.patch_is_finished:
            log_msg = "Patching files..."
            if len(self.progress_msg) > 0:
                log_msg = self.progress_msg.pop()

            self.progress_bar.Update(self.progress, log_msg)

            await asyncio.sleep(1)

    async def _patch_config(self):
        if not os.path.exists(self.config_file):
            return

        temp_cfg = toml.load(self.config_file)
        temp_cfg["titan_info"]["cfg_version"] = self.new_version

        with open(self.config_file, "w") as cfg_fh:
            toml.dump(temp_cfg, cfg_fh)

    def _error_dialog(self, msg, title="Error"):
        dialog = wx.MessageDialog(self, msg, title)
        dialog.ShowModal()
        sys.exit(-1)
        return

    def pre_check(self):
        self.progress_bar.Pulse("Verifying files...")

        if not os.path.exists(self.patch_parent_dir) or not os.path.exists(self.patch_zip):
            self._error_dialog(msg="Unable to find patch data. Please restart Titan or run it as Administrator and try again.")
            return

        if is_process_running("titan.exe"):
            self._error_dialog(msg="Titan is still running! Please close any other instances of Titan before trying to patch again.")
            return

    async def _finalize_patch(self):
        await asyncio.sleep(5)
        titan_restart = subprocess.Popen([os.path.join(self.working_dir, "titan.exe"), "updated"], cwd=self.working_dir)
        sys.exit(0)

    def start_patching(self):
        self.progress_msg.append("Copying files...")
        StartCoroutine(self._update_progress_bar, self)

        for root, dirs, files in os.walk(self.patch_dir):
            for file in files:
                if ("_adv." in file) or ("_core." in file) or ("siplib." in file):
                    wx_dir = os.path.join(self.patch_dir, "wx")
                    shutil.copy(os.path.join(wx_dir, file), os.path.join(self.working_dir, "wx"))
                else:
                    self.progress += self.progress_bar.GetRange() / len(files)
                    shutil.copy(os.path.join(self.patch_dir, file), self.working_dir)

            for _dir in dirs:
                n_dir = os.path.join(self.working_dir, _dir)
                if not os.path.exists(n_dir):
                    os.mkdir(os.path.join(self.working_dir, _dir))

        self.patch_is_finished = True
        self.progress_bar.Pulse("Cleaning up files...")
        time.sleep(1)

        try:
            if os.path.exists(self.patch_parent_dir):
                shutil.rmtree(self.patch_parent_dir)

            if os.path.exists(self.patch_zip):
                os.remove(self.patch_zip)
        except OSError as err:
            self._error_dialog(msg=f"Titan ran into an unexpected error! Error:\n{err}")

        self.progress_bar.Pulse("Updating configuration...")
        StartCoroutine(self._patch_config, self)

        self.progress_bar.Pulse("Update finished! Restarting Titan...")
        StartCoroutine(self._finalize_patch, self)


def main():
    app = WxAsyncApp()
    frame = TitanPatcherFrame(None, title=f"Titan Patcher")
    app.SetTopWindow(frame)
    loop = get_event_loop()
    loop.run_until_complete(app.MainLoop())


if __name__ == "__main__":
    main()
