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

  NO_SCHEDULE = "[]"

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
      return int(math.log(p + 1, 2))
    else:
      rounds_ = {matchup.round for matchup in self.matchups}
      return max(rounds_)

  @property
  def srfinished(self):
    if self.tournament.status == "completed":
      # As every Matchup.srfinished access may imply an API
      # request for match data, I try to optimize the search by
      # starting with the last round and go to the previos if
      # no finished time found. Note that this can only happen
      # if tournament is too old to have created/modified info
      # in its schedule data and all of its last round matches
      # were forfeited.
      rounds = range(1, self.rounds + 1)
      for round_ in reversed(rounds):
        finished = {
            matchup.srfinished
            for matchup in self.matchups
            if matchup.round == round_ and matchup.srfinished
        }
        print(finished)
        if finished:
          return max(finished)

  @property
  def srrounds(self):
    r = self.rounds
    if not self.tournament.is_elim:
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

  class SRClass(sr.helper.NoInstances):
    FORMAT_CHARS = ("N", "E")
    # FORMAT_CHARS order is important for is_elim()
    RANKS = ("MA", "MI", "QU")

    class Idx(enum.IntEnum):
      format_char = 0
      rank = 1
      level = 2
      n_srteams = 3
    UPPER_INDICES = frozenset((0, 1))
    INT_INDICES = frozenset((2, 3))

    @classmethod
    def format_char(cls, srclassval):
      return cls.split(srclassval)[cls.Idx.format_char]

    @classmethod
    def getval(cls, *args):
      values = list(args)
      if values[0] in (False, True):  # is_elim_is accepted
        values[0] = cls.FORMAT_CHARS[values[0]]
      is_elim = cls.FORMAT_CHARS.index(values[0].upper())
      N = (4 if is_elim else 3)
      values = values[:N]
      for i, v in enumerate(values):
        if i in cls.UPPER_INDICES:
          values[i] = v.upper()
        elif i in cls.INT_INDICES:
          values[i] = int(v)  # raises TypeError if not integer
      return "/".join([str(v) for v in values])

    @classmethod
    def is_elim(cls, srclassval):
      v = cls.format_char(srclassval)
      return bool(cls.FORMAT_CHARS.index(v))

    @classmethod
    def level(cls, srclassval):
      return cls.split(srclassval)[cls.Idx.level]

    @classmethod
    def n_srteams(cls, srclassval):
      splitted = cls.split(srclassval)
      if cls.Idx.n_srteams < len(splitted):
        return splitted[cls.Idx.n_srteams]

    @classmethod
    def rank(cls, srclassval):
      return cls.split(srclassval)[cls.Idx.rank]

    @classmethod
    def split(cls, srclassval):
      result = srclassval.split("/")
      for i, v in enumerate(result):
        if i in cls.UPPER_INDICES:
          result[i] = v.upper()
        elif i in cls.INT_INDICES:
          result[i] = int(v)
      return result

  class SRData(sr.helper.NoInstances):
    class Idx(enum.IntEnum):
      groupId = 0
      main_tournamentId = 1
      srname = 2
      srclass = 3
      winner_teamId = 4
      srtitle = 5
      # srtitle is defined for special tournaments listed in the
      # first section of the rulebook.
      srslot = 6  # first slot group
      enter_weeknr = 7
      exit_weeknr = 8

  def __init__(self, tournamentId: int):
    # ... is for unset
    self._groupId = ...
    self._maintournamentId = ...
    self._qualifier_tournaments = set()
    self._srname = ...
    self._is_elim = ...
    self._rank = ...
    self._level = ...
    self._n_srteams = ...

    #self._baseslot = ...
    #self._enter_weeknr = ...
    #self._exit_weeknr = ...


    #len_srdata = len(self.SRData.Idx.__members__)
    #self._srdata_inputs = [None] * len_srdata
    #self._teams = ...
    #self._title = ...
    #self._winner_teamId = ...
    # self._KEY is normally set by the metaclass after instance
    # creation but I need that now to be able to link main
    # tournaments with their qualifiers.
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
  def format_char(self):
    return self._get_class(self.SRClassIdx.format_char)
  @format_char.setter
  def format_char(self, format_char: str):
    format_char = format_char.upper()
    if format_char not in self.SRCLASS_FORMAT_CHARS:
      raise ValueError(f'invalid value: {format_char}')



  @property
  def group(self):
    if self._groupId is ...:
      if self.srdata:
        self._groupId = self.srdata[self.SRData.Idx.groupId]
      else:
        pass
        # Currently there is no FUMBBL API endpoint to get the
        # group of an arbitrary tournament.
    if self._groupId is not ...:
      return sr.group.Group(self._groupId)
  @group.setter
  def group(self, group: sr.group.Group):
    if hasattr(group, "id"):
      self._groupId = group.id
    else:  # setter also accepts an ID as parameter
      self._groupId = int(group)

  @property
  def http(self):
    return (
        "https://fumbbl.com/p/group"
        "?op=view"
        "&p=tournaments"
        f'&group={self.group.id}'
        f'&show={self.id}'
        "&at=1&showallrounds=1"
    )

  @property
  def id(self):
    return self._KEY[0]  # set by metaclass

  @property
  def is_elim(self):
    if self._is_elim is ...:
      if self.srdata:
        srclassval = self.srdata[self.SRData.Idx.srclass]
        self._is_elim = self.SRClass.is_elim(srclassval)
      else:
        t = self.group.oldapidata_tournament[self]
        tournament_format = t.find("type").text
        d = {
            "King": True,
            "Knockout": True,
            "RoundRobin": False,
            "Swiss": False,
        }
        self._is_elim = d[tournament_format]
    if self._is_elim is not ...:
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
      if self.srdata:
        srclassval = self.srdata[self.SRData.Idx.srclass]
        self._level = self.SRClass.level(srclassval)
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
    if self._maintournamentId is ...:
      if self.srdata:
        srdataidx = self.SRData.Idx.main_tournamentId
        self._maintournamentId = self.srdata[srdataidx]
    if self._maintournamentId in {0, self.id}:
      # For visual and compactness, the TOURNAMENTS.JSON file
      # has zeros as main tournament IDs for main tournaments.
      return self
      # Returning self avoids infinite recursion as there is a
      # self.main access in __init__().
    elif self._maintournamentId is not ...:
      return Tournament(self._maintournamentId)
  @main.setter
  def main(self, main: "Tournament"):
    previous_main = self.main
    if hasattr(main, "id"):
      self._maintournamentId = main.id
    else:  # setter also accepts an ID as parameter
      self._maintournamentId = int(main)
    if self._maintournamentId == self.id:
      self._maintournamentId = 0  # explained in the getter
    elif previous_main and previous_main is not self:
        previous_main._qualifier_tournaments.remove(self)
    if self.is_main is False:
      self.main._qualifier_tournaments.add(self)

  @property
  def name(self):
    if self.group:
      return self.group.apidata_tournament[self]["name"]

  @property
  def n_srteams(self):
    if self._n_srteams is ...:
      if self.srdata:
        srclassval = self.srdata[self.SRData.Idx.srclass]
        self._n_srteams = self.SRClass.n_srteams(srclassval)
    if self._n_srteams is not ...:
      return self._n_srteams
  @n_srteams.setter
  def n_srteams(self, n_srteams: int):
    exc = ValueError(f'invalid n_srteams: {n_srteams}')
    try:
      n_srteams = int(n_srteams)
    except ValueError:
      raise exc
    if n_srteams <= 0:
      raise exc
    self._n_srteams = n_srteams

  @property
  def qualifier_tournaments(self):
    return self._qualifier_tournaments

  @property
  def rank(self):
    if self._rank is ...:
      if self.srdata:
        srclassval = self.srdata[self.SRData.Idx.srclass]
        self._rank = self.SRClass.rank(srclassval)
    if self._rank is not ...:
      return self._rank
  @rank.setter
  def rank(self, rank: str):
    rank = rank.upper()
    if rank not in self.SRClass.RANKS:
      raise ValueError(f'invalid rank: {rank}')
    self._rank = rank

  @property
  def schedule(self):
    return Schedule(self.id)

  @property
  def srclass(self):
    return self.SRClass.getval(
        self.is_elim, self.rank, self.level, self.n_srteams
    )
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
    if self._srname is ...:
      if self.srdata:
        self._srname = self.srdata[self.SRData.Idx.srname]
    if self._srname is not ...:
      return self._srname
  @srname.setter
  def srname(self, name: str):
    self._srname = str(name)

  @property
  def status(self):
    if self.group:
      s = self.group.apidata_tournament[self]["status"]
      return s.lower()

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
