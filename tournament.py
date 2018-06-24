import enum
import functools
import json
import math

from . import fumbblapi
import sr


class Matchup(metaclass=sr.helper.InstanceRepeater):

  def __init__(self,
      tournamentId: int,
      round_: int,
      teamIds: frozenset
  ):
    pass

  @property
  def created(self):
    created = self.schedule.apidata[self]["created"]
    if created:
      return sr.time.strptime(created)

  @property
  def srfinished(self):
    if not self.is_pending:
      if self.modified:
        return self.modified
      if self.match:
        return self.match.finished

  @property
  def is_forfeited(self):
    return (not self.is_pending and not self.match)

  @property
  def is_pending(self):
    return ("result" not in self.schedule.apidata[self])

  @property
  def match(self):
    if not self.is_pending:
      matchId = self.schedule.apidata[self]["result"]["id"]
      if matchId:
        return sr.match.Match(matchId)
        # TODO: set known match properties here

  @property
  def modified(self):
    modified = self.schedule.apidata[self]["modified"]
    if modified:
      return sr.time.strptime(modified)

  @property
  def position(self):
    return self.schedule.apidata[self]["position"]

  @property
  def round(self):
    # round value set by metaclass as self._KEY[1]
    return self._KEY[1]

  @property
  def schedule(self):
    # tournamentId set by metaclass as self._KEY[0]
    return Schedule(self._KEY[0])

  @property
  def teams(self):
    # teamtIds set by metaclass as self._KEY[2]
    return {sr.team.Team(teamId) for teamId in self._KEY[2]}

  @property
  def tournament(self):
    # tournamentId set by metaclass as self._KEY[0]
    return Tournament(self._KEY[0])



class Schedule(metaclass=sr.helper.InstanceRepeater):

  NO_SCHEDULE = '[]'

  def __init__(self, tournamentId: int):
    self._apidata = ...

  def __repr__(self):
    return f'Schedule({self.tournament.id})'


  @property
  def apidata(self):
    if self._apidata == ...:
      li = fumbblapi.get__tournament_schedule(
          self.tournament.id
      )
      self._apidata = {}
      for d0 in li:
        teams = set()
        for d1 in d0["teams"]:
          team = sr.team.Team(d1["id"])
          if not team.name_is_set:
            # I have the team name known here so I set it and I
            # may spare the FUMBBL API request for it later
            team.name = d1["name"]
          teams.add(team.id)
        matchup = Matchup(
            self.tournament.id, d0["round"], frozenset(teams)
        )
        self._apidata[matchup] = d0
    return self._apidata

  @property
  def n_srteams(self):
    return len({team for team in self.round_teams(1) if team})

  @property
  def rounds(self):
    if self.tournament.is_elim:
      p = max({matchup.position for matchup in self.matchups})
      # p=1 for final; 3 for semi-final; 7 for quaterfinal; etc.
      r = int(math.log(p + 1, 2))
    else:
      rounds_ = {matchup.round for matchup in self.matchups}
      r = max(rounds_)
      # Sometimes non-elimination format tournaments' round
      # value is unset by tournament admins and they only
      # realize that when another round gets drawn after the
      # intended end of the tournament. They then forfeit all
      # matches of the last round. SR should not treat these
      # forfeits as real ones.
      # Example: Tournament(19144).
      f = True
      while r and 1 < r and f:
        f = round_is_forfeited(schedule, r)
        if f:
          r -= 1
    return r

  @property
  def srfinished(self):
    if not any(matchup.is_pending for matchup in self.matchups):
      s = {
          matchup.srfinished
          for matchup in self.matchups
          if matchup.srfinished
      }
      if s:
        return max(s)

  @property
  def teams(self):
    return self.round_teams(None)

  @property
  def tournament(self):
    # tournamentId set by metaclass as self._KEY[0]
    return Tournament(self._KEY[0])

  @property
  def matchups(self):
    return set(self.apidata)

  def round_is_forfeited(self, round_):
    if all(
        matchup.is_forfeited
        for matchup in self.matchups
        if matchup.round == round_
    ):
      return True
    else:
      return False

  def round_teams(self, round_):
    if round_ is None:
      teams_ = {
          team
          for matchup in self.matchups
          for team in matchup.teams
      }
    else:
      teams_ = {
          team
          for matchup in self.matchups
          for team in matchup.teams
          if matchup.round == round_
      }
    return teams_


#@functools.total_ordering
class Tournament(metaclass=sr.helper.InstanceRepeater):

  class DataIdx(enum.IntEnum):
    groupId = 0
    main_tournamentId = 1
    name = 2
    class_ = 3
    winner_teamId = 4
    title = 5
    fsg = 6
    enter_weeknr = 7
    exit_weeknr = 8

  def __init__(self, tournamentId: int):
    self._baseslot = ...
    self._enter_weeknr = ...
    self._exit_weeknr = ...
    self._groupId = ...
    self._is_elim = ...
    self._level = ...
    self._main_tournamentId = ...
    self._name = ...
    self._n_srteams = ...
    self._rank = ...
    self._qualifier_tournaments = set()
    self._teams = ...
    self._title = ...
    self._winner_teamId = ...
    # self._KEY is normally set by the metaclass after instance
    # creation but to link main tournaments with qualifiers,
    # I need that now.
    self._KEY = (tournamentId,)
    if self.is_main is False:
      self.main._qualifier_tournaments.add(self)

  def __lt__(self, other):
    raise NotImplemtedError()

  def __bool__(self):
    return bool(self.srname or self.name)

  def __repr__(self):
    return f'Tournament({self.id})'

  def __str__(self):
    return self.srname or self.name or "* Some Tournament *"

  @property
  def group(self):
    if self._groupId is ... and self.srdata:
      self._groupId = int(self.srdata[self.DataIdx.groupId])
    # Currently there is no FUMBBL API endpoint to get the group
    # of an arbitrary tournament.
    if self._groupId is not ...:
      return sr.group.Group(self._groupId)

  @property
  def http(self):
    return (
        'https://fumbbl.com/p/group'
        '?op=view'
        '&p=tournaments'
        f'&group={self.group.id}'
        f'&show={self.id}'
        '&at=1&showallrounds=1'
    )

  @property
  def id(self):
    return self._KEY[0]  # set by metaclass

  @property
  def is_elim(self):
    if self._is_elim is ...:
      self.srclass = self.srdata[self.DataIdx.class_]
    if self._is_elim is ...:
      t = self.group.oldapidata_tournament[self]
      tournament_format = t.find("type").text
      d = {
          "King": True,
          "Knockout": True,
          "RoundRobin": False,
          "Swiss": False,
      }
      self._is_elim = d[tournament_format]
    return self._is_elim
  @is_elim.setter
  def is_elim(self, is_elim: bool):
    self._is_elim = bool(is_elim)

  @property
  def is_main(self):
    if self.main is self:
      return True
    elif self.main:
      return False

  @property
  def level(self):
    if self._level is ...:
      self.srclass = self.srdata[self.DataIdx.class_]
    if self._level is not ...:
      return self._level
  @level.setter
  def level(self, level: int):
    exc = ValueError(f'invalid level: {level}')
    try:
      level = int(level)
    except ValueError:
      raise exc
    if level <= 0:
      raise exc
    self._level = level

  @property
  def main(self):
    if not self.srdata:
      return None
    elif self._main_tournamentId is ...:
      i = self.srdata[self.DataIdx.main_tournamentId]
      # For visual and compactness, the TOURNAMENTS.JSON file
      # has zeros as main tournament IDs for main tournaments.
      if i == 0:
        i = self.id
      self._main_tournamentId = i
    if self._main_tournamentId is not ...:
      if self._main_tournamentId == self.id:
        return self  # avoids recursion
      else:
        return Tournament(self._main_tournamentId)
  @main.setter
  def main(self, main):
    if self.is_main is not None:
      raise AttributeError("main tournament is already set")
    if hasattr(main, "id"):
      main_tournamentId = main.id
    else:
      main_tournamentId = main
    self._main_tournamentId = int(main_tournamentId)
    srdata_idx = self.DataIdx.main_tournamentId
    if self._main_tournamentId == self.id:
      self.srdata[srdata_idx] = 0
    else:
      self.srdata[srdata_idx] = self._main_tournamentId
      self.main._qualifier_tournaments.add(self)

  @property
  def name(self):
    if self.group:
      return self.group.apidata_tournament[self]["name"]

  @property
  def n_srteams(self):
    if self._n_srteams is ...:
      self.srclass = self.srdata[self.DataIdx.class_]
    if self._n_srteams is ...:
      self._n_srteams = self.schedule.n_srteams
    return self._n_srteams

  @property
  def qualifier_tournaments(self):
    return self._qualifier_tournaments

  @property
  def rank(self):
    if self._rank is ...:
      self.srclass = self.srdata[self.DataIdx.class_]
    if self._rank is not ...:
      return self._rank
  @rank.setter
  def rank(self, rank: str):
    ranks = ("MA", "MI", "QU")
    if rank not in ranks:
      raise ValueError(f'invalid rank: {rank}')
    self._rank = rank


  @property
  def schedule(self):
    return Schedule(self.id)

  @property
  def srclass(self):
    raise NotImplemtedError()
  @srclass.setter
  def srclass(self, class_):
    if class_ not in (None, ...):
      class_parts = class_.upper().split("/")
      if len(class_parts) == 3:
        elim, rank, level = class_parts
        n_srteams = ...
      elif len(class_parts) == 4:
        elim, rank, level, n_srteams = class_parts
        n_srteams = int(n_srteams)
      self.is_elim = (elim == "E")
      self.rank = rank
      self.level = level
      if self._n_srteams is ...:
        self._n_srteams = n_srteams

  @property
  def srdata(self):
    srdata_row = sr.data["tournament"].get(self.id)
    if srdata_row:
      return tuple(srdata_row)

  @property
  def srname(self):
    if self.srdata:
      return self.srdata[self.DataIdx.name]

  @property
  def status(self):
    if self.group:
      return self.group.apidata_tournament[self]["status"]

  @property
  def winner(self):
    if self.group:
      w = self.group.apidata_tournament[self].get("winner")
      if w:
        team = sr.team.Team(w["id"])
        if not team.name_is_set:
          # I have the team name known here so I set it and I
          # may spare the FUMBBL API request for it later
          team.name = w["name"]
      return team



def added():
  return {
      Tournament(tournamentId)
      for tournamentId in sr.data["tournament"]
  }


def new():
  return watched() - added()


def watched():
  return {
      tournament
      for group in sr.group.watched()
      for tournament in group.tournaments
  }
