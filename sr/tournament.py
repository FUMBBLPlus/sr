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
    if self._apidata in (None, ...):
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
  def srnteams(self):
    return len({team for team in self.round_teams(1) if team})

  @property
  def rounds(self):
    if self.tournament.iselim:
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
        if finished:
          return max(finished)

  @property
  def srrounds(self):
    r = self.rounds
    if not self.tournament.iselim:
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

  def _main_only(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
      if not self.ismain:
        raise AttributeError('only for main tournaments')
      else:
        return method(self, *args, **kwargs)
    return wrapper

  class SRClass(sr.helper.NoInstances):
    NONE = "?"
    NON_ELIM = "N"
    ELIM = "E"
    FORMAT_CHARS = (NON_ELIM, ELIM)
    # FORMAT_CHARS order is important for iselim()
    MAJOR = "MA"
    MINOR = "MI"
    QUALIFIER = "QU"
    RANKS = (MAJOR, MINOR, QUALIFIER)

    class Idx(enum.IntEnum):
      srformatchar = 0
      rank = 1
      level = 2
      srnteams = 3
    UPPER_INDICES = frozenset((0, 1))
    INT_INDICES = frozenset((2, 3))

    @classmethod
    def srformatchar(cls, srclassval):
      return cls.split(srclassval)[cls.Idx.srformatchar]

    @classmethod
    def getval(cls, *args):
      values = list(args)
      if values[0] in (False, True):  # iselim_is accepted
        values[0] = cls.FORMAT_CHARS[values[0]]
      iselim = cls.FORMAT_CHARS.index(values[0].upper())
      N = (4 if iselim else 3)
      values = values[:N]
      for i, v in enumerate(values):
        if v in (None, ...):
          continue
        if i in cls.UPPER_INDICES:
          values[i] = v.upper()
        elif i in cls.INT_INDICES:
          values[i] = int(v)  # raises TypeError if not integer
      return "/".join([
          (str(v) if v not in (None, ...) else cls.NONE)
          for v in values
      ])

    @classmethod
    def iselim(cls, srclassval):
      v = cls.srformatchar(srclassval)
      return bool(cls.FORMAT_CHARS.index(v))

    @classmethod
    def level(cls, srclassval):
      return cls.split(srclassval)[cls.Idx.level]

    @classmethod
    def srnteams(cls, srclassval):
      splitted = cls.split(srclassval)
      if cls.Idx.srnteams < len(splitted):
        return splitted[cls.Idx.srnteams]

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
      maintournamentId = 1
      srname = 2
      srclass = 3
      srtitle = 4
      # srtitle is defined for special tournaments listed in the
      # first section of the rulebook.
      srfsgname = 5  # first slot group name
      srenterweeknr = 6
      srexitweeknr = 7

  def __init__(self, tournamentId: int):
    # Tournaments should not get instantiated directly but
    # via their groups as knowing their group is required for
    # most of the methods. However, there is no way of getting
    # the group of an arbitrary tournament.
    # So use any of the added(), all(), changed(),
    # main_unknown(), new(), or the watched() functions to get
    # properly set tournament instances.

    # ... is for unset
    self._groupId = ...
    self._maintournamentId = ...
    self._qualifiers = set()
    self._srname = ...
    self._iselim = ...
    self._srrank = ...
    self._level = ...
    self._srnteams = ...
    self._srtitle = ...
    self._srfsg = ...
    self._srenterweeknr = ...
    self._srexitweeknr = ...
    # self._KEY is normally set by the metaclass after instance
    # creation but I need that now to be able to link main
    # tournaments with their qualifiers.
    self._KEY = (tournamentId,)
    if self.ismain is False:
      self.main._qualifiers.add(self)

  def __bool__(self):
    return bool(self.srname or self.name)

  def __repr__(self):
    return f'Tournament({self.id})'

  def __str__(self):
    return self.srname or self.name or "* Some Tournament *"

  @property
  def group(self):
    if self._groupId in (None, ...) and self.srdata:
      self._groupId = self.srdata[self.SRData.Idx.groupId]
    # Note that currently there is no FUMBBL API endpoint to get
    # the group of an arbitrary tournament.
    if self._groupId is not ...:
      return sr.group.Group(self._groupId)
  @group.setter
  def group(self, group: sr.group.Group):
    if hasattr(group, "id"):
      self._groupId = group.id
    else:  # setter also accepts an ID as parameter
      self._groupId = int(group)

  @property
  def groupId(self):
    if self.group:
      return self.group.id
  @groupId.setter
  def groupId(self, groupId):
    self.group = groupId

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
  def iselim(self):
    if self._iselim in (None, ...) and self.srdata:
      srclassval = self.srdata[self.SRData.Idx.srclass]
      self._iselim = self.SRClass.iselim(srclassval)
    if self._iselim in (None, ...):
      t = self.group.oldapidata_tournament[self]
      tournament_format = t.find("type").text
      d = {
          "King": True,
          "Knockout": True,
          "RoundRobin": False,
          "Swiss": False,
      }
      self._iselim = d[tournament_format]
    if self._iselim not in (..., self.SRClass.NONE):
      return self._iselim
  @iselim.setter
  def iselim(self, iselim: bool):
    if iselim not in (None, ...):
      self._iselim = bool(iselim)
    else:
      self._iselim = iselim

  @property
  def ismain(self):
    if self.main is self:
      return True
    elif self.main:
      return False

  @property
  def level(self):
    if self._level in (None, ...) and self.srdata:
      srclassval = self.srdata[self.SRData.Idx.srclass]
      self._level = self.SRClass.level(srclassval)
    if self._level in (None, ...) and self.group:
      self._level = self.group.default_tournament_level
    if self._level not in (..., self.SRClass.NONE):
      return self._level
  @level.setter
  def level(self, level: int):
    if level not in (None, ...):
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
    if self._maintournamentId is ... and self.srdata:
      srdataidx = self.SRData.Idx.maintournamentId
      self._maintournamentId = self.srdata[srdataidx]
    elif self.group and self.group.default_tournament_ismain:
      self._maintournamentId = 0
    if self._maintournamentId in {0, self.id}:
      # For visual and compactness, the TOURNAMENTS.JSON file
      # has zeros as main tournament IDs for main tournaments.
      return self
      # Returning self avoids infinite recursion as there is a
      # self.main access in __init__().
    elif self._maintournamentId not in (..., None):
      return Tournament(self._maintournamentId)
  @main.setter
  def main(self, main: "Tournament"):
    previous_main = self.main
    if main is None:  # unknown
      self._maintournamentId = main
    elif hasattr(main, "id"):
      self._maintournamentId = main.id
    else:  # setter also accepts an ID as parameter
      self._maintournamentId = int(main)
    if self._maintournamentId == self.id:
      self._maintournamentId = 0  # explained in the getter
    elif previous_main and previous_main is not self:
        previous_main._qualifiers.remove(self)
    if self.ismain is False:
      self.main._qualifiers.add(self)

  @property
  def maintournamentId(self):
    if self.ismain:
      return 0  # explained in self.main getter
    elif self.main:
      return self.main.id
  @maintournamentId.setter
  def maintournamentId(self, maintournamentId):
    self.main = maintournamentId

  @property
  def name(self):
    if self.group:
      return self.group.apidata_tournament[self]["name"]
    else:
      return ""

  @property
  def qualifiers(self):
    return self._qualifiers

  @property
  def schedule(self):
    return Schedule(self.id)

  @property
  def srclass(self):
    return self.SRClass.getval(
        self.iselim, self.srrank, self.level, self.srnteams
    )

  @property
  def srdata(self):
    srdata_row = sr.data["tournament"].get(self.id)
    if srdata_row:
      return tuple(srdata_row)

  @property
  def srdataischanged(self):
    return (self.srdata != self.srnewdata)

  @property
  @_main_only
  def srenterweeknr(self):
    if self._srenterweeknr in (None, ...) and self.srdata:
      srdataidx = self.SRData.Idx.srenterweeknr
      self._srenterweeknr = self.srdata[srdataidx]
    if self._srenterweeknr in (None, ...):
      srfinished = self.schedule.srfinished
      if srfinished:
        self._srenterweeknr = sr.time.weeknr(srfinished) + 1
        # Tournament enters the system the next week it
        # finishes, hence the plus one.
    if self._srenterweeknr is not ...:
      return self._srenterweeknr
  @srenterweeknr.setter
  @_main_only
  def srenterweeknr(self, srenterweeknr: int):
    if srenterweeknr not in (None, ...):
      srenterweeknr = int(srenterweeknr)
    self._srenterweeknr = srenterweeknr

  @property
  @_main_only
  def srexitweeknr(self):
    if self._srexitweeknr in (None, ...) and self.srdata:
      srdataidx = self.SRData.Idx.srexitweeknr
      self._srexitweeknr = self.srdata[srdataidx]
    if self._srexitweeknr in (None, ...):
      srenterweeknr = self.srenterweeknr
      if srenterweeknr is not None:
        srtitle = self.srtitle
        if not srtitle:
          remains = sr.settings["tournament.normal.remains"]
          self._srexitweeknr = srenterweeknr + remains
        else:
          remains = sr.settings["tournament.srtitle.remains"]
          prev, next_ = self.srsametitleprevnext
          if next_:
            next_srenterweeknr = next_.srenterweeknr
            if next_srenterweeknr:
              self._srexitweeknr = min(
                  next_srenterweeknr, srenterweeknr + remains
              )
          else:
            current_weeknr = sr.time.current_weeknr()
            if srenterweeknr + remains <= current_weeknr:
              self._srexitweeknr
    if self._srexitweeknr is not ...:
      return self._srexitweeknr
  @srexitweeknr.setter
  @_main_only
  def srexitweeknr(self, srexitweeknr: int):
    if srexitweeknr not in (None, ...):
      srexitweeknr = int(srexitweeknr)
    self._srexitweeknr = srexitweeknr


  @property
  def srformatchar(self):
    if self.iselim is not None:
      return self.SRClass.FORMAT_CHARS[self.iselim]
    else:
      return self.SRClass.NONE
  @srformatchar.setter
  def srformatchar(self, srformatchar: str):
    if srformatchar in (None, self.SRClass.NONE):
      self.iselim = None
    else:
      srformatchar_ = str(srformatchar).strip().upper()
      FORMAT_CHARS = self.SRClass.FORMAT_CHARS
      try:
        self.iselim = bool(FORMAT_CHARS.index(srformatchar_))
      except IndexError:
        raise ValueError(f'invalid value: {srformatchar}')

  @property
  @_main_only
  def srfsg(self):
    if self._srfsg in (None, ...) and self.srdata:
      srdataidx = self.SRData.Idx.srfsgname
      self._srfsg = sr.slot.SlotGroup(self.srdata[srdataidx])
    if self._srfsg in (None, ...) and self.group:
      self._srfsg = sr.slot.SlotGroup(
          self.group.default_tournament_srfsg
      )
    if self._srfsg is not ...:
      return self._srfsg
  @srfsg.setter
  @_main_only
  def srfsg(self, slot):
    if slot is None or hasattr(slot, "coachslots"):
      self._srfsg = slot
    else:
      self._srfsg = sr.slot.SlotGroup(str(slot).upper())

  @property
  @_main_only
  def srfsgname(self):
    if self.srfsg:
      return self.srfsg.name
  @srfsgname.setter
  @_main_only
  def srfsgname(self, name: str):
    self.srfsg = name

  @property
  def srisnew(self):
    return (self.srdata is None)

  @property
  @_main_only
  def srlatestexitweeknr(self):
    if self.srexitweeknr is not None:
      return self.srexitweeknr
    else:
      srenterweeknr = self.srenterweeknr
      if srenterweeknr is not None:
        srtitle = self.srtitle
        if not srtitle:
          remains = sr.settings["tournament.normal.remains"]
        else:
          remains = sr.settings["tournament.srtitle.remains"]
        return srenterweeknr + remains

    if self._srexitweeknr in (None, ...) and self.srdata:
      srdataidx = self.SRData.Idx.srexitweeknr
      self._srexitweeknr = self.srdata[srdataidx]
    if self._srexitweeknr in (None, ...):
      srenterweeknr = self.srenterweeknr
      if srenterweeknr is not None:
        srtitle = self.srtitle
        if not srtitle:
          remains = sr.settings["tournament.normal.remains"]
          self._srexitweeknr = srenterweeknr + remains
        else:
          remains = sr.settings["tournament.srtitle.remains"]
          prev, next_ = self.srsametitleprevnext
          if next_:
            next_srenterweeknr = next_.srenterweeknr
            if next_srenterweeknr:
              self._srexitweeknr = min(
                  next_srenterweeknr, srenterweeknr + remains
              )
          else:
            current_weeknr = sr.time.current_weeknr()
            if srenterweeknr + remains <= current_weeknr:
              self._srexitweeknr
    if self._srexitweeknr is not ...:
      return self._srexitweeknr

  @property
  def srname(self):
    if not self.srname_is_set and self.srdata:
      srdataidx = self.SRData.Idx.srname
      self._srname = self.srdata[srdataidx]
    if self.srname_is_set:
      return self._srname
    else:
      return self.name
  @srname.setter
  def srname(self, name: str):
    self._srname = str(name).upper()

  @property
  def srname_is_set(self):
    return (self._srname is not ...)

  @property
  def srnewdata(self):
    attrs = tuple(self.SRData.Idx.__members__)
    if not self.ismain:
      attrs = attrs[:self.SRData.Idx.srtitle - len(attrs)]
    return tuple(getattr(self, a) for a in attrs)

  @property
  def srnteams(self):
    if self._srnteams in (None, ...) and self.srdata:
      srclassval = self.srdata[self.SRData.Idx.srclass]
      self._srnteams = self.SRClass.srnteams(srclassval)
    if self._srnteams in (None, ...):
      self._srnteams = self.schedule.srnteams
    if self._srnteams not in (..., self.SRClass.NONE):
      return self._srnteams
  @srnteams.setter
  def srnteams(self, srnteams: int):
    if srnteams not in (None, ...):
      exc = ValueError(f'invalid srnteams: {srnteams}')
      try:
        srnteams = int(srnteams)
      except ValueError:
        raise exc
      if srnteams <= 0:
        raise exc
    self._srnteams = srnteams

  @property
  def srrank(self):
    if self._srrank in (None, ...) and self.srdata:
      srclassval = self.srdata[self.SRData.Idx.srclass]
      self._srrank = self.SRClass.rank(srclassval)
    if self._srrank in (None, ...) and self.group:
      self._srrank = self.group.default_tournament_srrank
    if self._srrank not in (..., self.SRClass.NONE):
      return self._srrank
  @srrank.setter
  def srrank(self, srrank: str):
    if srrank not in (None, ...):
      srrank = str(srrank).upper()
      if srrank not in self.SRClass.RANKS:
        raise ValueError(f'invalid srrank: {srrank}')
    self._srrank = srrank

  @property
  @_main_only
  def srsametitleiter(self):
    srtitle = self.srtitle
    if not srtitle:
      raise AttributeError("special main tournaments only")
    for tournament in (added() | new()):
      if tournament.ismain:
        if tournament.srtitle == srtitle:
          yield tournament

  @property
  @_main_only
  def srsametitleprevnext(self):
    result = [None] * 2
    for tournament in sorted(
        {
            tournament for tournament in self.srsametitleiter
            if tournament is not self
            and tournament.status == "completed"
        },
        key=lambda tournament: (
            tournament.srenterweeknr,
            tournament.id
        )
    ):
      if tournament.srenterweeknr < self.srenterweeknr:
        result[0] = tournament
      elif self.srenterweeknr < tournament.srenterweeknr:
        result[1] = tournament
        break
    return tuple(result)

  @property
  @_main_only
  def srtitle(self):
    if self._srtitle in (None, ...) and self.srdata:
      srdataidx = self.SRData.Idx.srtitle
      self._srtitle = self.srdata[srdataidx]
    if self._srtitle in (None, ...) and self.group:
      self._srtitle = self.group.default_tournament_srtitle
    if self._srtitle is not ...:
      return self._srtitle
  @srtitle.setter
  @_main_only
  def srtitle(self, title: str):
    self._srtitle = str(title)

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
        team = sr.team.Team(int(w["id"]))
        if not team.name_is_set:
          # I have the team name known here so I set it and I
          # may spare the FUMBBL API request for it later
          team.name = w["name"]
        return team

  def srnewdata_apply(self):
    sr.data["tournament"][self.id] = list(self.srnewdata)






def added():
  return {
      Tournament(tournamentId)
      for tournamentId in sr.data["tournament"]
  }


def all():
  return added() | watched()


def changed():
  return {
      tournament for tournament in all()
      if tournament.srdataischanged
  }


def main_unknown():
  return {
      tournament for tournament in all()
      if tournament.main is None
  }


def new():
  return watched() - added()


def savesrdata():
  sr._data.save("tournament")


def srtitles():
  return {t.srtitle for t in added() if t.ismain and t.srtitle}


def watched():
  return {
      tournament
      for group in sr.group.watched()
      for tournament in group.tournaments
  }
