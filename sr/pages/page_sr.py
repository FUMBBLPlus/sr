import sr
from .. import roman
from . import helper


class WikiPage(helper.WikiPage):
  name = "SR"

  def content(self, updated=None):
    kwargs = {}
    if not updated:
      updated = sr.time.now()
    if hasattr(updated, "strftime"):
      timefmt = "%Y-%m-%d %H:%M"
      updated = updated.strftime(timefmt)
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
