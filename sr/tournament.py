import enum
import functools
import json
import math

from . import fumbblapi
import sr


class Matchup(metaclass=sr.helper.InstanceRepeater):

  class Result(enum.Enum):
    win = "W"
    draw = "D"
    loss = "L"
    bye = "B"
    fillerbye = "b"
    conceded = "C"
    fortfeit = "F"
    quit = "Q"
    pending = "?"
    none = "."

  def __init__(self,
      tournamentId: int,
      round_: int,
      teamIds: frozenset
  ):
    pass  # without this instantiation raises TypeError

  @property
  def created(self):
    created = self.schedule.apidata[self]["created"]
    if created:
      return sr.time.strptime(created)

  @property
  def drawscores(self):
    if self.match:
      result = self.schedule.apidata[self]["result"]
      scores = {result["teams"][i]["score"] for i in range(2)}
      return (len(scores) == 1)

  @property
  def isforfeited(self):
    return (not self.ispending and not self.match)

  @property
  def ispending(self):
    return ("result" not in self.schedule.apidata[self])

  @property
  def match(self):
    if not self.ispending:
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
  def results(self):
    d = {
        Te: self.Result.pending
        for Te in self.teams if not Te.isfiller
    }
    if not self.ispending:
      if self.isforfeited:
        for Te in d:
          if len(d) == 1:
            d[Te] = self.Result.fillerbye
          elif Te is self.winner:
            d[Te] = self.Result.bye
          else:
            d[Te] = self.Result.fortfeit
      else:
        for Te in d:
          if self.drawscores and not self.tournament.iselim:
            d[Te] = self.Result.draw
          elif Te is self.winner:
            d[Te] = self.Result.win
          elif Te is self.match.conceded:
            d[Te] = self.Result.conceded
          else:
            d[Te] = self.Result.loss
    return d

  @property
  def round(self):
    # round value set by metaclass as self._KEY[1]
    return self._KEY[1]

  @property
  def schedule(self):
    # tournamentId set by metaclass as self._KEY[0]
    return Schedule(self._KEY[0])

  @property
  def srfinished(self):
    if not self.ispending:
      if self.modified:
        return self.modified
      if self.match:
        return self.match.finished

  @property
  def teams(self):
    # teamtIds set by metaclass as self._KEY[2]
    return {sr.team.Team(teamId) for teamId in self._KEY[2]}

  @property
  def tournament(self):
    # tournamentId set by metaclass as self._KEY[0]
    return Tournament(self._KEY[0])

  @property
  def winner(self):
    if not self.ispending:
      teamId = self.schedule.apidata[self]["result"]["winner"]
      if teamId:
        return sr.team.Team(int(teamId))







@sr.helper.idkey("tournamentId")
class Schedule(metaclass=sr.helper.InstanceRepeater):

  NO_SCHEDULE = "[]"

  def __init__(self, tournamentId: int):
    self._apidata = ...

  @property
  def apidata(self):
    if self._apidata is ...:
      li = fumbblapi.get__tournament_schedule(self.tournamentId)
      self._apidata = {}
      for d0 in li:
        teams = set()
        for d1 in d0["teams"]:
          team = sr.team.Team(d1["id"])
          if not team.nameisset:
            # I have the team name known here so I set it and I
            # may spare the FUMBBL API request for it later
            team.name = d1.get("name", ...)
          teams.add(team.id)
        matchup = Matchup(
            self.tournament.id, d0["round"], frozenset(teams)
        )
        self._apidata[matchup] = d0
    return self._apidata

  @property
  def matchups(self):
    return set(self.apidata)

  @property
  def results(self):
    d = sr._data.load_results(self.tournamentId)
    if d is not None:
      return d
    d = {
        Te: [Matchup.Result.none] * self.rounds
        for Te in self.teams
        if not Te.isfiller
    }
    quitters = set()
    for r in range(1, self.rounds + 1):
      for m in {m for m in self.matchups if m.round == r}:
        for Te, result_ in m.results.items():
          d[Te][r-1] = result_
      # Now I have to look for quitters
      if 1 < r:
        for Te, results_ in d.items():
          if Te in quitters:
            continue
          prev, this = results_[r-2:r]
          if this != Matchup.Result.none:
            continue
          # Replacement teams should not get treated as quitters
          # before their first participation.
          for r2, result2 in enumerate(results_, 1):
            if result2 != Matchup.Result.none:
              break
          if r <= r2:
            continue
          # For non-elimination tournament, no participation in
          # a round is considered a quit.
          # For elimination tournaments the previous round
          # should be checked.
          if (
              not self.tournament.iselim
              or prev in {
                  Matchup.Result.win,
                  Matchup.Result.bye,
                  Matchup.Result.fillerbye,
              }
          ):
            d[Te][r-1] = Matchup.Result.quit
            quitters.add(Te)
    return d

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
  def srnteams(self):
    return len({team for team in self.round_teams(1) if team})

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
        f = round_isforfeited(schedule, r)
        if f:
          r -= 1
    return r

  @property
  def teams(self):
    return self.round_teams(None)

  @property
  def tournament(self):
    return Tournament(self.tournamentId)

  def round_isforfeited(self, round_):
    if all(
        matchup.isforfeited
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

  def save_results(self):
    if self.tournament.status == "completed":
      sr._data.save_results(self.tournament.id)
      return True
    else:
      return False





@sr.helper.default_srdata_typecast
@sr.helper.srdata("tournament",
    (
        "groupId",
        "maintournamentId",
        "srname",
        "srclassval",
        "srtitle",
        # srtitle is defined for special tournaments listed in
        # the first section of the rulebook.
        "srfsgname",  # first slot group name
        "srenterweekNr",
        "srexitweekNr",
    ),
    #srclassval should controlled via self.srclass object
    valattrmapping = {
        "maintournamentId": [
            "srdatamaintournamentId",
            "groupdefaultmaintournamentId",
        ],
        "srname": ["srdatasrname", "name"],
        "srclassval": [
            "srdatasrclassval", "_srclassdotval"
        ],
        "srtitle": [
            "srdatasrtitle", "groupdefaultsrtitle",
        ],
        "srfsgname": [
            "srdatasrfsgname", "groupdefaultsrfsgname",
        ],
        "srenterweekNr": [
            "srdatasrenterweekNr", "schedulesrenterweekNr",
        ],
        "srexitweekNr": [
            "srdatasrexitweekNr", "srtitlesrexitweekNr",
        ],
    },
    valsettermapping = {"srclassval": False},
)
@sr.helper.idkey
class Tournament(metaclass=sr.helper.InstanceRepeater):

  def _main_only(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
      if not self.ismain:
        raise AttributeError('only for main tournaments')
      else:
        return method(self, *args, **kwargs)
    return wrapper

  @sr.helper.srdata(None,
      (
          "srformatchar",
          "rank",
          "level",
          "srnteams",
      ),
      valattrmapping = {
          "srformatchar": [
              "srdatasrformatchar", "apisrformatchar"
          ],
          "rank": [
              "srdatarank", "groupdefaultrank",
          ],
          "level": [
              "srdatalevel", "groupdefaultlevel",
          ],
          "srnteams": [
              "srdatasrnteams", "schedulesrnteams",
          ],
      },
  )
  @sr.helper.idkey("tournament", sr.helper.NOTYPECAST)
  class SRClass(metaclass=sr.helper.InstanceRepeater):
    SPLITTER = "/"
    NONE = "?"
    NON_ELIM = "N"
    ELIM = "E"
    FORMAT_CHARS = (NON_ELIM, ELIM)
    # FORMAT_CHARS order is important for iselim()
    MAJOR = "MA"
    MINOR = "MI"
    QUALIFIER = "QU"
    RANKS = (MAJOR, MINOR, QUALIFIER)
    MAX_LEVEL = 4

    @classmethod
    def _level_fgetvalcast(cls, value):
      return int(value)
    @classmethod
    def _level_beforefset(cls, value):
      value_ = int(value)
      if value_ not in range(1, cls.MAX_LEVEL):
        raise ValueError(f'invalid level: {value}')
      return value_
    @classmethod
    def _rank_fgetvalcast(cls, value):
      return value.upper()
    @classmethod
    def _rank_beforefset(cls, value):
      value_ = value.upper()
      if value_ not in cls.RANKS:
        raise ValueError(f'invalid rank: {value}')
      return value_
    @classmethod
    def _srformatchar_fgetvalcast(cls, value):
      return value.upper()
    @classmethod
    def _srformatchar_beforefset(cls, value):
      value_ = value.upper()
      if value_ not in cls.FORMAT_CHARS:
        raise ValueError(f'invalid srformatchar: {value}')
      return value_
    @classmethod
    def _srnteams_fgetvalcast(cls, value):
      return int(value)
    @classmethod
    def _srnteams_beforefset(cls, value):
      value_ = int(value)
      if value_ < 2:
        raise ValueError(f'invalid srnteams: {value}')
      return value_

    @classmethod
    def join(cls, parts):
      if parts[cls.SRData.Idx.srformatchar] == cls.ELIM:
        N = 4
      else:
        N = 3
      parts = parts[:N]
      strparts = [
          (cls.NONE if v is None else str(v))
          for v in parts
      ]
      return cls.SPLITTER.join(strparts)

    @classmethod
    def split(cls, val):
      result = val.split(cls.SPLITTER)
      for i, v in enumerate(result):
        idx = cls.SRData.Idx(i)
        colname = idx.name
        if v == cls.NONE:
          result[idx] = None
        else:
          if hasattr(cls, f'_{colname}_fgetvalcast'):
            v = getattr(cls, f'_{colname}_fgetvalcast')(v)
          result[idx] = v
      return result

    def _afterfset(self, colname, newvalue, oldvalue):
      self.tournament._srclassval = self.val

    def __init__(self, tournament_instance):
      pass  # without this instantiation raises TypeError

    @property
    def apisrformatchar(self):
      T = self.tournament
      et = T.group.oldapidata_tournament[T]
      # Old API results are xml.etree.ElementTree instances
      tournament_format = et.find("type").text
      d = {
          "King": self.ELIM,
          "Knockout": self.ELIM,
          "RoundRobin": self.NON_ELIM,
          "Swiss": self.NON_ELIM,
      }
      return d[tournament_format]

    @property
    def iselim(self):
      return bool(self.FORMAT_CHARS.index(self.srformatchar))
    @iselim.setter
    def iselim(self, value):
      self.srformatchar = self.FORMAT_CHARS[bool(value)]

    @property
    def groupdefaultlevel(self):
      T = self.tournament
      if T.group:
        return T.group.default_tournament_level

    @property
    def groupdefaultrank(self):
      T = self.tournament
      if T.group:
        return T.group.default_tournament_rank

    @property
    def schedulesrnteams(self):
      return self.tournament.schedule.srnteams

    @property
    def srdata(self):
      # T.srclassval would result inifinte recursion
      # (see Tournament's valattrmapping).
      val = self.tournament.srdatasrclassval
      if val not in (None, ...):
        return self.split(val)

    @property
    def val(self):
      return self.join(self.srnewdata)

  def __init__(self, tournamentId: int):
    # Tournaments should not get instantiated directly but
    # via their groups as knowing their group is required for
    # most of the methods. However, there is no way of getting
    # the group of an arbitrary tournament.
    # So use any of the added(), all(), changed(),
    # main_unknown(), new(), or the observed() functions to get
    # properly set tournament instances.

    # ... is for unset
    self._qualifiers = set()

    # self._KEY is normally set by the metaclass after instance
    # creation but I need that now to be able to link main
    # tournaments with their qualifiers.
    self._KEY = tournamentId
    if self.ismain is False:
      self.main._qualifiers.add(self)

  def __bool__(self):
    return bool(self.srname or self.name)

  def __delattr__(self, name):
    if name in self._srclassattrs():
      return delattr(self.srclass, name)
    return super().__delattr__(name)

  def __dir__(self):
    superdir = list(super().__dir__())
    return sorted(superdir + self._srclassattrs())

  def __getattr__(self, name):
    if name in self._srclassattrs():
      return getattr(self.srclass, name)
    # object does not have a __getattr__ method
    return super().__getattribute__(name)

  def __setattr__(self, name, value):
    if name in self._srclassattrs():
      return setattr(self.srclass, name, value)
    return super().__setattr__(name, value)

  def __str__(self):
    return self.srname or self.name or "* Some Tournament *"

  @property
  def _srclassdotval(self):
    return self.srclass.val

  @property
  def group(self):
    if self.groupId is not None:
      return sr.group.Group(self.groupId)

  @property
  def groupdefaultismain(self):
    if self.group:
      return self.group.default_tournament_ismain

  @property
  def groupdefaultmaintournamentId(self):
    if self.groupdefaultismain is True:
      return 0

  @property
  @_main_only
  def groupdefaultsrfsgname(self):
    if self.group:
      return self.group.default_tournament_srfsgname

  @property
  @_main_only
  def groupdefaultsrtitle(self):
    if self.group:
      return self.group.default_tournament_srtitle

  @property
  def http(self):
    if self.groupId is not None:
      return (
          "https://fumbbl.com/p/group"
          "?op=view"
          "&p=tournaments"
          f'&group={self.groupId}'
          f'&show={self.id}'
          "&at=1&showallrounds=1"
      )

  @property
  def ismain(self):
    if self.main is self:
      return True
    elif self.main:
      return False

  @property
  def main(self):
    if self.maintournamentId in {0, self.id}:
      return self
    elif self.maintournamentId:
      return Tournament(self.maintournamentId)
  @main.setter
  def main(self, maintournament):
    if maintournament is not None:
      self.maintournamentId = maintournament.id
    else:
      self.maintournamentId = None

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
  @_main_only
  def schedulesrenterweekNr(self):
    srfinished = self.schedule.srfinished
    if srfinished:
      return sr.time.weekNr(srfinished) + 1
      # Tournament enters the system the next week it
      # finishes, hence the plus one.

  @property
  def srclass(self):
    return self.SRClass(self)

  @property
  @_main_only
  def srfsg(self):
    if self.srfsgname:
      return sr.slot.SlotGroup(self.srfsgname)

  @property
  @_main_only
  def srlatestexitweekNr(self):
    if self.srexitweekNr is not None:
      return self.srexitweekNr
    else:
      srenterweekNr = self.srenterweekNr
      if srenterweekNr is not None:
        srtitle = self.srtitle
        if not srtitle:
          remains = sr.settings["tournament.normal.remains"]
        else:
          remains = sr.settings["tournament.srtitle.remains"]
        return srenterweekNr + remains

  @property
  def srnameisset(self):
    return (self._srname is not ...)

  @property
  def srnewdata(self):
    attrs = tuple(self.SRData.Idx.__members__)
    if not self.ismain:
      attrs = attrs[:self.SRData.Idx.srtitle - len(attrs)]
    return tuple(getattr(self, a) for a in attrs)

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
            tournament.srenterweekNr,
            tournament.id
        )
    ):
      if tournament.srenterweekNr < self.srenterweekNr:
        result[0] = tournament
      elif self.srenterweekNr < tournament.srenterweekNr:
        result[1] = tournament
        break
    return tuple(result)

  @property
  @_main_only
  def srtitlesrexitweekNr(self):
    srenterweekNr = self.srenterweekNr
    if srenterweekNr is not None:
      srtitle = self.srtitle
      if not srtitle:
        remains = sr.settings["tournament.normal.remains"]
        return srenterweekNr + remains
      else:
        remains = sr.settings["tournament.srtitle.remains"]
        latestsrexitweekNr = srenterweekNr + remains
        prev, next_ = self.srsametitleprevnext
        if next_:
          next_srenterweekNr = next_.srenterweekNr
          if next_srenterweekNr:
            return min(next_srenterweekNr, latestsrexitweekNr)
        elif latestsrexitweekNr <= sr.time.current_weekNr():
            return latestsrexitweekNr

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
        if not team.nameisset:
          # I have the team name known here so I set it and I
          # may spare the FUMBBL API request for it later
          team.name = w["name"]
        return team

  def _maintournamentId_fgetvalcast(self, val):
    if val is not None:
      val = int(val)
      if val in {0, self.id}:
        return 0
      else:
        return val

  _maintournamentId_beforefset = _maintournamentId_fgetvalcast

  def _srclassattrs(self):
    srclassattrs = list(self.SRClass.SRData.Idx.__members__)
    srclassattrs.append("iselim")
    return srclassattrs

  _srname_beforefset = lambda self, val: str(val).upper()



def added():
  return {
      Tournament(tournamentId)
      for tournamentId in sr.data[Tournament.SRData.name]
  }


def all():
  return added() | observed()


def changed():
  return {T for T in all() if T.srdataischanged}


@sr.helper.default_from_func("weekNr", sr.time.current_weekNr)
def enters(weekNr):
  return {
      T for T in all()
      if T.main.srenterweekNr is not None
      and weekNr == T.main.srenterweekNr
  }


@sr.helper.default_from_func("weekNr", sr.time.current_weekNr)
def exits(weekNr):
  return {
      T for T in all()
      if T.main.srlatestexitweekNr is not None
      and weekNr == T.main.srlatestexitweekNr
  }


def fumbblcups():
  return sorted({
      T for T in all() if T.ismain
      and T.srfsg is sr.slot.SlotGroup("FC")
  })


@sr.helper.default_from_func("weekNr", sr.time.current_weekNr)
def knownlasttimer(weekNr):
  return exits(weekNr + 1)


def main_unknown():
  return {T for T in all() if T.main is None}


def new():
  return observed() - added()


def observed():
  return {T for G in sr.group.observed() for T in G.tournaments}



@sr.helper.default_from_func("weekNr", sr.time.current_weekNr)
def ofweekNr(weekNr):
  return {
      T for T in all()
      if T.main.srenterweekNr is not None
      and T.main.srlatestexitweekNr is not None
      and weekNr in range(
          T.main.srenterweekNr, T.main.srlatestexitweekNr
      )
  }


def srtitles():
  return {T.srtitle for T in added() if T.ismain and T.srtitle}
