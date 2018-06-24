import enum
import functools
import json
import math
import typing

from . import fumbblapi
import sr


class Schedule(metaclass=sr.helper.InstanceRepeater):

  Matchup = typing.Dict
  Matchups = typing.List[Matchup]

  NO_SCHEDULE = '[]'

  def __init__(self, tournamentId):
    self._tournamentId = int(tournamentId)
    self._apidata = ...

  def __repr__(self):
    return f'Schedule({self._tournamentId})'


  @property
  def apidata(self):
    if self._apidata == ...:
      self._apidata = fumbblapi.get__tournament_schedule(
            self._tournamentId
      )
    return self._apidata

  @property
  def n_srteams(self):
    return len({team for team in self.round_teams(1) if team})

  @property
  def rounds(self):
    if self.tournament.is_elim:
      p = max({d["position"] for d in self.apidata})
      # p=1 for final; 3 for semi-final; 7 for quaterfinal; etc.
      r = int(math.log(p + 1, 2))
    else:
      rounds_ = {matchup["round"] for matchup in self.apidata}
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
        f = round_forfeited(schedule, r)
        if f:
          r -= 1
    return r

  @property
  def teams(self):
    return self.round_teams(None)

  @property
  def tournament(self):
    return Tournament(self._tournamentId)

  @property
  def matchups(self) -> Matchups:
    return sorted(
        self.apidata,
        key=lambda matchup: (
            matchup["round"],
            matchup["position"],
        )
    )

  def round_forfeited(self, round_):
    if all(
        (matchup.get("result", {}).get("id") == 0)
        for matchup in self.apidata
        if matchup["round"] == round_
    ):
      return True
    else:
      return False

  def round_teams(self, round_):
    if round_ is not None:
      teams_ = {
          sr.team.Team(team["id"])
          for matchup in self.apidata
          for team in matchup["teams"]
          if matchup["round"] == round_
      }
    else:
      teams_ = {
          sr.team.Team(team["id"])
          for matchup in self.apidata
          for team in matchup["teams"]
      }
    return teams_



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
    self._teams = ...
    self._title = ...
    self._winner_teamId = ...

  def __repr__(self):
    return f'Tournament({self.id})'

  def __str__(self):
    return self.name or "* Some Tournament *"

  @property
  def group(self):
    if self._groupId is ...:
      self._groupId = self.srdata[self.DataIdx.groupId]
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
    if self._main_tournamentId is ...:
      i = self.srdata[self.DataIdx.main_tournamentId]
      # For visual and compactness, the TOURNAMENTS.JSON file
      # has zeros as main tournament IDs for main tournaments.
      if i == 0:
        i = self.id
      self._main_tournamentId = i
    if self._main_tournamentId is not ...:
      return Tournament(self._main_tournamentId)

  @property
  def name(self):
    if self._name is ...:
      self._name = self.srdata[self.DataIdx.name]
    if self._name is not ...:
      return self._name

  @property
  def n_srteams(self):
    if self._n_srteams is ...:
      self.srclass = self.srdata[self.DataIdx.class_]
    if self._n_srteams is ...:
      self._n_srteams = self.schedule.n_srteams
    return self._n_srteams

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
    li = sr.data["tournament"].get(self.id, [...] * 10)
    return tuple(li)


def tournaments():
  return {
      Tournament(tournamentId)
      for tournamentId in sr.data["tournament"]
  }
