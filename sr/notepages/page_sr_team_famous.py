import copy
import sr
from .. import roman
from .. import bbcode
from . import helper


class NotePage(helper.NotePage):

  def content(self):
    return super().content(
        table = self.table,
    )

  @property
  def table(self):
    header=[
        "#",
        "Team",
        "Roster",
        "Coach",
        "F",
        "U",
        "L",
        "Best",
    ]
    famous = {}
    upper = {}
    lower = {}
    best = {}
    sort_keys = {}
    lastreports = {}
    current_weekNr = sr.time.current_weekNr()
    for reportNr, weekNr in sr.report.reportNrs().items():
      if current_weekNr < weekNr:
        continue
      report = sr.report.Report(reportNr)
      rankings = report.teamfullrankings
      for row in rankings:
        Pe = row.Performer
        lastreports[Pe] = report
        currbest = best.get(Pe, (999999999, None))[0]
        if row.Nr <= currbest:
          best[Pe] = (row.Nr, reportNr)
        if row.upperNr:
          li = upper.setdefault(Pe, [])
        elif row.lowerNr:
          li = lower.setdefault(Pe, [])
        else:
          continue
        li.append(reportNr)
    for Pe in set(upper) | set(lower):
      famous[Pe] = 0
      famous[Pe] += len(upper.get(Pe, [])) * 2
      famous[Pe] += len(lower.get(Pe, []))
    for Pe, F in famous.items():
      sort_keys[Pe] = (
        -F,
        -len(upper.get(Pe, [])),
        best.get(Pe, (999999999, None))[0],
        Pe.name,
      )
    def rowgen():
      prev_sort_key = None
      for rownum, Pe in enumerate(
          sorted(famous, key=sort_keys.__getitem__), 1
      ):
        sort_key = sort_keys[Pe]
        if prev_sort_key and sort_key[:-1] == prev_sort_key:
          N = ""
        else:
          N = str(rownum)
        Fval = famous[Pe]
        if Fval < 100:
          break
        Team = helper.bbcteam(Pe)
        Coach = helper.bbccoach(Pe.coach)
        F = str(famous[Pe])
        UL = {}
        for k, d in (("upper", upper), ("lower", lower)):
          value = len(d.get(Pe, []))
          if value:
            report = sr.report.Report(d[Pe][-1])
            s = helper.bbcreport(report, value)
          else:
            s = ""
          UL[k] = s
        bestval, bestreoprtNr = best[Pe]
        bestreport = sr.report.Report(bestreoprtNr)
        Best = helper.bbcreport(bestreport, bestval)
        Roster = Pe.roster.nameofweek(lastreports[Pe].weekNr)
        yield (
            N,
            Team,
            Roster,
            Coach,
            F,
            UL["upper"],
            UL["lower"],
            Best
        )
        prev_sort_key = sort_key[:-1]
    rows = tuple(rowgen())
    align="CLLLCCCC"
    widths = [
        "46px",
        "230px",
        "150px",
        "170px",
        "46px",
        "46px",
        "46px",
        "46px",
    ]
    return bbcode.table(
        rows,
        align=align,
        header=header,
        widths=widths,
    )




NotePage = NotePage("SR-Team-Famous")  # singleton
