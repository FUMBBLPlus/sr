import collections
import math

import sr


@sr.helper.idkey("nr")
class Report(metaclass=sr.helper.InstanceRepeater):

  UpperNrRanges = {
      "coach": range(1, 101),
      "team": range(1, 26),
  }

  UpperPtsRanges = {
      "coach": range(25, 999999999),
      "team": range(25, 999999999),
  }

  LowerNrRanges = {
      "coach": range(1, 101),
      "team": range(1, 26),
  }

  RankingsRow = collections.namedtuple(
      "RankingsRow",
      ["rownum", "nr", "slotobj"]
  )
  FullRankingsRow = collections.namedtuple(
      "FullRankingsRow",
      [
          "rownum",
          "Nr", "Move", "Performer", "P", "PΔ", "Pw", "T", "G",
          "upperNr", "lowerNr",
      ]
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
    nr = None
    weekNr = weekNr
    weekNrs_ = weekNrs()
    while not nr:
      nr = weekNrs_.get(weekNr)
      weekNr -= 1
    return cls(nr)

  def __init__(self, nr: int):
    self._coachfullrankings = None
    self._coachrankings = None
    self._teamrankings = None
    self._teamfullrankings = None

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

  def _iter_fullrankings(self, name):
    upperPerformers = []
    lowerPerformers = []
    upper_maxNr = sr.settings[f'{name}.upper.maxNr']
    upper_minP = sr.settings[f'{name}.upper.minP']
    lower_minP = sr.settings[f'{name}.lower.minP']
    if name == "coach":
      lower_minT = self.coachrankings_lower_minT
    elif name == "team":
      lower_maxrosterialNr = sr.settings[
          f'{name}.lower.maxrosterialNr'
      ]
      rosterials = {}
    rankings = getattr(self, f'{name}rankings')
    for Performer in sorted(rankings, key=rankings.get):
      R = rankings[Performer]
      rownum = R.rownum
      Nr = R.nr
      if name == "team":
        roster = Performer.roster.nameofweek(self.weekNr)
        rosterialPerformers = rosterials.setdefault(
            roster, []
        )
        rosterialPerformers.append((Performer, Nr))
        rosterialNr = len(rosterialPerformers)
        for _, Nr_ in reversed(rosterialPerformers[:-1]):
          if Nr_ == Nr:
            rosterialNr -= 1
          else:
            break
      Move = math.inf  # new coach by default
      P = R.slotobj.totalpoints
      PΔ = 0
      Pw = R.slotobj.wastedpoints
      T = 0
      G = 0
      upperNr = 0
      lowerNr = 0
      prevreport = self.prevnext[0]
      if prevreport:
        prevrankings = getattr(prevreport, f'{name}rankings')
        pR = prevrankings.get(Performer)
        if pR:
          Move = pR.nr - Nr
          PΔ = R.slotobj.totalpoints - pR.slotobj.totalpoints
      for item in R.slotobj.performances.items():
        perfobj, (slotgroup, slotnr) = item
        if slotgroup is sr.slot.SlotGroup("NE"):
          continue
        T += 1
        G += perfobj.totalnummatches
      if Nr <= upper_maxNr and upper_minP <= P:
        upperPerformers.append((Performer, Nr))
        upperNr = len(upperPerformers)
        for _, Nr_ in reversed(upperPerformers[:-1]):
          if Nr_ == Nr:
            upperNr -= 1
          else:
            break
      elif lower_minP <= P:
        if name == "coach":
          if lower_minT <= T:
            lowerNr = math.inf  # flag
        elif name == "team":
          if rosterialNr <= lower_maxrosterialNr:
            lowerNr = math.inf
        if lowerNr == math.inf:
          lowerPerformers.append((Performer, Nr))
          lowerNr = len(lowerPerformers)
          for _, Nr_ in reversed(lowerPerformers[:-1]):
            if Nr_ == Nr:
              lowerNr -= 1
            else:
              break
      yield self.FullRankingsRow(
        rownum,
        Nr, Move, Performer, P, PΔ, Pw, T, G,
        upperNr, lowerNr,
      )

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
  def coachrankings_lower_minT(self):
    nmainT = len({T for T in self.tournaments if T.ismain})
    minTmax = sr.settings["coach.lower.minTmax"]
    minTratio = sr.settings["coach.lower.minTratio"]
    return max(min(minTmax, nmainT // minTratio), 1)

  @property
  def coachslots(self):
    return sorted({
        sr.slot.CoachSlots(C.id, self.weekNr)
        for C in self.coaches
        if C
    }, key=lambda CS: CS.sort_key)

  @property
  def coachrankings(self):
    return self._rankings("coach")

  @property
  def coachfullrankings(self):
    return self.get_fullrankings("coach")

  @property
  def date(self):
    return sr.time.firstdate(self.weekNr)

  @property
  def enddate(self):
    p, n = self.prevnext
    if n:
      return n.date - sr.time.ONEDAY

  @property
  def enters(self):
    return sr.tournament.enters(self.weekNr)

  @property
  def exits(self):
    return sr.tournament.exits(self.weekNr)

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
        if Te
    }, key=lambda TS: TS.sort_key)

  @property
  def teamrankings(self):
    return self._rankings("team")

  @property
  def teamfullrankings(self):
    return self.get_fullrankings("team")

  @property
  def weekNr(self):
    return reportNrs()[self.nr]

  def get_fullrankings(self, name, *,
        rebuild=False,
        autosave=True,
    ):
    attr = f'_{name}fullrankings'
    if not rebuild and getattr(self, attr) is None:
      rankings = sr._data.load_rankings(self.nr, name)
      setattr(self, attr, rankings)
    if rebuild or getattr(self, attr) is None:
      generator = self._iter_fullrankings(name)
      setattr(self, attr, tuple(generator))
      if autosave:
        sr._data.save_rankings(self.nr, name)
    return getattr(self, attr)



def all():
  return tuple(
      Report(reportNr)
      for reportNr in list(reportNrs())[:-1]
  )


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
