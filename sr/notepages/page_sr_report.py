import math
import re

import sr
from .. import bbcode
from . import helper


class NotePage(helper.NotePage):

  KEY = "SR-Report-n"
  NAME = "Report"

  COACHMINPTS = 25
  TEAMNRCUTOFF = 100

  @classmethod
  def of_reportNr(cls, nr):
    name = f'SR-{cls.NAME}-{nr}'
    return cls(name)

  @classmethod
  def of_weekNr(cls, weekNr):
    nr = sr.report.weekNrs()[weekNr]
    return cls.of_reportNr(nr)

  @property
  def date(self):
    fromdate = self.report.date
    fromdatestr = fromdate.strftime(sr.time.ISO_DATE_FMT)
    todate = self.report.enddate
    if todate is not None:
      todatestr = todate.strftime(sr.time.ISO_DATE_FMT)
      return f'from {fromdatestr} to {todatestr}'
    else:
      return f'from {fromdatestr}'

  @property
  def nextreportlink(self):
    _, r = self.report.prevnext
    if r and r.weekNr <= sr.time.current_weekNr():
      return helper.bbcreport(r, "Next >>>")
    else:
      return ""

  @property
  def nr(self):
    matchobj = re.search(f'SR-{self.NAME}-(\\d+)', self.link)
    if matchobj:
      return int(matchobj.group(1))

  def numsomething(self, singulartitle, pluraltitle, value):
    if 1 == value:
      title = singulartitle
    elif 1 < value:
      title = pluraltitle
    return f'{title}: {value}'

  @property
  def numcoaches(self):
    value = len(self.report.coachfullrankings)
    return self.numsomething("Coach", "Coaches", value)

  @property
  def numteams(self):
    value =  len(self.report.teamfullrankings)
    return self.numsomething("Team", "Teams", value)

  @property
  def nummaintournaments(self):
    value =  len(
        {T for T in self.report.tournaments if T.ismain}
    )
    return self.numsomething(
        "Main Tournament", "Main Tournaments", value
    )

  @property
  def prevreportlink(self):
    r, _ = self.report.prevnext
    if r:
      return helper.bbcreport(r, "<<< Previous")
    else:
      return ""

  @property
  def report(self):
    return sr.report.Report(self.nr)

  @property
  def title2(self):
    return f'OBC Sport SR Rankings Report {self.nr}'

  def coachtable(self, house):
    header=[
        "Nr",
        "Move",
        "Coach",
        "P",
        "PΔ",
        "Pw",
        "T",
        "G",
    ]
    rankings = self.report.coachfullrankings
    def rowgen():
      prevNr = None
      for r in rankings:
        if getattr(r, f'{house.lower()}Nr'):
          Nr = (str(r.Nr) if r.Nr != prevNr else "")
          Move = helper.bbcmove(r.Move)
          Coach = helper.bbccoach(r.Performer)
          P = str(r.P)
          PΔ = (str(r.PΔ) if r.PΔ else "")
          Pw = (str(r.Pw) if r.Pw else "")
          T = str(r.T)
          G = str(r.G)
          yield (Nr, Move, Coach, P, PΔ, Pw, T, G)
          prevNr = r.Nr
    rows = tuple(rowgen())
    align="CCLCCCCC"
    widths = [
        "46px",
        "46px",
        "170px",
        "46px",
        "55px",
        "55px",
        "37px",
        "37px",
    ]
    return bbcode.table(
        rows,
        align=align,
        header=header,
        widths=widths,
    )

  def content(self):
    return super().content(
        coachlowerminP = sr.settings["coach.lower.minP"],
        coachlowertable = self.coachtable("lower"),
        coachrlowerminT = self.report.coachrankings_lower_minT,
        coachuppermaxNr = sr.settings["coach.upper.maxNr"],
        coachupperminP = sr.settings["coach.upper.minP"],
        coachuppertable = self.coachtable("upper"),
        date = self.date,
        nextreportlink = self.nextreportlink,
        numcoaches = self.numcoaches,
        nummaintournaments = self.nummaintournaments,
        numteams = self.numteams,
        prevreportlink = self.prevreportlink,
        teamlowermaxrosterialNr = sr.settings[
            "team.lower.maxrosterialNr"
        ],
        teamlowerminP = sr.settings["team.lower.minP"],
        teamlowertable = self.teamtable("lower"),
        teamuppermaxNr = sr.settings["team.upper.maxNr"],
        teamupperminP = sr.settings["team.upper.minP"],
        teamuppertable = self.teamtable("upper"),
        title = self.title2,
    )

  def teamtable(self, house):
    header=[
        "Nr",
        "Move",
        "Team",
        "Roster",
        "Coach",
        "P",
        "PΔ",
        "Pw",
        "T",
        "G",
    ]
    rankings = self.report.teamfullrankings
    def rowgen():
      weekNr = self.report.weekNr
      prevNr = None
      for r in rankings:
        if getattr(r, f'{house.lower()}Nr'):
          Nr = (str(r.Nr) if r.Nr != prevNr else "")
          Move = helper.bbcmove(r.Move)
          Team = helper.bbcteam(r.Performer)
          Roster = r.Performer.roster.nameofweek(weekNr)
          Coach = helper.bbccoach(r.Performer.coach)
          P = str(r.P)
          PΔ = (str(r.PΔ) if r.PΔ else "")
          Pw = (str(r.Pw) if r.Pw else "")
          T = str(r.T)
          G = str(r.G)
          yield (Nr, Move, Team, Roster, Coach, P, PΔ, Pw, T, G)
          prevNr = r.Nr
    rows = tuple(rowgen())
    align="CCLLLCCCCC"
    widths = [
        "46px",
        "46px",
        "230px",
        "150px",
        "170px",
        "46px",
        "55px",
        "55px",
        "37px",
        "37px",
    ]
    return bbcode.table(
        rows,
        align=align,
        header=header,
        widths=widths,
    )




def all_():
  current_weekNr = sr.time.current_weekNr()
  return [
      NotePage.of_reportNr(reportNr)
      for reportNr, weekNr in sr.report.reportNrs().items()
      if weekNr <= current_weekNr
  ]


def toupdate():
  c = sr.report.current_report()
  p, n = c.prevnext
  if p:
    return [p.nr, c.nr]
  else:
    return [c.nr]
  w = sr.time.lowest_enterweekNr_of_unexited()
  y = sr.time.fumbblyear(w)
  return [wp for wp in all_() if y <= wp.fumbblyear]

