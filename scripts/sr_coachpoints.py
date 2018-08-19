#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys

import sr


if __name__ == "__main__":
  params = [json.loads(a) for a in sys.argv[2:]]
  m = sr.notepages.page["SR-Coach-Points-name"]
  if len(sys.argv) == 1:
    print("Please wait...")
    try:
      m.print_points()
    except KeyboardInterrupt:
      pass
  elif "print".startswith(sys.argv[1].lower()):
    print("Please wait...")
    try:
      m.print_points(*params)
    except KeyboardInterrupt:
      pass
  elif "save".startswith(sys.argv[1].lower()):
    print("Please wait...")
    m.save_points(*params)
  else:
    print(
        "USAGE: sr_coachpoints.py "
        "[print|save] "
        "[reportNr] "
        "[coachName] "
        "[onebyone]"
    )
