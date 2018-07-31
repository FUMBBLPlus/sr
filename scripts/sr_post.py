#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import sys

import sr


now = sr.time.now()
postqueue = collections.deque()
timefmt = sr.time.ISO_DATE_FMT + " " + sr.time.ISO_TIME_FMT_M


def queue_mainpage():
  module = sr.notepages.page["SR"]
  postqueue.append((module.NotePage, {"updated": now}))


def queue_reportpage_all():
  queue_reportpage_custom(*list(sr.report.reportNrs()))

def queue_reportpage_current():
  queue_reportpage_custom(sr.report.current_report().nr)

def queue_reportpage_custom(*reportNrs):
  module = sr.notepages.page["SR-Report-n"]
  postqueue.extend([
      (module.NotePage.of_reportNr(reportNr), {})
      for reportNr in reportNrs
  ])

def queue_reportpage_after_turntime():
  c = sr.report.current_report()
  p, n = c.prevnext
  if p:
    reportNrs = [p.nr, c.nr]
  else:
    reportNrs = [c.nr]
  return queue_reportpage_custom(*reportNrs)


def queue_tournamentspage_added():
  queue_tournamentspage_custom(*sr.time.fumbblyears())

def queue_tournamentspage_unfinalized():
  W = sr.time.lowest_enterweekNr_of_unexited()
  Y = sr.time.fumbblyear(W)
  fumbblyears = [y for y in sr.time.fumbblyears() if Y <= y]
  queue_tournamentspage_custom(*fumbblyears)

def queue_tournamentspage_custom(*fumbblyears):
  module = sr.notepages.page["SR-Tournaments-Yn"]
  postqueue.extend([
      (module.NotePage.of_fumbblyear(y), {})
      for y in fumbblyears
  ])

def queue_tournamentspage_pending():
  module = sr.notepages.page["SR-Tournaments-Pending"]
  postqueue.append((module.NotePage, {}))


def postall():
  while postqueue:
    postone()

def postone():
  notepageobj, kwargs = postqueue.popleft()
  print(notepageobj, kwargs)
  print(f'Posting {notepageobj.link}...', end="\r")
  sys.stdout.flush()
  notepageobj.post(**kwargs)
  print(f'Posting {notepageobj.link} [DONE]')
  sys.stdout.flush()


def post_after_turntime():
  queue_reportpage_after_turntime()
  queue_tournamentspage_unfinalized()
  queue_tournamentspage_pending()
  queue_mainpage()
  postall()


def post_mainpage():
  queue_mainpage()
  postall()


def post_reportpage():
  print("Which report pages?")
  options = {
    "tt": (
        "post after turntime (current and previous)",
        queue_reportpage_after_turntime,
    ),
    ".": (
        "current",
        queue_reportpage_current,
    ),
    "a": (
        "all of them",
        queue_reportpage_all,
    ),
    "c": (
        "custom",
        lambda: queue_reportpage_custom(
            *sr.helper.ReportNrsInput("reportNr(s)")()
        ),
    ),
    "e": (
        "exit",
        lambda: None,
    ),
  }
  for o, (message, f) in options.items():
    print(f'  {o.upper()}: {message}')
  response = sr.helper.CallerInput(
      options = {o: f for o, (message, f) in options.items()},
  )()
  postall()


def post_tournamentspage():
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
        ),
    ),
    "p": (
        "pending",
        queue_tournamentspage_pending,
    ),
    "e": (
        "exit",
        lambda: None,
    ),
  }
  for o, (message, f) in options.items():
    print(f'  {o.upper()}: {message}')
  response = sr.helper.CallerInput(
      options = {o: f for o, (message, f) in options.items()},
  )()
  postall()


def main():
  options = {
    "tt": (
        "post all pages after turn time",
        post_after_turntime,
    ),
    "m": (
        "post mainpage",
        post_mainpage,
    ),
    "r1": (
        "post report page(s)",
        post_reportpage,
    ),
    "t": (
        "post tournaments page(s)",
        post_tournamentspage,
    ),
    "q": ("quit", lambda: "<QUIT>")
  }
  while True:
    print("Options:")
    for o, (message, f) in options.items():
      print(f'  {o.upper()}: {message}')
    response = sr.helper.CallerInput(
        options = {
            o: f
            for o, (message, f) in options.items()
        },
    )()
    if response == "<QUIT>":
      break





if __name__ == "__main__":
  usage = "usage: sr_post.py"
  if len(sys.argv) > 1:
      print(usage)
      sys.exit()
  try:
    main()
  except KeyboardInterrupt:
    pass
