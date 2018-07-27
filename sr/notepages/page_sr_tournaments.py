import sr
from .. import bbcode
from .. import roman
from . import helper


class NotePage(helper.FUMBBLYearNotePage):

  KEY = "SR-Tournaments-Y__"
  NAME = "Tournaments"

  @property
  def date(self):
    fromdatestr = self.fromdate.strftime(sr.time.ISO_DATE_FMT)
    todate = self.todate
    if todate is not None:
      todatestr = todate.strftime(sr.time.ISO_DATE_FMT)
      return f'from {fromdatestr} to {todatestr}'
    else:
      return f'from {fromdatestr}'

  @property
  def title2(self):
    return (
        "OBC Sport SR Rankings Tournaments of FUMBBL Year "
        f'{roman.to_roman(self.fumbblyear)}'
    )

  @property
  def tournaments(self):
    return sr.tournament.sort(
        sr.tournament.offumbblyear(self.fumbblyear),
        reverse=True,
    )

  @property
  def table(self):
    header=[
        "Name",
        "Rnk",
        "Lvl",
        "Fmt",
        "Tms",
        "Points",
        "FSG",
        "Enter Date",
        "Exit Date",
    ]
    rows = list(
        [
            helper.bbctournament(T),
            T.rank,
            T.level,
            T.srformatchar,
            helper.bbcnteams(T),
            T.srpointsstr,
            helper.bbcfsgname(T),
            helper.bbcenterdate(T),
            helper.bbcexitdate(T),
        ]
        for T in self.tournaments
    )
    align="LCCCCLCCC"
    widths = [
        "220px",
        "46px",
        "46px",
        "46px",
        "46px",
        "280px",
        "46px",
        "110px",
        "110px",
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
        title = self.title2,
        table = self.table,
    )


def all_():
  return [
      NotePage.of_fumbblyear(y)
      for y in list(sr.time.fumbblyears())
  ]


def toupdate():
  w = sr.time.lowest_enterweekNr_of_unexited()
  y = sr.time.fumbblyear(w)
  return [wp for wp in all_() if y <= wp.fumbblyear]
