import json

from . import fumbblapi
import sr

@sr.helper.default_srdata_typecast
@sr.helper.srdata("team",
    (
        "coachId",
        "rosterId",
        "name",
    ),
    {
        "coachId": [
            "_fillerval", "srdatacoachId", "apicoachId"
        ],
        "rosterId": [
            "_fillerval", "srdatarosterId", "apirosterId"
        ],
        "name": ["_fillername", "srdataname", "apiname"],
    }
)
@sr.helper.idkey
class Team(metaclass=sr.helper.InstanceRepeater):

  NO_TEAM = '{"players": []}'

  def __init__(self, teamId: int):
    self._apidata = ...

  def __bool__(self):
    if self.isfiller:
      return False
    else:
      return bool(self.name)

  def __str__(self):
    return self.name or "* Some Team *"

  @property
  def _fillerval(self):
    return (..., None)[self.isfiller]

  @property
  def _fillername(self):
    return (..., "* Filler *")[self.isfiller]

  @property
  def apidata(self):
    if self._apidata is ...:
      self._apidata = fumbblapi.get__team(self.id)
      if self._apidata == json.loads(self.NO_TEAM):
        self._apidata = None
    return self._apidata

  @property
  def apicoachId(self):
    if self.apidata:
      return self.apidata.get("coach", {}).get("id", ...)

  @property
  def apiname(self):
    if self.apidata:
      return self.apidata.get("name", ...)

  @property
  def apirosterId(self):
    if self.apidata:
      return self.apidata.get("roster", {}).get("id", ...)

  @property
  def coach(self):
    if self.coachId is not None:
      return sr.coach.Coach(self.coachId)
    elif not self.isfiller:
      return sr.coach.SomeCoach

  @property
  def isfiller(self):
    return (self.id in sr.data["fillerteams"])

  @property
  def roster(self):
    if self.rosterId:
      return sr.roster.Roster(self.rosterId)
    elif not self.isfiller:
      return sr.roster.SomeRoster


def iter_referenced():
  yield from Team.__members__.values()


def save():
  for T in iter_referenced():
    T.srnewdata_apply()
  sr._data.save("team")
