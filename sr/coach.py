import json

from . import fumbblapi
import sr


@sr.helper.objectreprhash
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






@sr.helper.srdata("coach",
    (
        "name",
    ),
    {
        "name": ["srdataname", "apiname"],
    },
)
@sr.helper.idkey
class Coach(metaclass=sr.helper.InstanceRepeater):

  NO_COACH = "Error:0 No such coach found."

  def __init__(self, coachId: int):
    pass  # without this instantiation raises TypeError

  def __bool__(self):
    return bool(self.name)

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


def iter_referenced():
  yield from Coach.__members__.values()


def save():
  for T in iter_referenced():
    T.srnewdata_apply()
  sr._data.save("coach")
