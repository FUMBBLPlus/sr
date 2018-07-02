import json

from . import fumbblapi
import sr

@sr.helper.srdata("team", ("coachId", "rosterId", "name"))
class Team(metaclass=sr.helper.InstanceRepeater):

  NO_TEAM = '{"players": []}'

  def __init__(self, teamId: int):
    self._apidata = ...
    self._coachId = ...
    self._rosterId = ...
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
    if self._coachId:
      return sr.coach.Coach(self._coachId)
    elif not self.is_filler:
      return sr.coach.SomeCoach
  @coach.setter
  def coach(self, coach):
    if coach in (None, sr.coach.SomeCoach):
      self._coachId = None
    if hasattr(coach, "id"):
      self._coachId = coach.id
    else:
      self._coachId = coach

  @property
  def coachId(self):
    if self._coachId is ...:
      if self.is_filler:
        self._coachId = None
      elif self.srdata:
        self._coachId = self.srdata[self.SRData.Idx.coachId]
      elif self.apidata:
        self._coachId = self.apidata["coach"]["id"]
        # I have the coach name known here so I set it and I
        # may spare the FUMBBL API request for it later
        coach = sr.coach.Coach(self._coachId)
        if not coach.name_is_set:
          coach.name = self.apidata["coach"]["name"]
    if self._coachId is not ...:
      return self._coachId
  @coachId.setter
  def coachId(self, coachId):
    if coachId is not None:
      coachId = int(coachId)
    self._coachId = coachId

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
      self._name = "* Filler *"
    elif self._name is ...:
      if self.srdata:
        self._name = self.srdata[self.SRData.Idx.name]
      else:
        self._name = self.apidata.get("name")
    return self._name
  @name.setter
  def name(self, name: str):
    self._name = str(name)

  @property
  def roster(self):
    if self._rosterId:
      return sr.roster.Roster(self._rosterId)
    elif not self.is_filler:
      return sr.roster.SomeRoster
  @roster.setter
  def roster(self, roster):
    if roster in (None, sr.roster.SomeRoster):
      self._rosterId = None
    if hasattr(roster, "id"):
      self._rosterId = roster.id
    else:
      self._rosterId = roster

  @property
  def rosterId(self):
    if self._rosterId is ...:
      if self.is_filler:
        self._rosterId = None
      elif self.srdata:
        self._rosterId = self.srdata[self.SRData.Idx.rosterId]
      elif self.apidata:
        self._rosterId = self.apidata["roster"]["id"]
        # I have the roster name known here so I set it and I
        # may spare the FUMBBL API request for it later
        roster = sr.roster.Roster(self._rosterId)
        if not roster.name_is_set:
          roster.name = self.apidata["roster"]["name"]
    if self._rosterId is not ...:
      return self._rosterId
  @rosterId.setter
  def rosterId(self, rosterId):
    if rosterId is not None:
      rosterId = int(rosterId)
    self._rosterId = rosterId
