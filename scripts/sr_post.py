#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import sr


def main():
  print("Please wait...")
  now = sr.time.now()
  timefmt = sr.time.ISO_DATE_FMT + " " + sr.time.ISO_TIME_FMT_M
  ps = []
  post_kwargs = {}
  ps.extend(sr.notepages.page["SR-Tournaments-Y__"].toupdate())
  ps.append(
      sr.notepages.page["SR-Tournaments-Pending"].NotePage
  )
  ps.append(
      sr.notepages.page["SR"].NotePage
  )
  post_kwargs["SR"] = {"updated": now}
  for P in ps:
    print(f'{P.link}...', end="\r")
    sys.stdout.flush()
    P.post(**(post_kwargs.get(P.link, {})))
    print(f'{P.link}   ')
    sys.stdout.flush()
  print(f'Updated at {now.strftime(timefmt)}')


if __name__ == "__main__":
  usage = "usage: sr_post.py"
  if len(sys.argv) > 1:
      print(usage)
      sys.exit()
  try:
    main()
  except KeyboardInterrupt:
    pass
