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

  def __repr__(self):
    return (
            f'{self.__class__.__name__}'
            f'({self._KEY[0]}, {self._KEY[1]})'
        )

  def __lt__(self, other):
    return (self.sort_key < other.sort_key)
  def __le__(self, other):
    return (self.sort_key <= other.sort_key)
  def __eq__(self, other):
    return (self.sort_key == other.sort_key)
  def __ne__(self, other):
    return (self.sort_key != other.sort_key)
  def __gt__(self, other):
    return (self.sort_key > other.sort_key)
  def __ge__(self, other):
    return (self.sort_key >= other.sort_key)

  @property
  def alltournaments(self):
    return list(itertools.chain(
        [self.tournament],
        self.tournament.qualifiers,
    ))

  @property
  def tournament(self):
    return sr.tournament.Tournament(self.tournamentId)

  @property
  def tournamentId(self):
    return self._KEY[0]

  @property
  @_main_tournament_only
  def clean(self):
    if self._clean is ...:
      nice = bool(self.distinctresults & self.DIRTY_RESULTS)
      self._clean = (not nice)
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
  @_main_tournament_only
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
  def nummatches(self):
    return sum(TP.nummatches for TP in self.teamperformances)

  @property
  @_main_tournament_only
  def points(self):
    if self._points is ...:
      self._points = sum(
          TP.points
          for TP in self.allteamperformances
      )
    return self._points

  @property
  def rawpoints(self):
    return sum(TP.rawpoints for TP in self.teamperformances)


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





class TeamPerformance(BasePerformance):

  def __init__(self,
      tournamentId: int,
      teamId: int,
  ):
    super().__init__()


  @property
  @_main_tournament_only
  def allnummatches(self):
    result = self.nummatches
    for TP in self.qualifierteamperformances:
      result += TP.nummatches
    return result

  @property
  def coachperformance(self):
    return CoachPerformance(
        self.tournamentId, self.team.coach.id
    )

  @property
  @_main_tournament_only
  def cumulatedrawpoints(self):
    return sum(
        TeamPerformance(T.id, self.teamId).rawpoints
        for T in self.alltournaments
    )

  @property
  @_main_tournament_only
  def distinctresults(self):
    Schedule = sr.tournament.Schedule
    return {
        result
        for T in self.alltournaments
        for result in Schedule(T.id).results.get(self.team, [])
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
  @_main_tournament_only
  def points(self):
    if self._points is ...:
      p = self.cumulatedrawpoints
      multiapplic = self.multiapplic
      if not multiapplic:
        self._points = p
      else:
        d_mp = {TP: TP.cumulatedrawpoints for TP in multiapplic}
        d_mp[self] = p
        min_p = min(d_mp.values())
        p = min_p // len(d_mp)
        for TP in d_mp:
          TP._points = p
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
    progression = self.progression
    if progression is None:
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
    pts = max(0, pts)
    return pts

  @property
  def results(self):
    return self.tournament.schedule.results.get(self.team, [])

  @property
  def strresults(self):
    schedule = self.tournament.schedule
    return schedule.strresults.get(self.team, "")

  @property
  def team(self):
    return sr.team.Team(self.teamId)

  @property
  def teamId(self):
    return self._KEY[1]


