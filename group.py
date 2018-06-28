import enum

from . import fumbblapi
import sr


class Group(metaclass=sr.helper.InstanceRepeater):

  class SRData(sr.helper.NoInstances):
    class Idx(enum.IntEnum):
      default_tournament_ismain = 0
      default_tournament_rank = 1
      default_tournament_level = 2
      default_tournament_srtitle = 3
      default_tournament_srfsg = 4

  def __init__(self, groupId):
    self._apidata_tournament = ...
    self._oldapidata_tournament = ...
    self._name = ...
    self._default_tournament_ismain = ...
    self._default_tournament_rank = ...
    self._default_tournament_level = ...
    self._default_tournament_srtitle = ...
    self._default_tournament_srfsg = ...

  def __repr__(self):
    return f'Group({self.id})'

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
  def default_tournament_ismain(self):
    if self._default_tournament_ismain is ...:
      if self.srdata:
        srdataidx = self.SRData.Idx .default_tournament_ismain
        return self.srdata[srdataidx]

  @property
  def default_tournament_level(self):
    if self._default_tournament_level is ...:
      if self.srdata:
        srdataidx = self.SRData.Idx .default_tournament_level
        return self.srdata[srdataidx]

  @property
  def default_tournament_rank(self):
    if self._default_tournament_rank is ...:
      if self.srdata:
        srdataidx = self.SRData.Idx .default_tournament_rank
        return self.srdata[srdataidx]

  @property
  def default_tournament_srfsg(self):
    if self._default_tournament_srfsg is ...:
      if self.srdata:
        srdataidx = self.SRData.Idx .default_tournament_srfsg
        return self.srdata[srdataidx]

  @property
  def default_tournament_srtitle(self):
    if self._default_tournament_srtitle is ...:
      if self.srdata:
        srdataidx = self.SRData.Idx .default_tournament_srtitle
        return self.srdata[srdataidx]


  @property
  def id(self):
    return self._KEY[0]  # set by metaclass

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
  def srdata(self):
    srdata_row = sr.data["group"].get(self.id)
    if srdata_row:
      return tuple(srdata_row)

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
      tournament.group = self

def watched():
  return {
      Group(groupId) for groupId in sr.data["groups_watched"]
  }
