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




@sr.helper.srdata("coach", ("name",))
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
  def apiname(self):
    try:
      return fumbblapi.get__coach(self.id).get("name")
    # self.NO_COACH is not JSON serializable
    except json.JSONDecodeError:
      pass
    return ...

  @property
  def id(self):
    return self._KEY[0]  # set by metaclass

  @property
  def name_is_set(self):
    return (self._name is not ...)

  @property
  def name(self):
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
