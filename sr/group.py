import enum

from . import fumbblapi
import sr


@sr.helper.srdata("group",
    (
        "default_tournament_ismain",
        "default_tournament_rank",
        "default_tournament_level",
        "default_tournament_srtitle",
        "default_tournament_srfsgname",
    ),
)
@sr.helper.idkey
class Group(metaclass=sr.helper.InstanceRepeater):

  def __init__(self, groupId):
    self._apidata_tournament = ...
    self._oldapidata_tournament = ...
    self._name = ...

  def __str__(self):
    return self.name or '* Some Group *'

  @property
  def apidata_tournament(self):
    if self._apidata_tournament is ...:
      ts = fumbblapi.get__group_tournaments(self.id)
      self._apidata_tournament = {
          sr.tournament.Tournament(t["id"]): t
          for t in ts
      }
      # The purpose of next line is explained in the method.
      self.set_for_tournaments(self._apidata_tournament)
    return self._apidata_tournament

  @property
  def name(self):
    if self._name is ...:
      # the request below also sets the name
      self.oldapidata_tournament
    return self._name

  @property
  def oldapidata_tournament(self):
    if self._oldapidata_tournament is ...:
      ts = fumbblapi.old_get__group_tournaments(self.id)
      # I have the group name here so is set it...
      self._name = ts.find("name").text
      self._oldapidata_tournament = {
          sr.tournament.Tournament(int(t.attrib["id"])): t
          for t in ts.iter("tournament")
      }
      # The purpose of next line is explained in the method.
      self.set_for_tournaments(self._oldapidata_tournament)
    return self._oldapidata_tournament

  @property
  def tournaments(self):
    tournaments_ = set(self.apidata_tournament)
    self.set_for_tournaments(tournaments_)  # explained below
    return tournaments_

  def set_for_tournaments(self, tournaments_):
    # As there is no way to get the group of an arbitrary
    # tournament from FUMBBL I catch every posiibility to set
    # the group of a tournament if its known.
    for tournament in tournaments_:
      tournament.groupId = self.id



def observed():
  return {
      Group(groupId) for groupId in sr.data["observed_groups"]
  }
