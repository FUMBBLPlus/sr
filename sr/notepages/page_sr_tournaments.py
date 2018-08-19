import sr
from .. import bbcode
from .. import roman
from . import helper


class NotePage(helper.FUMBBLYearNotePage):

  KEY = "SR-Tournaments-Yn"
  NAME = "Tournaments"

  def content(self):
    return super().content(
        date = self.datestr,
        title = self.title2,
        table = self.table,
    )

  @property
  def table(self):
    header=[
        "Name",
        "Fmt",
        "Rnk",
        "Lvl",
        "Tms",
        "Points",
        "FSG",
        "In Date",
        "Out Date",
    ]
    rows = list(
        [
            helper.bbctournament(T),
            T.srformatchar,
            T.rank,
            T.level,
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

  @property
  def title2(self):
    return (
        "Tournaments of FUMBBL Year "
        f'{roman.to_roman(self.fumbblyear)}'
    )

  @property
  def tournaments(self):
    return sr.tournament.sort(
        sr.tournament.offumbblyear(self.fumbblyear),
        reverse=True,
    )
