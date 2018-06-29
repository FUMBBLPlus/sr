import collections
import enum

import sr


class SlotGroup(metaclass=sr.helper.InstanceRepeater):

  class Idx(enum.IntEnum):
    enterweeknr = 0
    exitweeknr = 1
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
    pass

  def __repr__(self):
    return f'SlotGroup("{self.name}")'

  @property
  def name(self):
    return self._KEY  # set by metaclass/_get_key()

  def rules(self, weeknr=None):
    if weeknr is None:
      weeknr = sr.time.current_weeknr()
    for row in sr.data["slot"][self.name]:
      weeknrs = range(
          row[self.Idx.enterweeknr], row[self.Idx.exitweeknr]
      )
      if weeknr in weeknrs:
        # Copy row to prevent messing up sr.data["slot"].
        rules = list(row)
        nextslotgroup = SlotGroup(rules[self.Idx.nextslotgroup])
        rules[self.Idx.nextslotgroup] = nextslotgroup
        return self.Rules(*rules)

  def coachslots(self, weeknr=None):
    return self.rules(weeknr).coachslots

  def nextslotgroup(self, weeknr=None):
    return self.rules(weeknr).nextslotgroup

  def pointsincluded(self, weeknr=None):
    return self.rules(weeknr).pointsincluded

  def teamslots(self, weeknr=None):
    return self.rules(weeknr).teamslots
