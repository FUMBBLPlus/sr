import copy
import sr
from .. import roman
from .. import bbcode
from . import helper


from .page_sr_coach_records import consecutive



class NotePage(helper.NotePage):

  def content(self):
    return super().content(
        nr1teamtable = self.nr1teamtable,
        top10teamtable = self.top10teamtable,
        yearendtop3teamtable = self.yearendtop3teamtable,
    )

  @property
  def nr1teamtable(self):
    header=[
        "Team",
        "Roster",
        "Coach",
        "Times",
        "Consec",
        "Last Time",
    ]
    teams = {}
    sort_keys = {}
    current_weekNr = sr.time.current_weekNr()
    for reportNr, weekNr in sr.report.reportNrs().items():
      if current_weekNr < weekNr:
        continue
      report = sr.report.Report(reportNr)
      rankings = report.teamfullrankings
      for row in rankings:
        if 1 < row.Nr:
          break
        C = team = row.Performer
        li = teams.setdefault(C, [])
        li.append(reportNr)
    for team, reportNrs in teams.items():
      sort_keys[team] = (
          len(reportNrs),
          consecutive(reportNrs),
          reportNrs[-1],
      )
    def rowgen():
      for team in sorted(
          teams, key=sort_keys.__getitem__, reverse=True
      ):
        Team = helper.bbcteam(team)
        Coach = helper.bbccoach(team.coach)
        times, consec, lastreportNr = sort_keys[team]
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
        Roster = team.roster.nameofweek(lasttimereport.weekNr)
        if lasttimereport is sr.report.current_report():
          Team = bbcode.b(Team)
          Roster = bbcode.b(Roster)
          Coach = bbcode.b(Coach)
          Times = bbcode.b(Times)
          Consec = bbcode.b(Consec)
          LastTime = bbcode.b(LastTime)
        yield Team, Roster, Coach, Times, Consec, LastTime
    rows = tuple(rowgen())
    align="LLLCCC"
    widths = [
        "230px",
        "150px",
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
  def top10teamtable(self):
    header=[
        "Team",
        "Roster",
        "Coach",
        "Times",
        "Consec",
        "Best",
        "Last Time",
    ]
    teams = {}
    best = {}
    sort_keys = {}
    current_weekNr = sr.time.current_weekNr()
    for reportNr, weekNr in sr.report.reportNrs().items():
      if current_weekNr < weekNr:
        continue
      report = sr.report.Report(reportNr)
      rankings = report.teamfullrankings
      for row in rankings:
        if 10 < row.Nr:
          break
        Te = team = row.Performer
        li = teams.setdefault(Te, [])
        li.append(reportNr)
        best[Te] = min(best.setdefault(Te, 999), row.Nr)
    for team, reportNrs in teams.items():
      sort_keys[team] = (
          len(reportNrs),
          consecutive(reportNrs),
          -best[team],
          reportNrs[-1],
      )
    def rowgen():
      for team in sorted(
          teams, key=sort_keys.__getitem__, reverse=True
      ):
        Team = helper.bbcteam(team)
        Coach = helper.bbccoach(team.coach)
        times, consec, mbest, lastreportNr = sort_keys[team]
        Times = str(times)
        Consec = str(consec)
        Best = str(best[team])
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
        Roster = team.roster.nameofweek(lasttimereport.weekNr)
        if lasttimereport is sr.report.current_report():
          Team = bbcode.b(Team)
          Roster = bbcode.b(Roster)
          Coach = bbcode.b(Coach)
          Times = bbcode.b(Times)
          Consec = bbcode.b(Consec)
          Best = bbcode.b(Best)
          LastTime = bbcode.b(LastTime)
        yield Team, Roster, Coach, Times, Consec, Best, LastTime
    rows = tuple(rowgen())
    align="LLLCCCC"
    widths = [
        "230px",
        "150px",
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
  def yearendtop3teamtable(self):
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
        rankings = report.teamfullrankings
        Year = helper.bbcnoteurl(
            f'SR-Reports-Y{fumbblyear}',
            roman.to_roman(fumbblyear),
        )
        teams = [None, [], [], []]
        for row in rankings:
          if 3 < row.Nr:
            break
          team = row.Performer
          Team = helper.bbcteam(team)
          if row.Nr == 1:
            Team = bbcode.b(Team)
          Roster = team.roster.nameofweek(report.weekNr)
          Coach = helper.bbccoach(team.coach)
          teams[row.Nr].append(
            Team
            + "\n"
            + bbcode.size(f'{Roster} ({Coach})', 9)
          )
        yield (
            Year,
            "\n".join(teams[1]),
            "\n".join(teams[2]),
            "\n".join(teams[3]),
        )
    rows = tuple(rowgen())
    align="CLLL"
    widths = [
        "60px",
        "230px",
        "230px",
        "230px",
    ]
    return bbcode.table(
        rows,
        align=align,
        header=header,
        widths=widths,
    )


NotePage = NotePage("SR-Team-Records")  # singleton
