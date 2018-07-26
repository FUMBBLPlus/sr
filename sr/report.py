import collections

import sr


@sr.helper.idkey("nr")
class Report(metaclass=sr.helper.InstanceRepeater):

  RankingsRow = collections.namedtuple(
      "RankingsRow",
      ["rownum", "nr", "slotobj"]
  )

  @classmethod
  def _get_key(cls, nr):
    nr = int(nr)
    # next line raises KeyError for nonexisting reports
    weekNr = reportNrs()[nr]
    return nr

  @classmethod
  @sr.helper.default_from_func("weekNr", sr.time.current_weekNr)
  def ofweekNr(cls, weekNr):
    nr = weekNrs()[weekNr]
    return cls(nr)

  def __init__(self, nr: int):
    self._coachrankings = None
    self._teamrankings = None

  def _rankings(self, name):
    attr = f'_{name}rankings'
    if getattr(self, attr) is None:
      performancesattr = f'{name}performances'
      slotsattr = f'{name}slots'
      slotscls = getattr(sr.slot, f'{name.title()}Slots')
      for P in getattr(self, performancesattr):
        A = getattr(P, name)
        S = slotscls(A.id, self.weekNr)
        S.add(P)
      setattr(self, attr, {})
      prev_sort_key = None
      nr = 0
      for rownum, S in enumerate(getattr(self, slotsattr), 1):
        A = getattr(S, name)
        this_sort_key = S.sort_key[0]
        # sort_key[1] are names which are no tiebreakers
        if this_sort_key != prev_sort_key:
          nr = rownum
        getattr(self, attr)[A] = self.RankingsRow(rownum, nr, S)
        prev_sort_key = this_sort_key
    return getattr(self, attr)

  @property
  def coaches(self):
    return {C for T in self.tournaments for C in T.coaches}

  @property
  def coachperformances(self):
    return sorted({
        CP for T in self.tournaments
        for CP in T.allcoachperformances
        if T.ismain
    }, key=lambda CP: CP.sort_key)

  @property
  def coachslots(self):
    return sorted({
        sr.slot.CoachSlots(C.id, self.weekNr)
        for C in self.coaches
    }, key=lambda CS: CS.sort_key)

  @property
  def coachrankings(self):
    return self._rankings("coach")

  @property
  def date(self):
    return sr.time.firstdate(self.weekNr)

  @property
  def enters(self):
    return sr.tournament.enters(self.weekNr)

  @property
  def exits(self):
    return sr.tournament.enters(self.weekNr)

  @property
  def prevnext(self):
    p, n = None, None
    if self.nr - 1 in reportNrs():
      p = self.__class__(self.nr - 1)
    if self.nr + 1 in reportNrs():
      n = self.__class__(self.nr + 1)
    return p, n

  @property
  def tournaments(self):
    return sr.tournament.ofweekNr(self.weekNr)

  @property
  def fumbblyear(self):
    return sr.time.fumbblyear(self.weekNr)

  @property
  def teams(self):
    return {Te for T in self.tournaments for Te in T.teams}

  @property
  def teamperformances(self):
    return sorted({
        TP for T in self.tournaments
        for TP in T.allteamperformances
        if T.ismain
    }, key=lambda TP: TP.sort_key)

  @property
  def teamslots(self):
    return sorted({
        sr.slot.TeamSlots(Te.id, self.weekNr)
        for Te in self.teams
    }, key=lambda TS: TS.sort_key)

  @property
  def teamrankings(self):
    return self._rankings("team")

  @property
  def weekNr(self):
    return reportNrs()[self.nr]



def current_report():
  return Report.ofweekNr()



_weekNrs_reportNrs = ...
def weekNrs(*, rebuild=False):
  global _weekNrs_reportNrs
  if _weekNrs_reportNrs is ... or rebuild:
    r = set()
    # reports are based on (srdata) added tournaments
    for T in sr.tournament.added():
      if T.ismain and T.srenterweekNr is not None:
        r.add(T.srenterweekNr)
        if T.srexitweekNr is not None:
          r.add(T.srexitweekNr)
    max_weekNr = sr.time.current_weekNr() + 1
    weekNrs_ = tuple(sorted({w for w in r if w <= max_weekNr}))
    _weekNrs_reportNrs = ({},{})
    for nr, weeknr in enumerate(weekNrs_, 1):
      _weekNrs_reportNrs[0][weeknr] = nr
      _weekNrs_reportNrs[1][nr] = weeknr
  return _weekNrs_reportNrs[0]
def reportNrs(*, rebuild=False):
  if _weekNrs_reportNrs is ... or rebuild:
    weekNrs(rebuild=rebuild)
  return _weekNrs_reportNrs[1]
