"""
    runner.py

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
import re
import wx
import sys
import time
import asyncio
import datetime
import subprocess

from titan.gui import utils
from titan.globals import CONFIG_FILE, LOG_FILE, NAME

from wxasync import StartCoroutine


class Runner():
    """
    """
    def __init__(self, window, entry):
        self.debug_log = []
        self.already_wrote_log = False
        self.window = window
        self.entry = entry
        self.is_first = True
        self.initial_entry = entry
        self.initial_call = None
        self.initial_ret = None
        self.queued_entries = []
        self.run_log = []
        self.running = False
        self.time_start = 0
        self.time_end = 0

    def _write_debug(self):
        with open(LOG_FILE, "a") as fh:
            for msg in self.debug_log:
                fh.write(msg)

    def _log(self, msg, timestamp=True):
        if timestamp:
            current_time = datetime.datetime.now()
            self.debug_log.append(f"[{current_time}] {msg}\n")
        else:
            self.debug_log.append(f"{msg}\n")

    def _start_timer(self):
        self.running = True
        self.time_start = time.perf_counter()
        self._log("Timer has been started.")

    def _end_timer(self):
        self.time_end = time.perf_counter()
        self._log("Timer has been stopped.")
        self.running = False

    def _preload_is_entry(self, preload):
        # format: ent[game_name], ENT["Game Name"]
        rexpr = re.compile(r"^(ent|ENT).*\[(.*)\]")
        stripped = preload.strip()
        matches = rexpr.match(stripped)

        if matches is None:
            return None

        # return name of entry
        return matches.group(2).strip()

    def _push_status(self, msg):
        self.window.SetStatusText(msg)

    def get_duration(self):
        return self.time_end - self.time_start

    def get_duration_as_time(self):
        return time.strftime("%H:%M:%S", time.gmtime(self.get_duration()))

    def save_game_data(self):
        self._log(f"Changed playtime of '{self.initial_entry.title}' from {self.initial_entry.time_played} to {self.initial_entry.time_played + self.get_duration()}")
        self.initial_entry.time_played += self.get_duration()
        self.initial_entry.times_opened += 1

    def run_preload(self, preload):
        self._log(f"Starting preload '{preload}'...")
        if preload in self.run_log:
            self._push_status(f"'{os.path.basename(preload)}' has already been called, {self.entry.title} tried to call it again. Skipping...")
            return

        self.run_log.append(preload)
        try:
            extproc = subprocess.Popen([preload], cwd=os.path.dirname(preload))
            self._log(f"Preload has been started.")
            return extproc
        except OSError as err:
            self._log(f"Fatal error while creating process for preload '{preload}'! Error:\n{err}")
            self._write_debug()

    def run_entry(self):
        self._log(f"Creating process for entry '{self.entry.title}'...")
        try:
            _cwd = os.path.dirname(self.entry.location)
            proc = subprocess.Popen([self.entry.location, *self.entry.arguments], stdout=subprocess.PIPE, cwd=_cwd, universal_newlines=True)
            self._log(f"Process has been started.")
            return proc
        except OSError as err:
            self._log(f"Fatal error while creating process for entry '{self.entry.title}'! Error:\n{err}")
            self._write_debug()
            utils.warning_dialog(f"Unable to start entry '{self.entry.title}', skipping! It may require {NAME} to be ran as Administrator.\nMore details in '{LOG_FILE}'.")

    async def _check_process(self):
        while self.running:
            if self.initial_call.poll() is not None:
                break
            cur_duration = time.strftime("%H:%M:%S", time.gmtime(time.perf_counter() - self.time_start))
            self.window.SetStatusText(f"{self.initial_entry.title}: {cur_duration}")
            await asyncio.sleep(0.5)

        self.running = False
        self._end_timer()
        self.save_game_data()
        self.window.entrylist.refresh_entries()

        if self.already_wrote_log is False:
            self._write_debug()

        self.window.SetStatusText(f"Entry '{self.initial_entry.title}' ran for {self.get_duration_as_time()}")

    def run(self):
        self._log(f"Starting entry '{self.entry.title}'...")

        if self.entry.location in self.run_log:
            self.window.SetStatusText(f"Entry '{self.entry.title}' was already ran! Skipping...")
            return

        self.run_log.append(self.entry.location)

        if len(self.entry.preloads) > 0:
            for preload in self.entry.preloads:
                sub_entry = self._preload_is_entry(preload)

                if sub_entry is None:   # load regular preload
                    self.run_preload(preload)
                else:                   # queue new entry
                    new_entry = self.window.entrylist.get_entry(sub_entry)
                    if new_entry is None:
                        utils.warning_dialog(f"Entry '{sub_entry}' doesn't exist! Skipping...")
                        continue

                    if new_entry.location in self.run_log:
                        utils.warning_dialog(f"Found recursive call of entry '{new_entry.title}' inside entry '{self.entry.title}'! More details in '{LOG_FILE}'")

                        # recursive call logging
                        self._log(f"Found recursive call of '{new_entry.title}' inside '{self.entry.title}'! Call order:")
                        self._log("\n[RECURSIVE CALL ORDER (start)]", False)

                        indent = 1
                        for entry in self.run_log:
                            self._log(f"\t{'-' * indent}> {entry}", False)
                            indent += 1

                        self._log("\t[WARNING OCCURRENCE]", False)
                        self._log(f"\t{'-' * indent}> {new_entry.location} >>> called by entry '{self.entry.title}', exists in entry '{new_entry.title}'", False)
                        self._log(f"\t{'-' * (indent + 1)}> {self.entry.location} >>> called by entry '{new_entry.title}', exists in entry '{self.entry.title}'", False)
                        self._log("[RECURSIVE CALL ORDER (end)]", False)
                        self._write_debug()
                        self.already_wrote_log = True
                        continue

                    self.queued_entries.append(new_entry)
                    self._log(f"Queued next entry '{new_entry.title}'")

        proc = self.run_entry()

        if self.is_first:
            self._start_timer()
            self.running = True
            self.initial_call = proc
            self.is_first = False
            StartCoroutine(self._check_process, self.window)

        if len(self.queued_entries) > 0:
            self._log(f"Starting queued entries...")
            for entry in self.queued_entries:
                self.entry = entry
                self.queued_entries.remove(entry)
                self.run()
            self._log("Queued entries have been started.")
