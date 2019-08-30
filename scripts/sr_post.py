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


def queue_halloffame_all():
  queue_halloffame_topcoaches()
  queue_halloffame_topteams()
  queue_halloffame_famouscoaches()
  queue_halloffame_famousteams()

def queue_halloffame_topcoaches():
  module = sr.notepages.page["SR-Coach-Records"]
  postqueue.append((module.NotePage, {}))

def queue_halloffame_topteams():
  module = sr.notepages.page["SR-Team-Records"]
  postqueue.append((module.NotePage, {}))

def queue_halloffame_famouscoaches():
  module = sr.notepages.page["SR-Coach-Famous"]
  postqueue.append((module.NotePage, {}))

def queue_halloffame_famousteams():
  module = sr.notepages.page["SR-Team-Famous"]
  postqueue.append((module.NotePage, {}))


def queue_pointspage_all():
  module = sr.notepages.page["SR-Coach-Points-name"]
  report = module.NotePage.report
  for row in report.coachfullrankings:
    if row.upperNr or row.lowerNr:
      queue_pointspage_coach(row.Performer.name)

def queue_pointspage_cleanup():
  module = sr.notepages.page["SR-Coach-Points-name"]
  ids = sr.data["coachpointsnote"]
  ids_taken = set(module.NotePage.coachpointsnotes.values())
  ids_available = ids - ids_taken
  if ids_available:
    postqueue.extend([
        (module.CleanupNotePage(i), {})
        for i in ids_available
    ])

def queue_pointspage_coach(coachName):
  module = sr.notepages.page["SR-Coach-Points-name"]
  postqueue.append(
      (module.NotePage.of_coachName(coachName), {})
  )


def queue_reportpage_after_turntime():
  c = sr.report.current_report()
  p, n = c.prevnext
  if p:
    reportNrs = [p.nr, c.nr]
  else:
    reportNrs = [c.nr]
  return queue_reportpage_custom(*reportNrs)

def queue_reportpage_all():
  current_weekNr = sr.time.current_weekNr()
  reportNrs = [
      reportNr
      for reportNr, weekNr in sr.report.reportNrs().items()
      if weekNr <= current_weekNr
  ]
  queue_reportpage_custom(*reportNrs)

def queue_reportpage_current():
  queue_reportpage_custom(sr.report.current_report().nr)

def queue_reportpage_custom(*reportNrs):
  module = sr.notepages.page["SR-Report-n"]
  postqueue.extend([
      (module.NotePage.of_reportNr(reportNr), {})
      for reportNr in reportNrs
  ])


def queue_reportspage_after_turntime():
  c = sr.report.current_report()
  fumbblyears = {sr.time.current_fumbblyear()}
  p, n = c.prevnext
  if p:
    fumbblyears.add(sr.time.fumbblyear(p.weekNr))
  return queue_reportspage_custom(*sorted(fumbblyears))

def queue_reportspage_all():
  queue_reportspage_custom(*sr.time.fumbblyears())

def queue_reportspage_current():
  queue_reportspage_custom(sr.time.current_fumbblyear())

def queue_reportspage_custom(*fumbblyears):
  module = sr.notepages.page["SR-Reports-Yn"]
  postqueue.extend([
      (module.NotePage.of_fumbblyear(y), {})
      for y in fumbblyears
  ])


def queue_tournamentspage_all():
  queue_tournamentspage_custom(*sr.time.fumbblyears())

def queue_tournamentspage_unfinalized():
  W = sr.time.lowest_enterweekNr_of_unexited()
  Y = sr.time.fumbblyear(W)
  fumbblyears = [y for y in sr.time.fumbblyears() if Y <= y]
  queue_tournamentspage_custom(*fumbblyears)

def queue_tournamentspage_current():
  queue_tournamentspage_custom(sr.time.current_fumbblyear())

def queue_tournamentspage_custom(*fumbblyears):
  module = sr.notepages.page["SR-Tournaments-Yn"]
  postqueue.extend([
      (module.NotePage.of_fumbblyear(y), {})
      for y in fumbblyears
  ])

def queue_tournamentspage_pending():
  module = sr.notepages.page["SR-Tournaments-Pending"]
  postqueue.append((module.NotePage, {}))


def queue_supplemental_all():
  queue_rrr_masters()
  queue_xfl_masters()
  for weight in ("LO", "MI", "HI"):
    queue_barb_masters(weight)

def queue_rrr_masters():
  module = sr.notepages.page["RRR-GrandMasters"]
  postqueue.append((module.NotePage, {}))

def queue_xfl_masters():
  module = sr.notepages.page["XFL-GrandMasters"]
  postqueue.append((module.NotePage, {}))

def queue_barb_masters(weight):
  module = sr.notepages.page[f'BARB-w-GrandMasters']
  np = getattr(module, f'{weight.upper()}_NotePage')
  postqueue.append((np, {}))



def postall():
  while postqueue:
    postone()

def postone():
  notepageobj, kwargs = postqueue.popleft()
  id_ = notepageobj.id or ".."
  print(
      f'Posting [{id_}] {notepageobj.link}...',
      end="\r",
  )
  sys.stdout.flush()
  notepageobj.post(**kwargs)
  print(
      f'Posting [{notepageobj.id}] {notepageobj.link} [DONE]',
  )
  sys.stdout.flush()


def post_after_turntime():
  queue_pointspage_all()
  postall()
  queue_pointspage_cleanup()
  queue_reportpage_after_turntime()
  queue_reportspage_after_turntime()
  queue_tournamentspage_unfinalized()
  queue_tournamentspage_pending()
  queue_mainpage()
  queue_halloffame_all()
  queue_supplemental_all()
  postall()


def post_all():
  queue_pointspage_all()
  postall()
  queue_pointspage_cleanup()
  queue_reportpage_all()
  queue_reportspage_all()
  queue_tournamentspage_all()
  queue_tournamentspage_pending()
  queue_mainpage()
  queue_halloffame_all()
  queue_supplemental_all()
  postall()


def post_mainpage():
  queue_mainpage()
  postall()


def post_halloffame():
  print("Which hall of fame pages?")
  options = {
    "a": (
        "all of them",
        queue_halloffame_all,
    ),
    "tc": (
        "Top Coaches",
        queue_halloffame_topcoaches,
    ),
    "tt": (
        "Top Teams",
        queue_halloffame_topteams,
    ),
    "fc": (
        "Famous Coaches",
        queue_halloffame_famouscoaches,
    ),
    "ft": (
        "Famous Teams",
        queue_halloffame_famousteams,
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


def post_pointspage():
  print("Whose points pages?")
  options = {
    "a": (
        "all of them",
        queue_pointspage_all,
    ),
    "x": (
        "cleanup",
        queue_pointspage_cleanup,
    ),
    "c": (
        "specific coach",
        lambda: queue_pointspage_coach(
            sr.helper.Input("name")()
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


def post_reportspage():
  print("Which reports pages?")
  options = {
    "tt": (
        "post after turntime (current and previous)",
        queue_reportspage_after_turntime,
    ),
    ".": (
        "current",
        queue_reportspage_current,
    ),
    "a": (
        "all of them",
        queue_reportspage_all,
    ),
    "c": (
        "custom",
        lambda: queue_reportspage_custom(
            *sr.helper.FumbblyearsInput("fumbblyear(s)")()
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


def post_supplemental():
  print("Which hall of fame pages?")
  options = {
    "a": (
        "all of them",
         queue_supplemental_all,
    ),
    "rrr": (
        "RRR Grand Masters",
        queue_rrr_masters,
    ),
    "xfl": (
        "XFL Grand Masters",
        queue_xfl_masters,
    ),
    "blo": (
        "BARB Low Grand Masters",
        lambda: queue_barb_masters("LO"),
    ),
    "bmi": (
        "BARB Mid Grand Masters",
        lambda: queue_barb_masters("MI"),
    ),
    "bhi": (
        "BARB High Grand Masters",
        lambda: queue_barb_masters("HI"),
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
        queue_tournamentspage_all,
    ),
    ".": (
        "current",
        queue_tournamentspage_current,
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
    "a": (
        "post all pages",
        post_all,
    ),
    "p": (
        "post coach points page(s)",
        post_pointspage,
    ),
    "r1": (
        "post report page(s)",
        post_reportpage,
    ),
    "ry": (
        "post reports of year page(s)",
        post_reportspage,
    ),
    "ty": (
        "post tournaments of year page(s)",
        post_tournamentspage,
    ),
    "h": (
        "post hall of fame page(s)",
        post_halloffame,
    ),
    "s": (
        "post supplemental page(s)",
        post_supplemental,
    ),
    "m": (
        "post mainpage",
        post_mainpage,
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
