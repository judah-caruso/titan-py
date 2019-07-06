#!/usr/bin/env python
from setuptools import setup, find_packages
from titan.globals import VERSION
import pkg_resources
import sys

try:
    if int(pkg_resources.get_distribution("pip").version.split(".")[0]) < 6:
        print("pip versions <= 6.0 not supported, please upgrade with:\n\n\t'pip install -U pip'")
        sys.exit(-1)
except pkg_resources.DistributionNotFound:
    pass

py_version = sys.version_info[:2]
if py_version < (2, 7, 3):
    print(f"Titan requires Python version 2.7.3 or later. Detected: {py_version}")
    sys.exit(-1)

long_description = ""

install_requires = ["toml", "wxPython", "wxasync"]

setup(name="Titan",
      version=VERSION,
      description="A simple program to open multiple games and track your playtime.",
      long_description=long_description,
      author="Judah Caruso Rodriguez",
      author_email="k@0px.moe",
      url="https://github.com/kyoto-shift/titan-py",
      license="GPLv2",
      packages=find_packages(exclude=["titan_games.toml"]),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={"gui_scripts": [
        "titan = titan.entrypoints.titan_gui:main"]})
