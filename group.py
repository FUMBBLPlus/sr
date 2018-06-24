from . import fumbblapi
import sr


class Group(metaclass=sr.helper.InstanceRepeater):

  def __init__(self, groupId):
    self._apidata_tournament = ...
    self._oldapidata_tournament = ...

  def __repr__(self):
    return f'Group({self.id})'

  def __str__(self):
    return self.name or '* Some Group *'

  @property
  def apidata_tournament(self):
    raise NotImplementedError()

  @property
  def id(self):
    return self._KEY[0]  # set by metaclass

  @property
  def oldapidata_tournament(self):
    if self._oldapidata_tournament is ...:
      ts = fumbblapi.old_get__group_tournaments(self.id)
      self._oldapidata_tournament = {
          sr.tournament.Tournament(int(t.attrib["id"])): t
          for t in ts.iter("tournament")
      }
    return self._oldapidata_tournament

