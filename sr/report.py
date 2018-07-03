import sr


@sr.helper.idkey("weekNr")
class Report(metaclass=sr.helper.InstanceRepeater):

  def __init__(self, weekNr: int):
    pass

  @property
  def enters(self):
    return sr.tournament.enters(self.weekNr)

  @property
  def exits(self):
    return sr.tournament.enters(self.weekNr)

  @property
  def nr(self):
    return weekNrs().index(self.weekNr)

  @property
  def tournaments(self):
    return sr.tournament.ofweekNr(self.weekNr)




def current_report():
  return Report(sr.time.current_weekNr())




_weekNrs = ...
def weekNrs(*, rebuild=False):
  global _weekNrs
  if _weekNrs is ... or rebuild:
    r = set()
    # reports are based on (srdata) added tournaments
    for T in sr.tournament.added():
      if T.ismain and T.srenterweekNr is not None:
        r.add(T.srenterweekNr)
        if T.srexitweekNr is not None:
          r.add(T.srexitweekNr)
    max_weekNr = sr.time.current_weekNr() + 1
    _weekNrs = tuple(sorted({w for w in r if w <= max_weekNr}))
  return _weekNrs

