"""
    globals.py

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
import sys

NAME = "Titan"
NAME_LOW = NAME.lower()
VERSION = "0.11"

USAGE = f"{NAME} v{VERSION}\nUsage: {NAME_LOW} (help|add|list|stats) [game]"
LONG_USAGE = ""

WORKING_DIR = os.path.dirname(sys.argv[0])
CONFIG_FILE = os.path.join(WORKING_DIR, f"{NAME_LOW}_games.toml")
STATS_FILE = os.path.join(WORKING_DIR, f"{NAME_LOW}_stats.toml")
LOG_FILE = os.path.join(WORKING_DIR, f"{NAME_LOW}.log")
