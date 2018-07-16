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
    nextslotgroup = 4
    pointsincluded = 5

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


class TeamSlots(metaclass=sr.helper.InstanceRepeater):

  def __init__(self, teamId, weekNr):
    pass  # without this instantiation raises TypeError

  @property
  def team(self):
    return sr.team.Team(self.teamId)

  @property
  def teamId(self):
    return self._KEY[0]

  @property
  def weekNr(self):
    return self._KEY[1]

  @property
  def slotgrouprules(self):
    print(list(sr.data["slot"]))
    return {
        SlotGroup(sgname): SlotGroup(sgname).rules(self.weekNr)
        for sgname in sr.data["slot"]
    }
