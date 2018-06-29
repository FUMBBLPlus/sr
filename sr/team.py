import json

from . import fumbblapi
import sr


class Team(metaclass=sr.helper.InstanceRepeater):

  NO_TEAM = '{"players": []}'

  def __init__(self, teamId: int):
    self._apidata = ...
    self._name = ...

  def __bool__(self):
    if self.is_filler:
      return False
    else:
      return bool(self.name)

  def __repr__(self):
    return f'Team({self.id})'

  def __str__(self):
    return self.name or "* Some Team *"

  @property
  def apidata(self):
    if self._apidata is ...:
      self._apidata = fumbblapi.get__team(self.id)
      if self._apidata == json.loads(self.NO_TEAM):
        self._apidata = None
    return self._apidata

  @property
  def coach(self):
    if self.is_filler:
      return None
    elif self.apidata:
      coach = sr.coach.Coach(self.apidata["coach"]["id"])
      if not coach.name_is_set:
        # I have the coach name known here so I set it and I may
        # spare the FUMBBL API request for it later
        coach.name = self.apidata["coach"]["name"]
    else:
      coach = sr.coach.SomeCoach
    return coach

  @property
  def is_filler(self):
    return (self.id in sr.data["fillerteams"])

  @property
  def id(self):
    return self._KEY[0]  # set by metaclass

  @property
  def name_is_set(self):
    return (self.is_filler or self._name is not ...)

  @property
  def name(self):
    if self.is_filler:
      return "filler"
    elif self._name is ...:
      self._name = self.apidata.get("name")
    return self._name
  @name.setter
  def name(self, name: str):
    self._name = str(name)

  @property
  def roster(self):
    if self.is_filler:
      return None
    elif self.apidata:
      roster = sr.roster.Roster(self.apidata["roster"]["id"])
      if not roster.name_is_set:
        # I have the roster name known here so I set it and I
        # may spare the FUMBBL API request for it later
        roster.name = self.apidata["roster"]["name"]
    else:
      roster = sr.roster.SomeRoster
    return roster

