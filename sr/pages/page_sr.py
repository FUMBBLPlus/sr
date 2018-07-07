import sr
from .. import roman
from . import helper


class WikiPage(helper.WikiPage):
  NAME = "SR"
  name = NAME

  def content(self, updated=None):
    kwargs = {}
    if not updated:
      updated = sr.time.now()
    if hasattr(updated, "strftime"):
      tfmt = f'{sr.time.ISO_DATE_FMT} {sr.time.ISO_TIME_FMT_M}'
      updated = updated.strftime(tfmt)
    kwargs["updated"] = updated
    kwargs["weeknr"] = sr.time.current_weekNr()
    kwargs["reports"] = " | ".join(
        f'[{roman.to_roman(y)}|SR-Reports-Y{y}]'
        for y in sorted(sr.time.fumbblyears(), reverse=True)
    )
    tournaments = [
        f'[{roman.to_roman(y)}|SR-Tournaments-Y{y}]'
        for y in sorted(sr.time.fumbblyears(), reverse=True)
    ]
    tournaments.insert(0, "[Pending|SR-PendingTournaments]")
    kwargs["tournaments"] = " | ".join(tournaments)
    return super().content(**kwargs)
