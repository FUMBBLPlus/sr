import sr
from .. import bbcode
from .. import roman
from . import helper


class NotePage(helper.FUMBBLYearNotePage):

  KEY = "SR-Reports-Yn"
  NAME = "Reports"

  def content(self):
    return super().content(
        date = self.datestr,
        title = self.title2,
        table = self.table,
    )

  @property
  def table(self):
    header=[
        "Report",
        "Tournaments Entered",
        "Tournaments Exited",
        "Top 3 Coaches",
        "Top 3 Teams",
    ]
    def rowgen():
      current_weekNr = sr.time.current_weekNr()
      current_report = sr.report.current_report()
      for report in self.reports:
        ReportLines = []
       #if report.weekNr <= current_weekNr:
       #  ReportLines.append(helper.bbcreport(report))
       #else:
       #  ReportLines.append(f'{report.nr}')
        ReportLines.append(f'{report.nr}')
        ReportLines.append(
            report.date.strftime(sr.time.ISO_DATE_FMT)
        )
        if report.weekNr <= current_weekNr:
          Report = helper.bbcreport(
              report, "\n".join(ReportLines)
          )
        else:
          Report = "\n".join(ReportLines)
        if report is current_report:
          Report = bbcode.b(Report)
        tournaments = {}
        for name in ("enters", "exits"):
          tournaments[name] = [
            helper.bbctournament(T)
            for T in sr.tournament.sortwithoutenterweekNr(
                getattr(report, name)
            )
            if T.ismain
          ]
          if current_weekNr < report.weekNr:
            tournaments[name].append("…")
        if current_weekNr < report.weekNr:
          dots = bbcode.center("…")
          tops = {"coach": [dots], "team": [dots]}
        else:
          top3objs = {"coach": [], "team": []}
          tops = {}
          for name, li in top3objs.items():
            rankings = getattr(report, f'{name}fullrankings')
            for R in rankings:
              if 3 < R.Nr:
                break
              li.append((R.Nr, R.Performer))
            bbcfunc = getattr(helper, f'bbc{name}')
            tops[name] = [
              f'{Nr}. {bbcfunc(Performer)}'
              for Nr, Performer in top3objs[name]
            ]
            if tops[name]:
              tops[name][0] = bbcode.b(tops[name][0])
        yield [
            Report,
            "\n".join(tournaments["enters"]),
            "\n".join(tournaments["exits"]),
            "\n".join(tops["coach"]),
            "\n".join(tops["team"]),
        ]
    rows = list(rowgen())
    align="CCCLL"
    widths = [
        "80px",
        "205px",
        "205px",
        "205px",
        "235px",
    ]
    return bbcode.table(
        rows,
        align=align,
        header=header,
        widths=widths,
    )

  @property
  def title2(self):
    return (
        "OBC Sport SR Rankings Reports of FUMBBL Year "
        f'{roman.to_roman(self.fumbblyear)}'
    )
