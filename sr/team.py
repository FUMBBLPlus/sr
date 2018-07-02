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
    if self.isfiller:
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
  def apicoachId(self):
    return self.apidata.get("coach", {}).get("id", ...)

  @property
  def apiname(self):
    return self.apidata.get("name", ...)

  @property
  def apirosterId(self):
    return self.apidata.get("roster", {}).get("id", ...)


  @property
  def coach(self):
    if self._coachId:
      return sr.coach.Coach(self._coachId)
    elif not self.isfiller:
      return sr.coach.SomeCoach
  @coach.setter
  def coach(self, coach):
    if coach in (None, sr.coach.SomeCoach):
      self._coachId = None
    if hasattr(coach, "id"):
      self._coachId = coach.id
    else:
      self._coachId = int(coach)

  @property
  def coachId(self):
    if self._coachId is ... and self.isfiller:
      self._coachId = None
    if self._coachId is ...:
      self._coachId = self.srdatacoachId
    if self._coachId is ...:
      self._coachId = self.apicoachId
    if self._coachId is ...:
      self._coachId = None
    return self._coachId
  @coachId.setter
  def coachId(self, coachId):
    if coachId is not None:
      coachId = int(coachId)
    self._coachId = coachId

  @property
  def isfiller(self):
    return (self.id in sr.data["fillerteams"])

  @property
  def id(self):
    return self._KEY[0]  # set by metaclass

  @property
  def name_is_set(self):
    return (self.isfiller or self._name is not ...)

  @property
  def name(self):
    if self._name is ... and self.isfiller:
      self._name = "* Filler *"
    if self._name is ...:
      self._name = self.srdataname
    if self._name is ...:
      self._name = self.apiname
    if self._name is ...:
      self._name = None
    return self._name
  @name.setter
  def name(self, name: str):
    if name is not None:
      self._name = str(name)
    else:
      self._name = name

  @property
  def roster(self):
    if self._rosterId:
      return sr.roster.Roster(self._rosterId)
    elif not self.isfiller:
      return sr.roster.SomeRoster
  @roster.setter
  def roster(self, roster):
    if roster in (None, sr.roster.SomeRoster):
      self._rosterId = None
    if hasattr(roster, "id"):
      self._rosterId = roster.id
    else:
      self._rosterId = int(roster)

  @property
  def rosterId(self):
    if self._rosterId is ... and self.isfiller:
      self._rosterId = None
    if self._rosterId is ...:
      self._rosterId = self.srdatarosterId
    if self._rosterId is ...:
      self._rosterId = self.apirosterId
    if self._rosterId is ...:
      self._rosterId = None
    return self._rosterId
  @rosterId.setter
  def rosterId(self, rosterId):
    if rosterId is not None:
      rosterId = int(rosterId)
    self._rosterId = rosterId

