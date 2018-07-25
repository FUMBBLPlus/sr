import collections
import enum

import sr


@sr.helper.idkey("name")
class SlotGroup(metaclass=sr.helper.InstanceRepeater):

  class Idx(enum.IntEnum):
    enterweekNr = 0
    exitweekNr = 1
    coachslots = 2
    teamslots = 3
    dirtyslotgroup = 4
    nextslotgroup = 5
    pointsincluded = 6

  Rules = collections.namedtuple("Rules",  Idx.__members__)

  @classmethod
  def _get_key(cls, name:str):
    name_ = name.upper()
    if name_ not in sr.data["slot"]:
      raise ValueError(f'invalid slot group name: {name}')
    return name_

  def __init__(self, name: str):
    pass  # without this instantiation raises TypeError

  @sr.helper.default_from_func("weekNr", sr.time.current_weekNr)
  def rules(self, weekNr=None):
    if weekNr is None:
      weekNr = sr.time.current_weekNr()
    for row in sr.data["slot"][self.name]:
      weekNrs = range(
          row[self.Idx.enterweekNr], row[self.Idx.exitweekNr]
      )
      if weekNr in weekNrs:
        # Copy row to prevent messing up sr.data["slot"].
        rules = list(row)
        dirtyslotgoupname = rules[self.Idx.dirtyslotgroup]
        if dirtyslotgoupname is None:
          dirtyslotgroup = None
        else:
          dirtyslotgroup = SlotGroup(dirtyslotgoupname)
        rules[self.Idx.dirtyslotgroup] = dirtyslotgroup
        nextslotgoupname = rules[self.Idx.nextslotgroup]
        if nextslotgoupname is None:
          nextslotgroup = None
        else:
          nextslotgroup = SlotGroup(nextslotgoupname)
        rules[self.Idx.nextslotgroup] = nextslotgroup
        return self.Rules(*rules)

  def coachslots(self, weekNr=None):
    return self.rules(weekNr).coachslots

  def nextslotgroup(self, weekNr=None):
    return self.rules(weekNr).nextslotgroup

  def pointsincluded(self, weekNr=None):
    return self.rules(weekNr).pointsincluded

  def teamslots(self, weekNr=None):
    return self.rules(weekNr).teamslots






class BaseSlots(metaclass=sr.helper.InstanceRepeater):

  _rules = {}

  def __init__(self):
    self.performances = {}
    self.group = {group: [] for group in self.rules}


  @property
  def rules(self):
    if self.weekNr not in self._rules:
      result = {}
      for sgname in sr.data["slot"]:
        group = SlotGroup(sgname)
        rules = group.rules(self.weekNr)
        if rules is not None:
          result[group] = rules
      self._rules[self.weekNr] = result
    return self._rules[self.weekNr]

  @property
  def weekNr(self):
    return self._KEY[1]

  def add(self, performance):
    # I assume that performances are added in order.
    group = performance.tournament.srfsg
    if not performance.clean:
      group = self.rules[group].dirtyslotgroup
    while True:
      n = self.N(group)
      li = self.group[group]
      if 99999 <= n or len(li) < n:
        self.performances[performance] = (group, len(li))
        li.append(performance)
        break
      else:
        group = self.rules[group].nextslotgroup

  def N(self, group):
    ruleattr = self.__class__.__name__.lower()
    return getattr(self.rules[group], ruleattr)

  @property
  def nincluded(self):
    return sum(
      self.N(group)
      for group in self.rules
      if self.rules[group].pointsincluded
    )

  @property
  def totalpoints(self):
    return sum(
        P.totalpoints
        for P, (group, i) in self.performances.items()
        if self.rules[group].pointsincluded
    )

  @property
  def pointsarray(self):
    return sorted((
        P.totalpoints
        for P, (group, i) in self.performances.items()
        if self.rules[group].pointsincluded
    ), reverse=True)

  @property
  def sort_key(self):
    tp = -self.totalpoints
    pli = [-p for p in self.pointsarray]
    nshort = self.nincluded - len(pli)
    pli += [0] * nshort
    return tp, tuple(pli)

  @property
  def wastedpoints(self):
    return sum(
        P.totalpoints
        for P in self.group[SlotGroup("W")]
    )




class CoachSlots(BaseSlots):

  def __init__(self, coachId, weekNr):
    # without this instantiation raises TypeError
    super().__init__()

  @property
  def coach(self):
    return sr.coach.Coach(self.coachId)

  @property
  def coachId(self):
    return self._KEY[0]

  @property
  def sort_key(self):
    return (
        super(self.__class__, self).sort_key,
        (self.coach.name.lower().strip(), self.coach.id)
    )




class TeamSlots(BaseSlots):

  def __init__(self, coachId, weekNr):
    # without this instantiation raises TypeError
    super().__init__()

  @property
  def sort_key(self):
    return (
        super(self.__class__, self).sort_key,
        (self.team.name.lower().strip(), self.team.id)
    )

  @property
  def team(self):
    return sr.team.Team(self.teamId)

  @property
  def teamId(self):
    return self._KEY[0]



