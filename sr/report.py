import sr


class Report(metaclass=sr.helper.InstanceRepeater):

  def __init__(self, weeknr: int):
    pass

  def __repr__(self):
    return f'Report({self.weeknr})'

  @property
  def enters(self):
    return sr.tournament.enters(self.weeknr)

  @property
  def exits(self):
    return sr.tournament.enters(self.weeknr)

  @property
  def nr(self):
    return weeknrs().index(self.weeknr)

  @property
  def tournaments(self):
    return sr.tournament.ofweeknr(self.weeknr)

  @property
  def weeknr(self):
    return self._KEY[0]  # set by metaclass




def current_report():
  return Report(sr.time.current_weeknr())




_weeknrs = ...
def weeknrs(*, rebuild=False):
  global _weeknrs
  if _weeknrs is ... or rebuild:
    r = set()
    for T in sr.tournament.added():
      if T.ismain and T.srenterweeknr is not None:
        r.add(T.srenterweeknr)
        if T.srexitweeknr is not None:
          r.add(T.srexitweeknr)
    max_weeknr = sr.time.current_weeknr() + 1
    _weeknrs = tuple(sorted({w for w in r if w <= max_weeknr}))
  return _weeknrs

