from . import fumbblapi
import sr


@sr.helper.idkey
class Match(metaclass=sr.helper.InstanceRepeater):

  def __init__(self, matchId: int):
    self._apidata = ...
    self._oldapidata = ...

  @property
  def apidata(self):
    if self._apidata is ...:
      self._apidata = fumbblapi.get__match(self.id)
    return self._apidata

  @property
  def conceded(self):
    for team in ("home", "away"):
      d = self.oldapidata.find(team).attrib
      if d.get("conceded", "false").lower() == "true":
        return sr.team.Team(int(d["id"]))

  @property
  def finished(self):
    d = self.apidata
    return sr.time.strptime(f'{d["date"]} {d["time"]}')

  @property
  def oldapidata(self):
    if self._oldapidata is ...:
      self._oldapidata = fumbblapi.old_get__match(self.id)
    return self._oldapidata
