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

  @property
  def numcoachesteams(self):
    numcoaches = len(self.report.coachrankings)
    numteams =  len(self.report.teamrankings)
    return f'Coaches: {numcoaches} | Teams: {numteams}'

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

  def coachtable(self,
        nrrange = range(1, 999999999),
        ptsrange = range(0, 999999999),
        tournamentnrrange = range(1, 999999999),
    ):
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
    rankings = self.report.coachrankings
    rows = []
    prevnr = None
    for C in sorted(rankings, key=rankings.get):
      R = rankings[C]  # differs
      if R.nr not in nrrange:
        continue
      move = bbcode.size("NEW", 8)
      coach = helper.bbccoach(C)
      Pval = R.slotobj.totalpoints
      if Pval not in ptsrange:
        continue
      P = str(Pval)
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
      if Tval not in tournamentnrrange:
        continue
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
      nr = (str(R.nr) if R.nr != prevnr else "")
      prevnr = R.nr
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
        coachlowertable = self.coachtable(
            nrrange = range(101, 999999999),
            ptsrange = range(25, 999999999),
            tournamentnrrange = range(6, 999999999),
        ),
        coachuppertable = self.coachtable(
            nrrange = range(1, 101),
            ptsrange = range(25, 999999999),
        ),
        date = self.date,
        nextreportlink = self.nextreportlink,
        numcoachesteams = self.numcoachesteams,
        prevreportlink = self.prevreportlink,
        title = self.title2,
        teamlowertable = self.teamtable(
            nrrange = range(26, 999999999),
            rosterialnrrange = range(1, 4),
        ),
        teamuppertable = self.teamtable(
            nrrange = range(1, 26),
            ptsrange = range(25, 999999999),
        ),
    )

  def teamtable(self,
        nrrange = range(1, 999999999),
        ptsrange = range(0, 999999999),
        tournamentnrrange = range(1, 999999999),
        rosterialnrrange = range(1, 999999999),
    ):
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
    rankings = self.report.teamrankings
    rows = []
    rosterials = {}
    prevnr = None
    for Te in sorted(rankings, key=rankings.get):
      R = rankings[Te]
      Ro = Te.roster
      roster = Ro.nameofweek(self.report.weekNr)
      if roster not in rosterials:
        rosterials[roster] = []
      rosterials[roster].append(Te)
      rosterialnr = len(rosterials[roster])
      if R.nr not in nrrange:
        continue
      if rosterialnr not in rosterialnrrange:
        continue
      C = Te.coach
      move = bbcode.size("NEW", 8)
      team = helper.bbcteam(Te)
      coach = helper.bbccoach(C)
      Pval = R.slotobj.totalpoints
      if Pval not in ptsrange:
        continue
      P = str(Pval)
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
      if Tval not in tournamentnrrange:
        continue
      T = str(Tval)
      G = str(Gval)
      pR = None
      prevreport = self.report.prevnext[0]
      if prevreport:
        pR = prevreport.teamrankings.get(Te)
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
      nr = (str(R.nr) if R.nr != prevnr else "")
      prevnr = R.nr
      rows.append([
          nr, move, team, roster, coach, P, PΔ, Pw, T, G
      ])
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

