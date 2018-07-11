import sr
from .. import roman
from . import helper


class WikiPage(helper.FUMBBLYearWikiPage):
  NAME = "SR-Tournaments-Y__"

  @property
  def name(self):
    return f'SR-Tournaments-Y{self.fumbblyear}'

  @property
  def title(self):
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
            helper.tournamentnametext(T),
            T.rank,
            T.level,
            T.srformatchar,
            helper.tournamentnteamstext(T),
            T.srpointsstr,
            helper.tournamentfsgnametext(T),
            helper.tournamententerdatetext(T),
            helper.tournamentexitdatetext(T),
        ]
        for T in self.tournaments
    )
    align="LCCCCLCCC"
    return helper.table(rows, align, header)

  def content(self):
    return super().content(title=self.title, table=self.table)


def all():
  return [
      sr.pages.page["SR-Tournaments-Y__"].WikiPage(y)
      for y in list(sr.time.fumbblyears())
  ]


def toupdate():
  w = sr.time.lowest_enterweekNr_of_unexited()
  y = sr.time.fumbblyear(w)
  return [wp for wp in all() if y <= wp.fumbblyear]
