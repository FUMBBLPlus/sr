#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import sr

TOURNAMENTS = {
    "added": sr.tournament.added,
    "all": sr.tournament.all_,
    "enters": sr.tournament.enters,
    "exits": sr.tournament.exits,
    "new": sr.tournament.new,
    "observed": sr.tournament.observed,
    "pending": sr.tournament.pending,
    "offumbblyear": sr.tournament.offumbblyear,
    "ofweeknr": sr.tournament.ofweekNr,
}

FILTERS = {
    "multi",
}


def get_filter(argv):
  p = argv[-1].partition("=")
  if p[2].strip():
    return p[2].strip().lower()


def get_tournaments(argv):
  name = argv[1]
  parameters = argv[2:]
  if get_filter(argv):
    parameters = parameters[:-1]
  parameters = [
      (int(p) if p.isdecimal() else p)
      for p in parameters
  ]
  if name.lower() in TOURNAMENTS:
    f = TOURNAMENTS[name.lower()]
    tournaments_ = f(*parameters)
  elif name.isdecimal():
    tournamentId = int(name)
    tournaments_ = {
        T for T in sr.tournament.added()
        if T.id == tournamentId
    }
  else:
    tournaments_ = {
        T for T in sr.tournament.added()
        if T.srname.upper() == name.upper()
    }
  tournaments_ = {T for T in tournaments_ if T.ismain}
  return sr.tournament.sort(tournaments_, reverse=True)


def main(tournaments, filter_):
  for T in tournaments:
    tshown = False
    for CP in sorted(
        T.allcoachperformances,
        key=lambda CP: CP.totalpoints,
        reverse=True,
    ):
      allteams = CP.allteams
      if len(allteams) == 1 and filter_ == "multi":
        continue
      if not tshown:
        stra2 = f' [{T.id}] {T.srclass.val}'[:49]
        stra1 = T.srname[:49-len(stra2)]
        stra = stra1 + stra2
        print(
            f'{stra:<50}'
            f'{"Results":<11}'
            f'{" Praw":^5}'
            f'{"  P":^5}'
            f'{" Ptot":^5}'
            f'{"C":>3}'
        )
        print("-" * 79)
        tshown = True
      stra = f'Coach: {str(CP.coach)} [{CP.coach.id}]'[:65]
      print(
          f'{stra:<71}'
          f'{CP.totalpoints:>5}'
          f'{"-+"[CP.clean]:>3}'
      )
      for Te in allteams:
        TP = sr.performance.TeamPerformance(T.id, Te.id)
        stra = (
            " " * 2
            + "Team: "
            + f'{str(Te).strip()} [{str(Te.id)}]'
        )[:49]
        tppoints = TP.points
        if tppoints is None:
          tppoints = ""
        print(
            f'{stra:<50}'
            f'{TP.strresults:<11}'
            f'{TP.rawpoints:>5}'
            f'{tppoints:>5}'
            f'{TP.totalpoints:>5}'
            f'{"-+"[TP.clean]:>3}'
        )
        for TP2 in sorted(
            TP.qualifierteamperformances,
            key=lambda TP: (
                (TP.rawpoints == 0),
                -TP.tournament.id,
            )
        ):
          stra2 = (
              f' [{TP2.tournament.id}]'
              f' {TP2.tournament.srclass.val}'
          )[:49]
          stra1 = (
              " " * 4
              + TP2.tournament.srname
          )[:49-len(stra2)]
          stra = stra1 + stra2
          tp2points = TP2.points
          if tp2points is None:
            tp2points = ""
          print(
              f'{stra:<50}'
              f'{TP2.strresults:<11}'
              f'{TP2.rawpoints:>5}'
              f'{tp2points:>5}'
              f'{"-+"[TP2.clean]:>8}'
          )
    if tshown:
      print()


def usage():
  line1 = (
      "usage: sr_points.py "
      "<tournament(s) parameter(s)> [filter=<filtername>]"
  )
  line2 = (
      "tournament shortcuts: "
      + ", ".join(TOURNAMENTS)

  )
  line3 = "filters: multi"
  return "\n".join([line1, line2, line3])


if __name__ == "__main__":
  if len(sys.argv) == 1:
    print(usage())
    sys.exit()
  try:
    tournaments = get_tournaments(sys.argv)
  except TypeError:
    print(usage())
    sys.exit()
  if not tournaments:
    print(usage())
    sys.exit()
  filter_ = get_filter(sys.argv)
  if filter_ and filter_ not in FILTERS:
    print(usage())
    sys.exit()
  try:
    main(tournaments, filter_)
  except KeyboardInterrupt:
    pass
