import sr


@sr.helper.idkey("weekNr")
class Report(metaclass=sr.helper.InstanceRepeater):

  def __init__(self, weekNr: int):
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
      n = 0
      for k, S in enumerate(getattr(self, slotsattr), 1):
        A = getattr(S, name)
        this_sort_key = S.sort_key[0]
        # sort_key[1] are names which are no tiebreakers
        if this_sort_key != prev_sort_key:
          n = k
        getattr(self, attr)[A] = k, n, S
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
  def nr(self):
    return weekNrs().index(self.weekNr) + 1

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

