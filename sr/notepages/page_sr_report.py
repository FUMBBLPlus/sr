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
  def coachbelow(self):
    if self.COACHMINPTS <= 0:
      return ""
    n = len([
        R for R in self.report.coachrankings.values()
        if R.slotobj.totalpoints < self.COACHMINPTS
    ])
    if self.COACHMINPTS == 1:
      limit = f'1 point'
    else:
      limit = f'{self.COACHMINPTS} points'
    if n == 1:
      text = f'1 coach below {limit}'
    elif 1 < n:
      text = f'{n} coaches below {limit}'
    else:
      return ""
    return "\n" + bbcode.center(text)

  @property
  def coachtable(self):
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
    rankings = self.report.coachrankings  # differs
    rows = []
    for C in sorted(rankings, key=rankings.get):  # differs
      R = rankings[C]  # differs
      if R.slotobj.totalpoints < self.COACHMINPTS:
        continue
      nr = (str(R.nr) if R.rownum == R.nr else "")
      move = bbcode.size(8, "NEW")
      coach = helper.bbccoach(C)
      P = str(R.slotobj.totalpoints)
      PΔ = ""
      Pw = ""
      if R.slotobj.wastedpoints:
        Pw = str(R.slotobj.wastedpoints)
      Tval, Gval = 0, 0
      for item in R.slotobj.performances.items():
        perfobj, (slotgroup, slotnr) = item
        if slotgroup is sr.slot.SlotGroup("NE"):
            continue
        Tval += 1
        Gval += perfobj.totalnummatches
      T = str(Tval)
      G = str(Gval)
      pR = None
      prevreport = self.report.prevnext[0]
      if prevreport:
        pR = prevreport.coachrankings.get(C)  # differs
      if pR:
          moveval = pR.nr - R.nr
          if 0 < moveval:
            move = f'↑{bbcode.size(moveval, 8)}'
          elif moveval < 0:
            move = f'↓{bbcode.size(abs(moveval), 8)}'
          else:
            move = ""
          PΔval = R.slotobj.totalpoints
          PΔval -= pR.slotobj.totalpoints
          if PΔval:
            PΔ = str(PΔval)
      rows.append([nr, move, coach, P, PΔ, Pw, T, G])
    align="CCLCCCCC"
    widths = [
        "46px",
        "46px",
        "170x",
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
        date = self.date,
        nextreportlink = self.nextreportlink,
        prevreportlink = self.prevreportlink,
        title = self.title2,
        coachbelow = self.coachbelow,
        coachtable = self.coachtable,
        teambelow = self.teambelow,
        teamtable = self.teamtable,
    )

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
  def teambelow(self):
    if self.TEAMNRCUTOFF <= 0:
      return ""
    n = len([
        R for R in self.report.teamrankings.values()
        if self.TEAMNRCUTOFF < R.nr
    ])
    if n == 1:
      text = f'1 team below'
    elif 1 < n:
      text = f'{n} teams below'
    else:
      return ""
    return "\n" + bbcode.center(text)

  @property
  def teamtable(self):
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
    rankings = self.report.teamrankings  # differs
    rows = []
    for Te in sorted(rankings, key=rankings.get):  # differs
      R = rankings[Te]  # differs
      if self.TEAMNRCUTOFF < R.nr:
        break
      Ro = Te.roster  # differs
      C = Te.coach  # differs
      nr = (str(R.nr) if R.rownum == R.nr else "")
      move = bbcode.size(8, "NEW")
      team = helper.bbcteam(Te)
      roster = Ro.nameofweek(self.report.weekNr)
      coach = helper.bbccoach(C)
      P = str(R.slotobj.totalpoints)
      PΔ = ""
      Pw = ""
      if R.slotobj.wastedpoints:
        Pw = str(R.slotobj.wastedpoints)
      Tval, Gval = 0, 0
      for item in R.slotobj.performances.items():
        perfobj, (slotgroup, slotnr) = item
        if slotgroup is sr.slot.SlotGroup("NE"):
            continue
        Tval += 1
        Gval += perfobj.totalnummatches
      T = str(Tval)
      G = str(Gval)
      pR = None
      prevreport = self.report.prevnext[0]
      if prevreport:
        pR = prevreport.teamrankings.get(Te)  # differs
      if pR:
          moveval = pR.nr - R.nr
          if 0 < moveval:
            move = f'↑{bbcode.size(moveval, 8)}'
          elif moveval < 0:
            move = f'↓{bbcode.size(abs(moveval), 8)}'
          else:
            move = ""
          PΔval = R.slotobj.totalpoints
          PΔval -= pR.slotobj.totalpoints
          if PΔval:
            PΔ = str(PΔval)
      rows.append([
          nr, move, team, roster, coach, P, PΔ, Pw, T, G
      ])
    align="CCLLLCCCCC"
    widths = [
        "46px",
        "46px",
        "230x",
        "150x",
        "170x",
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

  @property
  def title2(self):
    return f'OBC Sport SR Rankings Report {self.nr}'




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

