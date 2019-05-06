#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
import sys

import sr

if __name__ == "__main__":
  usage = "usage: sr_set_login.py my_user_name my_password"
  if len(sys.argv) > 2:
    sr.loginsettings["user_name"] = sys.argv[1]
    sr.loginsettings["password"] = sys.argv[2]
    srdatadir = pathlib.Path(sys.argv[1])
  else:
    print(usage)

