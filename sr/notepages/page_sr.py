import sr
from .. import roman
from . import helper


class NotePage(helper.NotePage):

  def content(self, updated=None):
    kwargs = {}
    if not updated:
      updated = sr.time.now()
    if hasattr(updated, "strftime"):
      tfmt = f'{sr.time.ISO_DATE_FMT} {sr.time.ISO_TIME_FMT_M}'
      updated = updated.strftime(tfmt)
    kwargs["updated"] = updated
    kwargs["weeknr"] = w = sr.time.current_weekNr()
    current_report = sr.report.Report(w)
    kwargs["current_report_nr"] = current_report.nr
    fumbblyears = sorted(sr.time.fumbblyears(), reverse=True)
    rnote = sr.notepages.page["SR-Reports-Y__"].NotePage
    reports = [rnote.of_fumbblyear(16) for y in fumbblyears]
    tnote = sr.notepages.page["SR-Tournaments-Y__"].NotePage
    tournaments = [tnote.of_fumbblyear(16) for y in fumbblyears]
    kwargs["reports"] = "\n | \\\n".join(
        f'[url={p.url}]{roman.to_roman(p.fumbblyear)}[/url]\\'
        for p in reports
    )
    kwargs["tournaments"] = "\n | \\\n".join(
        f'[url={p.url}]{roman.to_roman(p.fumbblyear)}[/url]\\'
        for p in tournaments
    )
    return super().content(**kwargs)

NotePage = NotePage("SR")  # singleton
