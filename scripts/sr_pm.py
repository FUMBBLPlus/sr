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
    parts = [
        "[block=automargin width=814px]",
        bbcode.otag(
            "table",
            "blackborder border2 bg=#e6ddc7",
        ),
    ]
    return "".join(parts)


class TableEndItem:

  HASBBCODE = True

  def __str__(self):
    return "\n"

  def bbcode(self):
    return bbcode.ctag("table") + bbcode.ctag("block")



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
      "FSG",
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
      "Results",
      bbcode.center(
          f'Pts{bbcode.sub("B")}{bbcode.THREEPEREMSPACE}'
      ),
      bbcode.center("FSG"),
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

  bbcodewidths = (
      "250px",
      "46px",
      "46px",
      "46px",
      "46px",
      "100px",
      "46px",
      "46px",
      "46px",
      "46px",
      "46px",
      "46px",
  )

  def bbcode(self):
    return (
      bbcode.otag("tr", "bg=black fg=white")
      + "".join([
          (
              bbcode.otag("td", f'width={self.bbcodewidths[i]}')
              + s
              + bbcode.ctag("td")
          )
          for i, s in enumerate(self.bbcodevalues)
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
      + bbcode.otag("td", "colspan=12")
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
      + bbcode.otag("td", "colspan=12")
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
    self._raw_values = ...

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
  def raw_values(self):
    if self._raw_values is ...:
      team = self.performance.team
      coach = team.coach
      d = {
          "Tournament": self.tournament,
          "Fmt": self.tournament.srformatchar,
          "Rnk": self.tournament.rank,
          "Lvl": self.tournament.level,
          "Tms": None,
          "Results": self.performance.results,
          "Winner": (team is self.tournament.winner),
          "PtsB": self.performance.rawpoints,
          "FSG": helper.bbcfsgname(self.tournament.main),
          "PtsT": self.performance.points,
          "SlotT": None,
          "SlotT_n": None,
          "SlotT_N": None,
          "CleanT": self.mainperformance.clean,
          "PtsC": self.coachperformance.points,
          "SlotC": None,
          "SlotC_n": None,
          "SlotC_N": None,
          "CleanC": self.maincoachperformance.clean,
      }
      try:
        d["Tms"] = self.tournament.srnteams
      except IndexError:
        pass
      if d["PtsT"] is not None:
        TR = self.report.teamrankings[team]
        tmper = TR.slotobj.performances[self.mainperformance]
        d["SlotT"], d["SlotT_n"] = tmper
        if d["SlotT"] is sr.slot.SlotGroup("W"):
          d["PtsT"] = 0
        else:
          d["SlotT_N"] = TR.slotobj.N(d["SlotT"].name)
      if d["PtsC"] is not None:
        CR =  self.report.coachrankings[coach]
        cmper = CR.slotobj.performances[self.maincoachperformance]
        d["SlotC"], d["SlotC_n"] = cmper
        if d["SlotC"] is sr.slot.SlotGroup("W"):
          d["PtsC"] = 0
        else:
          d["SlotC_N"] = CR.slotobj.N(d["SlotC"].name)
      self._raw_values = d
    return self._raw_values

  @property
  def values(self):
    d = self.raw_values
    return [
      self.TOURNAMENTINDENT + d["Tournament"].srname,
      d["Fmt"],
      d["Rnk"],
      d["Lvl"],
      (d["Tms"] if d["Tms"] else ""),
      (
          "".join([
              item[0].value for item in d["Results"]
          ])
          + (self.WINNERCHAR if d["Winner"] else "")
      ),
      d["PtsB"],
      d["FSG"],
      ("" if d["PtsT"] is None else d["PtsT"]),
      (
          (
              "" if d["SlotT"] is None
              else (
                  d["SlotT"].name if d["CleanT"]
                  else d["SlotT"].name.lower()
              )
          )
          + ("" if d["SlotT_n"] is None else f' {d["SlotT_n"]}')
          + ("" if d["SlotT_N"] is None else f'/{d["SlotT_N"]}')
      ),
      ("" if d["PtsC"] is None else d["PtsC"]),
      (
          (
              "" if d["SlotC"] is None
              else (
                  d["SlotC"].name if d["CleanC"]
                  else d["SlotC"].name.lower()
              )
          )
          + ("" if d["SlotC_n"] is None else f' {d["SlotC_n"]}')
          + ("" if d["SlotC_N"] is None else f'/{d["SlotC_N"]}')
      ),
  ]

  def bbcode(self, odd=True):
    d = self.raw_values
    Result = sr.tournament.Matchup.Result
    resultparts = []
    for item in d["Results"]:
      result, oppo, match = item
      resultvalue = result.value
      if result is Result.none:
        resultvalue = self.BBCODENONERESULTCHAR
      if match is not None:
        resultparts.append(
            helper.bbcmatch(match, resultvalue)
        )
      else:
        resultparts.append(resultvalue)
    results = "".join(resultparts)
    if d["Winner"]:
      results += self.BBCODEWINNERCHAR
    parts = []
    parts.append(bbcode.otag("tr"))
    parts.append(bbcode.otag("td"))
    parts.append((
        self.BBCODETOURNAMENTINDENT
        + helper.bbctournament(d["Tournament"], False, False)
    ))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.center(d["Fmt"]))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.center(d["Rnk"]))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.center(d["Lvl"]))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    if d["Tms"]:
      parts.append(bbcode.center(d["Tms"]))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.monospace(results))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.right(d["PtsB"]))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(d["FSG"])
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    if d["PtsT"] is not None:
      parts.append(bbcode.right(d["PtsT"]))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    if d["SlotT"]:
      parts.append(helper.bbcslot((
          d["SlotT"] if d["CleanT"] else d["SlotT"].lower()),
          d["SlotT_n"],
          d["SlotT_N"],
      ))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    if d["PtsC"] is not None:
      parts.append(bbcode.right(d["PtsC"]))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    if d["SlotC"]:
      parts.append(helper.bbcslot((
          d["SlotC"] if d["CleanC"] else d["SlotC"].lower()),
          d["SlotC_n"],
          d["SlotC_N"],
      ))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.ctag("tr"))
    s = "".join(parts)
    return s


class FooterItem(Item):

  def __init__(self, coachpoints):
    self.coachpoints = coachpoints
    super().__init__()

  def __str__(self):
    return ""

  def bbcode(self):
    parts = []
    parts.append(bbcode.otag("tr", "bg=black fg=white"))
    parts.append(bbcode.otag("td", "colspan=10"))
    parts.append("Total SR Coach Ranking Points")
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
    parts.append(bbcode.right(self.coachpoints))
    parts.append(bbcode.ctag("td"))
    parts.append(bbcode.otag("td"))
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
    coachpoints = 0
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
          tpi = TeamPerformanceItem(report, performance)
          yield tpi
          coachpoints += tpi.raw_values["PtsC"]
    yield FooterItem(coachpoints)
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
