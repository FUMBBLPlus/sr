import sr
from .. import bbcode
from .. import roman
from . import helper


class NotePage(helper.FUMBBLYearNotePage):

  @property
  def tournaments(self):
    return sr.tournament.sort(sr.tournament.pending())

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
        ]
        for T in self.tournaments
    )
    align="LCCCCLC"
    widths = [
        "220px",
        "46px",
        "46px",
        "46px",
        "46px",
        "280px",
        "46px",
    ]
    return bbcode.table(
        rows,
        align=align,
        header=header,
        widths=widths,
    )

  def content(self):
    return super().content(table=self.table)

NotePage = NotePage("SR-Tournaments-Pending")  # singleton
