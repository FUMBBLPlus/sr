import functools
import itertools

import sr





def _main_tournament_only(method):
  @functools.wraps(method)
  def wrapper(self, *args, **kwargs):
    if not self.tournament.ismain:
      raise AttributeError('only for main tournaments')
    else:
      return method(self, *args, **kwargs)
  return wrapper





class BasePerformance(metaclass=sr.helper.InstanceRepeater):

  DIRTY_RESULTS = {
      sr.tournament.Matchup.Result.conceded,
      sr.tournament.Matchup.Result.fortfeit,
      sr.tournament.Matchup.Result.quit,
  }

  MATCH_RESULTS = {
      sr.tournament.Matchup.Result.win,
      sr.tournament.Matchup.Result.draw,
      sr.tournament.Matchup.Result.loss,
      sr.tournament.Matchup.Result.conceded,
  }

  def __init__(self):
    self._clean = ...
    self._points = ...
    self._totalpoints = ...

  def __repr__(self):
    return (
            f'{self.__class__.__name__}'
            f'({self._KEY[0]}, {self._KEY[1]})'
        )

 #def __lt__(self, other):
 #  return (self.sort_key < other.sort_key)
 #def __le__(self, other):
 #  return (self.sort_key <= other.sort_key)
 #def __eq__(self, other):
 #  return (self.sort_key == other.sort_key)
 #def __ne__(self, other):
 #  return (self.sort_key != other.sort_key)
 #def __gt__(self, other):
 #  return (self.sort_key > other.sort_key)
 #def __ge__(self, other):
 #  return (self.sort_key >= other.sort_key)


  @property
  def alltournaments(self):
    tournaments = set(self.withqualifiers)
    tournaments |= {
        TP.tournament for TP in self.levelperformances
    }
    return tournaments


  @property
  def tournament(self):
    return sr.tournament.Tournament(self.tournamentId)

  @property
  def tournamentId(self):
    return self._KEY[0]

  @property
  def clean(self):
    if self._clean is ...:
      performances = self.thisallteamperformances
      teams = {TP.team for TP in performances}
      if len(teams) != 1:
        self._clean = False
    if self._clean is ...:
      levels = {TP.tournament.level for TP in performances}
      if len(levels) < len(performances):
        self._clean = False
    if self._clean is ...:
      unclean = bool(self.distinctresults & self.DIRTY_RESULTS)
      self._clean = (not unclean)
    return self._clean

  @property
  @_main_tournament_only
  def sort_key(self):
    enterweekNr = self.tournament.srenterweekNr
    if not self.clean:
      # dirty results first with smallest points first
      return self.clean, self.points, -enterweekNr
    else:
      # clean results second with highest points first
      return self.clean, -self.points, -enterweekNr

  @property
  def withqualifiers(self):
    return list(itertools.chain(
        [self.tournament],
        self.tournament.qualifiers,
    ))




class CoachPerformance(BasePerformance):

  def __init__(self,
      tournamentId: int,
      coachId: int,
  ):
    super().__init__()

  @property
  @_main_tournament_only
  def allmatches(self):
    return sum(
        TP.allnummatches
        for TP in self.allteamperformances
    )

  @property
  def coach(self):
    return sr.coach.Coach(self.coachId)

  @property
  def coachId(self):
    return self._KEY[1]

  @property
  @_main_tournament_only
  def cumulatedrawpoints(self):
    return sum(
        TP.cumulatedrawpoints
        for TP in self.allteamperformances
    )

  @property
  def distinctresults(self):
    Schedule = sr.tournament.Schedule
    return {
        result
        for T in self.alltournaments
        for Te in self.allteams
        for result in Schedule(T.id).results.get(Te, [])
    }

  @property
  def allteamperformances(self):
    return {
        TP for TP in self.tournament.allteamperformances
        if TP.team.coach is self.coach
    }

  @property
  @_main_tournament_only
  def allteams(self):
    return {
        Te for Te in self.tournament.allteams
        if Te.coach is self.coach
    }

  @property
  def levelperformances(self):
    if self.tournament.ismain:
      return {self}
    level = self.tournament.level
    tournaments = {
        T for T in self.tournament.main.qualifiers
        if T.level == level
        and self.coach in T.coaches
    }
    return {
        CoachPerformance(T.id, self.coachId)
        for T in tournaments
    }

  @property
  def nummatches(self):
    return sum(TP.nummatches for TP in self.teamperformances)

  @property
  def points(self):
    if self._points is ...:
      lp = sorted(
          (TP.rawpoints, TP.tournamentId, TP, CP)
          for CP in self.levelperformances
          for TP in CP.teamperformances
      )
      done = False
      for pts, _, TP, CP in lp:
        # Multiple applications of same teams are handled in the
        # TeamPerformance points: one point is kept the rest are
        # zeroed.
        if TP.points == TP.rawpoints:
          # I want to keep the lowest of those kept team points
          # for the coach and done.
          if not done:
            CP._points = pts
            done = True
        # The rest of the points should be zeroed.
        if CP._points is ...:
          CP._points = 0
    # If no team made to this level then at this point
    # self._points is yet unchanged but it should be zero.
    if self._points is ...:
      self._points = 0
    return self._points

  @property
  def teamperformances(self):
    return {
        TP for TP in self.tournament.teamperformances
        if TP.team.coach is self.coach
    }

  @property
  def teams(self):
    return {
        Te for Te in self.tournament.teams
        if Te.coach is self.coach
    }

  @property
  def thisallteamperformances(self):
    return {
        TP
        for T in self.alltournaments
        for TP in T.allteamperformances
        if TP.team.coach is self.coach
    }

  @property
  def thisalltournaments(self):
    return {
        T for T in self.alltournaments
        if self.coach in T.coaches
    }


  @property
  @_main_tournament_only
  def totalnummatches(self):
    return sum(
        CoachPerformance(T.id, self.teamId).nummatches
        for T in self.withqualifiers
        if self.coach in T.coaches
    )

  @property
  @_main_tournament_only
  def totalpoints(self):
    if self._totalpoints is ...:
      self._totalpoints = sum(
          CoachPerformance(T.id, self.coachId).points
          for T in self.withqualifiers
          if self.coach in T.coaches
      )
    return self._totalpoints





class TeamPerformance(BasePerformance):

  def __init__(self,
      tournamentId: int,
      teamId: int,
  ):
    self._rawpoints = ...
    super().__init__()

  @property
  def coachperformance(self):
    return CoachPerformance(
        self.tournamentId, self.team.coach.id
    )

  @property
  def distinctresults(self):
    Schedule = sr.tournament.Schedule
    return {
        result
        for T in self.alltournaments
        for result in Schedule(T.id).results.get(self.team, [])
    }

  @property
  def levelperformances(self):
    if self.tournament.ismain:
      return {self}
    level = self.tournament.level
    tournaments = {
        T for T in self.tournament.main.qualifiers
        if T.level == level
        and self.team in T.teams
    }
    return {
        TeamPerformance(T.id, self.teamId)
        for T in tournaments
    }

  @property
  @_main_tournament_only
  def multiapplic(self):
    return {
        TP
        for TP in self.tournament.allteamperformances
        if TP.team is not self.team
        and TP.team.coach is self.team.coach
    }

  @property
  def nummatches(self):
    return len([
        r for r in self.results
        if r in self.MATCH_RESULTS
    ])

  @property
  def points(self):
    if self._points is ...:
      lp = sorted(
          (TP.rawpoints, TP.tournamentId, TP)
          for TP in self.levelperformances
      )
      for i, (pts, _, TP) in enumerate(lp):
        if i == 0:
          TP._points = pts
        else:
          TP._points = 0
    return self._points

  @property
  def progression(self):
    return self.tournament.schedule.results.get(self.team)

  @property
  @_main_tournament_only
  def qualifierteamperformances(self):
    return {TeamPerformance(T.id, self.teamId)
        for T in self.tournament.qualifiers
        if self.team in T.teams
    }

  @property
  def rawpoints(self):
    if self._rawpoints is ...:
      progression = self.progression
      if progression is None:
        self._rawpoints = 0
        return 0
      parts0 = self.tournament.srpointsstr.split('|')
      parts1 = [s.strip() for s in reversed(parts0)]
      initialpts = int(parts1[0])
      if len(parts1) == 3:
        winnerpts = int(parts1[2])
      else:
        winnerpts = None
      if self.tournament.iselim:
        parts2 = [
            int(s.strip())
            for s in reversed(parts1[1].split('–'))
        ]
        if winnerpts is None:
          winnerpts = (parts2[-1] - parts2[-2]) // 4
          parts2[-1] -= winnerpts
        wskip = 0
        normprog = reversed(list(enumerate(progression, 1)))
        for round_, result in normprog:
          if result in self.DIRTY_RESULTS:
            wskip += 1
          elif result == sr.tournament.Matchup.Result.win:
            if wskip:
              wskip -= 1
            else:
              break
        else:
          if wskip:
            round_ = None
            pts = 0
          else:
            round_ = 0
        if round_ is not None:
          pts = ([initialpts] + parts2)[round_]
      else:
        parts2 = [int(s.strip()) for s in parts1[1].split('/')]
        winpts, drawpts, losspts = parts2
        pts = initialpts
        for result in self.progression:
          if result in self.DIRTY_RESULTS:
            pts -= winpts + drawpts
          elif result == sr.tournament.Matchup.Result.win:
            pts += winpts
          elif result == sr.tournament.Matchup.Result.draw:
            pts += drawpts
          elif result == sr.tournament.Matchup.Result.loss:
            pts += losspts
      if self.team is self.tournament.winner and winnerpts:
        pts += winnerpts
      self._rawpoints = max(0, pts)
    return self._rawpoints

  @property
  def results(self):
    return self.tournament.schedule.results.get(self.team, [])

  @property
  def strresults(self):
    schedule = self.tournament.schedule
    strresults = schedule.strresults
    if self.team in strresults:
      return strresults[self.team]
    else:
      nonestr = sr.tournament.Matchup.Result.none.value
      return nonestr * schedule.srrounds

  @property
  def team(self):
    return sr.team.Team(self.teamId)

  @property
  def teamId(self):
    return self._KEY[1]

  @property
  def thisallteamperformances(self):
    return {
        TeamPerformance(T.id, self.team.id)
        for T in self.alltournaments
        if self.team in T.teams
    }

  @property
  def thisalltournaments(self):
    return {
        T for T in self.alltournaments
        if self.team in T.teams
    }

  @property
  @_main_tournament_only
  def totalnummatches(self):
    return sum(
        TeamPerformance(T.id, self.teamId).nummatches
        for T in self.withqualifiers
        if self.team in T.teams
    )

  @property
  @_main_tournament_only
  def totalpoints(self):
    if self._totalpoints is ...:
      self._totalpoints = sum(
          TeamPerformance(T.id, self.teamId).points
          for T in self.withqualifiers
          if self.team in T.teams
      )
    return self._totalpoints

