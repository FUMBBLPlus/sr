import json

from . import fumbblapi
import sr


@sr.helper.objectreprhash
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

  def nameofweek(self, weekNr=None):
    return self.name






@sr.helper.idkey
class Roster(metaclass=sr.helper.InstanceRepeater):

  NO_ROSTER = '{"stars": [], "positions": []}'

  def __init__(self, rosterId: int):
    self._apidata = ...
    self._name = ...

  def __bool__(self):
    return bool(self.name)

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
  def apiname(self):
    return self.apidata.get("name", ...)

  @property
  def name(self):
    if self._name is ...:
      self._name = self.nameofweek()
    if self._name is ...:
      self._name = self.apiname
    if self._name is ...:
        self._name = None
    return self._name
  @name.setter
  def name(self, name: str):
    self._name = str(name)

  @property
  def nameisset(self):
    return (self._name is not ...)

  def nameofweek(self, weekNr=None):
    names = sr.data["rostername"].get(self.id)
    if names:
      if weekNr is None:
        return names[-1][-1]
      else:
        weekNr = int(weekNr)
        for start_weekNr, stop_weekNr, name in names:
          if weekNr in range(start_weekNr, stop_weekNr):
            return name
        else:
          return name
    elif self.apidata:
      return self.apidata.get("name")
