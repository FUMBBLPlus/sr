#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import sys

import sr
from sr import bbcode
from sr.notepages import helper


class Item:

  HASBBCODE = True
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


class LineItem(Item):

  HASBBCODE = False
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


class EmptyItem(LineItem):

  LINESTRS = ("",)

  def bbcode(self):
    return ""


class TableStartItem:

  HASBBCODE = True

  def __str__(self):
    return "\n"

  def bbcode(self):
    return bbcode.otag(
        "table",
        "blackborder border2 bg=#e6ddc7"
    )


class TableEndItem:

  HASBBCODE = True

  def __str__(self):
    return "\n"

  def bbcode(self):
    return bbcode.ctag("table")



class MajorSeparatorItem:

  HASBBCODE = False

  def __str__(self):
    return "\n"



class CoachItem(Item):

  aligns = "C"
  charwidths = (90,)

  def __init__(self, coach):
      self.coach = coach

  @property
  def values(self):
      return (f'[{self.coach.id}] {self.coach.name}',)

  def bbcode(self):
    return bbcode.center(helper.bbccoach(self.coach))


class HeaderItem(Item):

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

  bbcodevalues = (
      f'Tournament{bbcode.THINSPACE}/{bbcode.THINSPACE}Team',
      bbcode.center("Fmt"),
      bbcode.center("Rnk"),
      bbcode.center("Lvl"),
      bbcode.center("Tms"),
      bbcode.center("Results"),
      bbcode.center(
          f'Pts{bbcode.sub("B")}{bbcode.THREEPEREMSPACE}'
      ),
      bbcode.center(
          f'Pts{bbcode.sub("T")}{bbcode.THREEPEREMSPACE}'
      ),
      bbcode.center(
          f'Slot{bbcode.sub("T")}{bbcode.THREEPEREMSPACE}'
      ),
      bbcode.center(
          f'Pts{bbcode.sub("C")}{bbcode.THREEPEREMSPACE}'
      ),
      bbcode.center(
          f'Slot{bbcode.sub("C")}{bbcode.THREEPEREMSPACE}'
      ),
  )

  def bbcode(self):
    return (
      bbcode.otag("tr", "bg=black fg=white")
      + "".join([
          (
              bbcode.otag("td")
              + s
              + bbcode.ctag("td")
          )
          for s in self.bbcodevalues
      ])
      + bbcode.ctag("tr")
    )



class MainTournamentItem(Item):

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

  def bbcode(self):
    return (
      bbcode.otag("tr", "bg=#b6ad97 fg=#e6ddc7")
      + bbcode.otag("td", "colspan=11")
      + bbcode.b(
          helper.bbctournament(self.tournament, False, False)
      )
      + bbcode.ctag("td")
      + bbcode.ctag("tr")
    )


class TeamItem(Item):

  BBCODEINDENT = bbcode.ENSPACE
  INDENT = "  "
  aligns = "L"
  charwidths = (90,)

  def __init__(self, team):
      self.team = team

  @property
  def values(self):
      return (self.INDENT + self.team.name,)

  def bbcode(self):
    return (
      bbcode.otag("tr", "bg=#d6cdb7")
      + bbcode.otag("td", "colspan=11")
      + self.BBCODEINDENT + helper.bbcteam(self.team)
      + bbcode.ctag("td")
      + bbcode.ctag("tr")
    )


class TeamPerformanceItem(Item):

  TOURNAMENTINDENT = "    "
  WINNERCHAR = "*"
  BBCODETOURNAMENTINDENT = bbcode.ENSPACE * 2
  BBCODEWINNERCHAR = "★"
  BBCODENONERESULTCHAR = "·"

  def __init__(self, report, performance):
    self.report = report
    self.performance = performance

  @property
  def current(self):
    return (self.report.weekNr == sr.time.current_weekNr())

  @property
  def tournament(self):
    return self.performance.tournament

  @property
  def coachperformance(self):
    return sr.performance.CoachPerformance(
        self.tournament.id, self.performance.team.coach.id
  )
  @property
  def maincoachperformance(self):
    return sr.performance.CoachPerformance(
        self.tournament.main.id, self.performance.team.coach.id
    )
  @property
  def mainperformance(self):
    return sr.performance.TeamPerformance(
        self.tournament.main.id, self.performance.team.id
    )

  @property
  def values(self):
    team = self.performance.team
    coach = team.coach
    mainperformance = self.mainperformance
    maincoachperformance = self.maincoachperformance
    tpoints = self.performance.points
    if tpoints is None:
      tslot = ""
    else:
      TR = self.report.teamrankings[team]
      Tmainperf = TR.slotobj.performances[mainperformance]
      tpoints = self.performance.points
      tslotgroup, tslotnr = Tmainperf
      tslot = tslotgroup.name
      if tslot == "W":
        tpoints = 0
      else:
        tslots = TR.slotobj.N(tslotgroup.name)
        tslot += f' {tslotnr}/{tslots}'
      if not mainperformance.clean:
        tslot = tslot.lower()
    cpoints = self.coachperformance.points
    if cpoints is None:
      cslot = ""
    else:
      CR =  self.report.coachrankings[coach]
      Cmainperf = CR.slotobj.performances[maincoachperformance]
      cslotgroup, cslotnr = Cmainperf
      cslot = cslotgroup.name
      if cslot == "W":
        cpoints = 0
      else:
        cslots = CR.slotobj.N(cslotgroup.name)
        cslot += f' {cslotnr}/{cslots}'
      if not maincoachperformance.clean:
        cslot = cslot.lower()
    try:
      srnteams = self.tournament.srnteams
    except IndexError:
      srnteams = ""
    results = "".join([
        r.value for r in self.performance.results
    ])
    iswinner = (team is self.tournament.winner)
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

  def bbcode(self, odd=True):
    Result = sr.tournament.Matchup.Result
    team = self.performance.team
    coach = team.coach
    mainperformance = self.mainperformance
    maincoachperformance = self.maincoachperformance
    tpoints = self.performance.points
    if tpoints is None:
      tslot = ""
    else:
      TR = self.report.teamrankings[team]
      Tmainperf = TR.slotobj.performances[mainperformance]
      tpoints = self.performance.points
      tslotgroup, tslotnr = Tmainperf
      tslot = tslotgroup.name
      if tslot == "W":
        tpoints = 0
      else:
        tslots = TR.slotobj.N(tslotgroup.name)
        #tslot += f'{bbcode.SIXPEREMSPACE}{tslotnr}/{tslots}'
        tslot = helper.bbcslot(tslot, tslotnr, tslots)
      if not mainperformance.clean:
        tslot = tslot.lower()
    cpoints = self.coachperformance.points
    if cpoints is None:
      cslot = ""
    else:
      CR =  self.report.coachrankings[coach]
      Cmainperf = CR.slotobj.performances[maincoachperformance]
      cslotgroup, cslotnr = Cmainperf
      cslot = cslotgroup.name
      if cslot == "W":
        cpoints = 0
      else:
        cslots = CR.slotobj.N(cslotgroup.name)
        #cslot += f' {cslotnr}/{cslots}'
        cslot = helper.bbcslot(cslot, cslotnr, cslots)
      if not maincoachperformance.clean:
        cslot = cslot.lower()
    try:
      srnteams = self.tournament.srnteams
    except IndexError:
      srnteams = ""
    resultparts = []
    for result, matchup in self.performance.fullresults:
      resultvalue = result.value
      if result is Result.none:
        resultvalue = self.BBCODENONERESULTCHAR
      if matchup is not None:
        match = matchup.match
        if match is not None:
          resultparts.append(
              helper.bbcmatch(match, resultvalue)
          )
        else:
          resultparts.append(resultvalue)
      else:
        resultparts.append(resultvalue)
    results = "".join(resultparts)
    iswinner = (team is self.tournament.winner)
    if iswinner:
      results += self.BBCODEWINNERCHAR
    parts = []
    #if odd:
    #  parts.append(bbcode.otag("tr"))
    #else:
    #  parts.append(bbcode.otag("tr", "bg=#d6cdb7"))
    parts.append(bbcode.otag("tr"))
    parts.append(bbcode.otag("td"))
    parts.append((
        self.BBCODETOURNAMENTINDENT
        + helper.bbctournament(self.tournament, False, False)
    ))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.center(self.tournament.srformatchar))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.center(self.tournament.rank))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.center(self.tournament.level))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.center(srnteams))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.monospace(results))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.right(self.performance.rawpoints))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(
        bbcode.right((tpoints if tpoints is not None else ""))
    )
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(tslot)
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(
          bbcode.right((cpoints if cpoints is not None else ""))
    )
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(cslot)
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.ctag("tr"))
    s = "".join(parts)
    return s

def iteritems(reportNr=None, coachName=None):
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
      yield MajorSeparatorItem()
    if coachName is None:
      yield CoachItem(C)
    yield TableStartItem()
    yield HeaderItem()
    yield LineItem()
    for coachperformance in sorted(
        R.slotobj.performances,
        key=lambda P: P.sort_key
    ):
      yield MainTournamentItem(coachperformance)
      for teamperformance in sorted(
          coachperformance.allteamperformances,
          key=lambda p:p.team.name
      ):
        yield TeamItem(teamperformance.team)
        for performance in sorted(
            teamperformance.thisallteamperformances
        ):
          yield TeamPerformanceItem(report, performance)
    yield TableEndItem()



def bbcode_points(reportNr=None, coachName=None):
  def subgen():
    for item in iteritems(reportNr, coachName):
      if not item.HASBBCODE:
        continue
      if item.__class__.__name__ == "TeamItem":
        oddevengen = itertools.cycle((True, False))
      if item.__class__.__name__ == "TeamPerformanceItem":
        yield item.bbcode(next(oddevengen))
      else:
        yield item.bbcode()
  return f'\\{bbcode.N}'.join(subgen())


def print_points(reportNr=None, coachName=None):
  for item in iteritems(reportNr, coachName):
    print(item)


def save_points(reportNr=None, coachName=None):
  if reportNr is None:
    report = sr.report.current_report()
  else:
    report = sr.report.Report(int(reportNr))
  reportNr = report.nr
  with open(f'pts-{reportNr}.txt', "w", encoding="utf8") as f:
    f.write("\n".join(
        [str(item) for item in iteritems(reportNr, coachName)]
    ))



if __name__ == "__main__":
  if len(sys.argv) == 1:
    save_points()
  else:
    save_points(*sys.argv[1:])
