"""
    filehandler.py

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
import sys
import toml
import inspect

from titan.gui import utils
from titan.globals import CONFIG_FILE, LOG_FILE, VERSION, CFG_VERSION, NAME, NAME_LOW

TITAN_INFO_COMMENT = f" # Internal toml object used by {NAME}. Editing is not recommended."
TITAN_INFO_RAW = toml.dumps({f"{NAME_LOW}_info": {"cfg_version": CFG_VERSION}})
TITAN_TABLE_HEADER = TITAN_INFO_RAW.split()[0]
TITAN_INFO = TITAN_TABLE_HEADER + TITAN_INFO_COMMENT + TITAN_INFO_RAW[len(TITAN_TABLE_HEADER):]


def init_files():
    if os.path.exists(LOG_FILE):
        try:
            # if log file is more than 5 MB, clear it
            if os.path.getsize(LOG_FILE) >= 5000000:
                open(LOG_FILE, "w").close()
        except OSError as err:
            print("Unable to write to log file '{LOG_FILE}'! Do you have the correct permissions?")

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "a") as cfg_fh:
            cfg_fh.write("# This file may also be edited manually. However, there are a few things to note:\n")
            cfg_fh.write("#   - Path variables (location, preloads, etc) are OS-specific. If you're unsure how to format them, try adding an entry via the program and see how it formats the path.\n")
            cfg_fh.write("#   - All fields must be included (even if empty).\n")
            cfg_fh.write("#   - Names can be formatted however you like. If the name uses spaces or special characters, you must surround it with double quotes (ex. \"Titanfall 2\").\n")
            cfg_fh.write("#   - time_played takes a float value of the amount of time played (in seconds)\n")
            cfg_fh.write("#   - times_opened takes an integer value of the amount of times opened.\n")
            cfg_fh.write("""
# ["Example Game"]
# time_played = 60 # Time in seconds
# times_opened = 1
# location  = "C:\\\\Games\\\\ExampleGame\\\\bin\\\\game.exe" # A string of the path to the main executable of the game (OS-specific formatting).
# arguments = [ "--console", "--windowed=true" ] # A list of strings for console commands you'd like to run with the game. Is the equivalent of "Set Launch Options" in Steam.
# preloads  = [ "C:\\\\Games\\\\ExampleGame\\\\bin\\\\trainer.exe", "cmd:[obs]" ] # A list of strings for external programs or entries you'd like to run before the main program.\n\n""")
            cfg_fh.write(TITAN_INFO)


def save_entries(entries):
    try:
        with open(CONFIG_FILE, "w") as cfg_fh:
            cfg_fh.write(TITAN_INFO)
            for entry in entries:
                args_normalized = []
                preloads_normalized = []

                if len(entry.preloads) > 0:
                    for preload in entry.preloads:
                        preloads_normalized.append(os.path.normpath(preload.strip()))

                if len(entry.arguments) > 0:
                    for argument in entry.arguments:
                        args_normalized.append(argument.strip())

                cfg_fh.write("\n")
                toml.dump({entry.title: {
                    "time_played": entry.time_played,
                    "times_opened": entry.times_opened,
                    "location": os.path.normpath(entry.location),
                    "arguments": args_normalized,
                    "preloads": preloads_normalized
                    }}, cfg_fh)
    except PermissionError as err:
        utils.warning_dialog(f"Unable to save to file '{CONFIG_FILE}'!\nReason: {err.strerror} [{err.errno}]")
        return


def load_file(f):
    try:
        file = toml.load(f)
        del file[f"{NAME_LOW}_info"]
        return file
    except toml.TomlDecodeError as err:
        if "already exists" in err.msg:
            utils.error_dialog(f"Entry '{str(err.msg).split()[1]}' already exists in file '{f}'!")
        else:
            utils.error_dialog(f"Formatting error in file '{f}'!\nReason: {err.msg}")
    except:
        utils.error_dialog(f"Unable to load file '{f}'!\nReason: {sys.exc_info()[0]}")


def delete_file(f):
    try:
        os.remove(f)
    except OSError as err:
        utils.error_dialog(f"Unable to remove file '{f}'!\nReason: {err.strerror} [{err.errno}]")
