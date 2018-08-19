import copy
import sr
from .. import roman
from .. import bbcode
from . import helper


def consecutive(reportNrs):
  series = []
  for reportNr in reportNrs:
    if series:
      if series[-1][-1] == reportNr - 1:
        series[-1].append(reportNr)
      else:
        series.append([reportNr])
    else:
      series.append([reportNr])
  if series:
    return max({len(s) for s in series})
  else:
    return 0



class NotePage(helper.NotePage):

  def content(self):
    return super().content(
        nr1coachtable = self.nr1coachtable,
        top10coachtable = self.top10coachtable,
        yearendtop3coachtable = self.yearendtop3coachtable,
    )

  @property
  def nr1coachtable(self):
    header=[
        "Coach",
        "Times",
        "Consec",
        "Last Time",
    ]
    coaches = {}
    sort_keys = {}
    current_weekNr = sr.time.current_weekNr()
    for reportNr, weekNr in sr.report.reportNrs().items():
      if current_weekNr < weekNr:
        continue
      report = sr.report.Report(reportNr)
      rankings = report.coachfullrankings
      for row in rankings:
        if 1 < row.Nr:
          break
        C = coach = row.Performer
        li = coaches.setdefault(C, [])
        li.append(reportNr)
    for coach, reportNrs in coaches.items():
      sort_keys[coach] = (
          len(reportNrs),
          consecutive(reportNrs),
          reportNrs[-1],
      )
    def rowgen():
      for coach in sorted(
          coaches, key=sort_keys.__getitem__, reverse=True
      ):
        Coach = helper.bbccoach(coach)
        times, consec, lastreportNr = sort_keys[coach]
        Times = str(times)
        Consec = str(consec)
        lasttimereport = sr.report.Report(lastreportNr)
        if lasttimereport is sr.report.current_report():
          LastTime = helper.bbcreport(
              lasttimereport,
              "CURRENT"
          )
        else:
          LastTime = helper.bbcreport(
              lasttimereport,
              lasttimereport.enddate.strftime(
                  sr.time.ISO_DATE_FMT
              )
          )
        if lasttimereport is sr.report.current_report():
          Coach = bbcode.b(Coach)
          Times = bbcode.b(Times)
          Consec = bbcode.b(Consec)
          LastTime = bbcode.b(LastTime)
        yield Coach, Times, Consec, LastTime
    rows = tuple(rowgen())
    align="LCCC"
    widths = [
        "170px",
        "60px",
        "60px",
        "80px",
    ]
    return bbcode.table(
        rows,
        align=align,
        header=header,
        widths=widths,
    )

  @property
  def top10coachtable(self):
    header=[
        "Coach",
        "Times",
        "Consec",
        "Best",
        "Last Time",
    ]
    coaches = {}
    best = {}
    sort_keys = {}
    current_weekNr = sr.time.current_weekNr()
    for reportNr, weekNr in sr.report.reportNrs().items():
      if current_weekNr < weekNr:
        continue
      report = sr.report.Report(reportNr)
      rankings = report.coachfullrankings
      for row in rankings:
        if 10 < row.Nr:
          break
        C = coach = row.Performer
        li = coaches.setdefault(C, [])
        li.append(reportNr)
        best[C] = min(best.setdefault(C, 999), row.Nr)
    for coach, reportNrs in coaches.items():
      sort_keys[coach] = (
          len(reportNrs),
          consecutive(reportNrs),
          -best[coach],
          reportNrs[-1],
      )
    def rowgen():
      for coach in sorted(
          coaches, key=sort_keys.__getitem__, reverse=True
      ):
        Coach = helper.bbccoach(coach)
        times, consec, mbest, lastreportNr = sort_keys[coach]
        Times = str(times)
        Consec = str(consec)
        Best = str(best[coach])
        lasttimereport = sr.report.Report(lastreportNr)
        if lasttimereport is sr.report.current_report():
          LastTime = helper.bbcreport(
              lasttimereport,
              "CURRENT"
          )
        else:
          LastTime = helper.bbcreport(
              lasttimereport,
              lasttimereport.enddate.strftime(
                  sr.time.ISO_DATE_FMT
              )
          )
        if lasttimereport is sr.report.current_report():
          Coach = bbcode.b(Coach)
          Times = bbcode.b(Times)
          Consec = bbcode.b(Consec)
          Best = bbcode.b(Best)
          LastTime = bbcode.b(LastTime)
        yield Coach, Times, Consec, Best, LastTime
    rows = tuple(rowgen())
    align="LCCCC"
    widths = [
        "170px",
        "60px",
        "60px",
        "46px",
        "80px",
    ]
    return bbcode.table(
        rows,
        align=align,
        header=header,
        widths=widths,
    )

  @property
  def yearendtop3coachtable(self):
    header=[
        "Year",
        "No. 1",
        "No. 2",
        "No. 3",
    ]
    def rowgen():
      fumbblyears = sorted(list(sr.time.fumbblyears()))[:-1]
      for fumbblyear in reversed(fumbblyears):
        weekNrs = sr.time.fumbblyears()[fumbblyear]
        weekNr = weekNrs.stop - 1  # weekNrs is a range object
        report = sr.report.Report.ofweekNr(weekNr)
        rankings = report.coachfullrankings
        Year = helper.bbcnoteurl(
            f'SR-Reports-Y{fumbblyear}',
            roman.to_roman(fumbblyear),
        )
        coaches = [None, [], [], []]
        for row in rankings:
          if 3 < row.Nr:
            break
          coaches[row.Nr].append(helper.bbccoach(row.Performer))
        yield (
            Year,
            "\n".join(bbcode.b(c) for c in coaches[1]),
            "\n".join(coaches[2]),
            "\n".join(coaches[3]),
        )
    rows = tuple(rowgen())
    align="CLLL"
    widths = [
        "60px",
        "170px",
        "170px",
        "170px",
    ]
    return bbcode.table(
        rows,
        align=align,
        header=header,
        widths=widths,
    )


NotePage = NotePage("SR-Coach-Records")  # singleton
