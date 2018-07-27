#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import sys

import sr


now = sr.time.now()
postqueue = collections.deque()
timefmt = sr.time.ISO_DATE_FMT + " " + sr.time.ISO_TIME_FMT_M


def queue_tournamentspage_added():
  queue_tournamentspage_custom(*sr.time.fumbblyears())

def queue_tournamentspage_unfinalized():
  W = sr.time.lowest_enterweekNr_of_unexited()
  Y = sr.time.fumbblyear(w)
  fumbblyears = [y for y in sr.time.fumbblyears() if Y <= y]
  queue_tournamentspage_custom(*fumbblyears)

def queue_tournamentspage_custom(*fumbblyears):
  module = sr.notepages.page["SR-Tournaments-Y__"]
  postqueue.extend([
      (module.NotePage.of_fumbblyear(y), {})
      for y in fumbblyears
  ])

def postall():
  while postqueue:
    postone()

def postone():
  notepageobj, kwargs = postqueue.popleft()
  print(f'{notepageobj.link}...', end="\r")
  sys.stdout.flush()
  notepageobj.post(**kwargs)
  print(f'{notepageobj.link}   ')
  sys.stdout.flush()


def post_tournaments_page():
  print("Which tournaments pages?")
  options = {
    "a": (
        "all of them",
        queue_tournamentspage_added,
    ),
    "u": (
        "those with unfinalized fumbblyear",
        queue_tournamentspage_unfinalized,
    ),
    "c": (
        "custom",
        lambda: queue_tournamentspage_custom(
            *sr.helper.FumbblyearsInput("fumbblyear(s)")()
        )
    ),
    "e": ("exit", lambda: None)
  }
  for o, (message, f) in options.items():
    print(f'  {o.upper()}: {message}')
  sr.helper.CallerInput(
      options = {o: f for o, (message, f) in options.items()},
  )()
  postall()


def main():
  while True:
    print("Options:")
    print("  1: post new report")
    print("  T: post tournaments page")
    print("  Q: quit")
    while True:
      I = input(sr.helper.Input.prompt).strip().upper()
      if I in ("T", "TOURNAMENTS", "TOURNAMENTS PAGE"):
        post_tournaments_page()
        break
      elif I in ("Q", "QUIT"):
        return


  print("Please wait...")
  now = sr.time.now()

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
