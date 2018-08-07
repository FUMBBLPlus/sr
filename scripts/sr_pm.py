#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import sys

import sr
from sr import bbcode


class Row:

  STRSEPARATOR = " "
  charwidths = (30, 3, 3, 3, 3, 10, 4, 4, 8, 4, 8)
  aligns = aligns = "LCCCCLRRLRL"
  values = ("",) * len(charwidths)

  def __str__(self):
    align_trans = {"L": "<", "C": "^", "R": ">"}
    return self.STRSEPARATOR.join(
        "{{:{}{}}}".format(
            align_trans[self.aligns[c]], self.charwidths[c]
        ).format(v)
        for c, v in enumerate(self.values)
    )


class LineRow(Row):

  LINESTRS = ("=",)

  @property
  def aligns(self):
    return "L" * len(self.charwidths)


  @property
  def values(self):
    values = []
    for i, w in enumerate(self.charwidths):
      try:
        linestr = self.LINESTRS[i]
      except IndexError:
        linestr = self.LINESTRS[-1]
      chargen = itertools.cycle(linestr)
      values.append("".join(next(chargen) for _ in range(w)))
    return values



class EmptyRow(LineRow):

  LINESTRS = ("",)



class SpaceBetweenCoachAndTable:

  def __str__(self):
    return "\n"



class SpaceBetweenTwoTables:

  def __str__(self):
    return "\n" * 2



class CoachRow(Row):

    aligns = "C"
    charwidths = (90,)

    def __init__(self, coach):
        self.coach = coach

    @property
    def values(self):
        return (f'[{self.coach.id}] {self.coach.name}',)


class HeaderRow(Row):

  values = (
      "Tournament / Team",
      "Fmt",
      "Rnk",
      "Lvl",
      "Tms",
      "Results",
      "Pbas",
      "Ptea",
      "Stea",
      "Pcoa",
      "Scoa",
  )





class MainTournamentRow(Row):

    aligns = "L"
    charwidths = (90,)

    def __init__(self, coachperformance):
        self.coachperformance = coachperformance

    @property
    def tournament(self):
        return self.coachperformance.tournament

    @property
    def values(self):
        return (self.tournament.srname,)

class TeamRow(Row):

    INDENT = "  "
    aligns = "L"
    charwidths = (90,)

    def __init__(self, team):
        self.team = team

    @property
    def values(self):
        return (self.INDENT + self.team.name,)


class TeamPerformanceRow(Row):

  TOURNAMENTINDENT = "    "
  WINNERCHAR = "*"

  def __init__(self, report, performance):
    self.report = report
    self.performance = performance

  @property
  def tournament(self):
    return self.performance.tournament

  @property
  def coachperformance(self):
    return sr.performance.CoachPerformance(self.tournament.id, self.performance.team.coach.id)
  @property
  def maincoachperformance(self):
    return sr.performance.CoachPerformance(self.tournament.main.id, self.performance.team.coach.id)
  @property
  def mainperformance(self):
    return sr.performance.TeamPerformance(self.tournament.main.id, self.performance.team.id)

  @property
  def values(self):
    tpoints = self.performance.points
    if tpoints is None:
      tslot = ""
    else:
      tslotgroup, tslotnr = self.report.teamrankings[self.performance.team].slotobj.performances[self.mainperformance]
      tslot = tslotgroup.name
      if tslot == "W":
        tpoints = 0
      else:
        tslots = self.report.teamrankings[self.performance.team].slotobj.N(tslotgroup.name)
        tslot += f' {tslotnr}/{tslots}'
      if not self.mainperformance.clean:
        tslot = tslot.lower()
    cpoints = self.coachperformance.points
    if cpoints is None:
      cslot = ""
    else:
      cslotgroup, cslotnr = self.report.coachrankings[self.performance.team.coach].slotobj.performances[self.maincoachperformance]
      cslot = cslotgroup.name
      if cslot == "W":
        cpoints = 0
      else:
        cslots = self.report.coachrankings[self.performance.team.coach].slotobj.N(cslotgroup.name)
        cslot += f' {cslotnr}/{cslots}'
      if not self.maincoachperformance.clean:
        cslot = cslot.lower()
    try:
      srnteams = self.tournament.srnteams
    except IndexError:
      srnteams = ""
    results = "".join([
        r.value for r in self.performance.results
    ])
    iswinner = (self.performance.team is self.tournament.winner)
    if iswinner:
      results += self.WINNERCHAR
    result = [
      self.TOURNAMENTINDENT + self.tournament.srname,
      self.tournament.srformatchar,
      self.tournament.rank,
      self.tournament.level,
      srnteams,
      results,
      self.performance.rawpoints,
      (tpoints if tpoints is not None else ""),
      tslot,
       (cpoints if cpoints is not None else ""),
      cslot,
    ]
    return result


def iter_rows(reportNr=None, coachName=None):
  if reportNr is None:
    report = sr.report.current_report()
  else:
    report = sr.report.Report(int(reportNr))
  coachrankings = report.coachrankings
  if coachName is not None:
    coachrankings = {
        C: R for C, R in coachrankings.items()
        if C.name == coachName
    }
  for i, (C, R) in enumerate(coachrankings.items()):
    if 0 < i:
      yield SpaceBetweenTwoTables()
    if coachName is None:
      yield CoachRow(C)
      yield SpaceBetweenCoachAndTable()
    yield HeaderRow()
    yield LineRow()
    for coachperformance in sorted(
        R.slotobj.performances,
        key=lambda P: P.sort_key
    ):
      yield MainTournamentRow(coachperformance)
      for teamperformance in sorted(
          coachperformance.allteamperformances,
          key=lambda p:p.team.name
      ):
        yield TeamRow(teamperformance.team)
        for performance in sorted(
            teamperformance.thisallteamperformances
        ):
          yield TeamPerformanceRow(report, performance)





def print_points(reportNr=None, coachName=None):
  for row in iter_rows(reportNr, coachName):
    print(row)


def save_points(reportNr=None, coachName=None):
  if reportNr is None:
    report = sr.report.current_report()
  else:
    report = sr.report.Report(int(reportNr))
  reportNr = report.nr
  with open(f'pts-{reportNr}.txt', "w", encoding="utf8") as f:
    f.write("\n".join(
        [str(row) for row in iter_rows(reportNr, coachName)]
    ))


if __name__ == "__main__":
  if len(sys.argv) == 1:
    save_points()
  else:
    save_points(*sys.argv[1:])
