import json

from . import fumbblapi
import sr


class SomeRoster:

  def __bool__(self):
    return False

  def __repr__(self):
    return "SomeRoster"

  def __str__(self):
    return "* Some Roster *"

  @property
  def name(self):
    return str(self)

SomeRoster = SomeRoster()  # singleton


class Roster(metaclass=sr.helper.InstanceRepeater):

  NO_ROSTER = '{"stars": [], "positions": []}'

  def __init__(self, rosterId: int):
    self._apidata = ...
    self._name = ...

  def __bool__(self):
    return bool(self.name)

  def __repr__(self):
    return f'Roster({self.id})'

  def __str__(self):
    return self.name or "* Some Roster *"

  @property
  def apidata(self):
    if self._apidata is ...:
      self._apidata = fumbblapi.get__roster(self.id)
      if self._apidata == json.loads(self.NO_ROSTER):
        self._apidata = None
    return self._apidata

  @property
  def id(self):
    return self._KEY[0]  # set by metaclass

  @property
  def name(self):
    if self._name is ...:
      self._name = self.name_of_week()
      if not self._name:
        self._name = self.apidata.get("name")
    return self._name
  @name.setter
  def name(self, name: str):
    self._name = str(name)

  @property
  def name_is_set(self):
    return (self._name is not ...)

  def name_of_week(self, weeknr=None):
    names = sr.data["rostername"].get(self.id)
    if names:
      if weeknr is None:
        return names[-1][-1]
      else:
        weeknr = int(weeknr)
        for start_weeknr, stop_weeknr, name in names:
          if weeknr in range(start_weeknr, stop_weeknr):
            return name
        else:
          return name
    elif self.apidata:
      return self.apidata.get("name")
