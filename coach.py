import json

from . import fumbblapi
import sr


class SomeCoach:

  def __bool__(self):
    return False

  def __repr__(self):
    return "SomeCoach"

  def __str__(self):
    return "* Some Coach *"

  @property
  def name(self):
    return str(self)

SomeCoach = SomeCoach()  # singleton


class Coach(metaclass=sr.helper.InstanceRepeater):

  NO_COACH = "Error:0 No such coach found."

  def __init__(self, coachId: int):
    self._name = ...

  def __bool__(self):
    return bool(self.name)

  def __repr__(self):
    return f'Coach({self.id})'

  def __str__(self):
    return self.name or "* Some Coach *"

  @property
  def id(self):
    return self._KEY[0]  # set by metaclass

  @property
  def name_is_set(self):
    return (self._name != ...)

  @property
  def name(self):
    if self._name == ...:
      try:
        self._name = fumbblapi.get__coach(self.id).get("name")
      except json.JSONDecodeError:
        self._name = None
    return self._name
  @name.setter
  def name(self, name: str):
    self._name = str(name)
