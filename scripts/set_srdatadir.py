#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
import sys

import sr

if __name__ == "__main__":
  usage = "usage: set_srdatadir.py <directory>"
  if len(sys.argv) > 1:
    srdatadir = pathlib.Path(sys.argv[1])
    if srdatadir.is_dir():
      abspath = srdatadir.resolve(strict=True)
      sr.settings["sr-data.path"] = abspath.as_posix()
      sys.exit()
  print(usage)

