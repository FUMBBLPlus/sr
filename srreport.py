import collections
import copy
import functools
import types

import srdata
import srpoints
import srschedule
import srslot
import srteam
import srtournament


class Report:

  CoachPointsKey = collections.namedtuple(
      'CoachPointsKey',
      ('mainTournamentId', 'coach'),
  )

  PointsArrayItem = collections.namedtuple(
      'PointsArrayItem',
      ('tournamentId', 'progression', 'is_ugly', 'points'),
  )

  PointsValue = collections.namedtuple(
      'PointsValue',
      ('is_ugly', 'points'),
  )

  TeamPointsKey = collections.namedtuple(
      'TeamPointsKey',
      ('mainTournamentId', 'teamId'),
  )

  def __init__(self, weeknr):
    self._weeknr = weeknr
    self.reset()

  @property
  def base_coach_slots(self):
    return srslot.coach_slots(self.weeknr)

  @property
  def base_team_slots(self):
    return srslot.team_slots(self.weeknr)

  @property
  def coaches(self):
    if self._coaches is None:
      self._coaches = frozenset(
          self.team_info(teamId)["coach"]
          for teamId in self.teamIds
      )
    return self._coaches

  @property
  def coach_points(self):
    # coach points of main tournaments
    # after multiple applications
    if self._coach_points is None:
      ct = self.coach_teams_of_tournaments
      result = {
        k: self.PointsValue(
          any(
              self.team_points[
                  self.TeamPointsKey(k.mainTournamentId, teamId)
              ].is_ugly
              for teamId in teamIds
          ),
          sum(
              self.team_points[
                  self.TeamPointsKey(k.mainTournamentId, teamId)
              ].points
              for teamId in teamIds
          ),
        )
        for k, teamIds in ct.items()
      }
      self._coach_points =  types.MappingProxyType(result)
    return self._coach_points

  @property
  def coach_slots(self):
    if self._coach_slots is None:
      b = self.base_coach_slots
      self._coach_slots = types.MappingProxyType({
          coach: copy.copy(b) for coach in sorted(self.coaches)
      })
    return self._coach_slots

  @property
  def coach_teams_of_tournaments(self):
    if self._coach_teams_of_tournaments is None:
      result = {}
      for key0 in self.raw_points:
          team_info = self.team_info(key0.teamId)
          if team_info:
            key1 = self.CoachPointsKey(
                key0.mainTournamentId, team_info["coach"]
            )
            result.setdefault(key1, set()).add(key0.teamId)
      result = types.MappingProxyType({
          k: frozenset(result[k]) for k in sorted(result)
      })
      self._coach_teams_of_tournaments = result
    return self._coach_teams_of_tournaments

  @property
  def enter_tournaments(self):
    if self._enter_tournaments is None:
      TI = srdata.TournamentIdx
      gen = srtournament.iter_weeknr_tournaments(
          self.weeknr, move='enter'
      )
      self._enter_tournaments = types.MappingProxyType({
          row[TI.ID]: row for row in gen
      })
    return self._enter_tournaments


  @property
  def exit_tournaments(self):
    if self._exit_tournaments is None:
      TI = srdata.TournamentIdx
      gen = srtournament.iter_weeknr_tournaments(
          self.weeknr, move='exit'
      )
      self._exit_tournaments = types.MappingProxyType({
          row[TI.ID]: row for row in gen
      })
    return self._exit_tournaments


  @property
  def fallback_slot_group(self):
    return srslot.fallback_slot_group(self.weeknr)

  @property
  def multiple_applications(self):
    return types.MappingProxyType({
          k: set_
          for k, set_ in self.coach_teams_of_tournaments.items()
          if 1 < len(set_)
      })

  @property
  def points(self):
    # team points of individual tournaments
    # after multiple applications
    if self._points is None:
      result = dict(self.raw_points)
      for k, teamIds in self.multiple_applications.items():
        min_pts = min(
            sum(
                i.points
                for i in self.raw_points[
                    self.TeamPointsKey(
                        k.mainTournamentId, teamId
                    )
                ]
            )
            for teamId in teamIds)
        pts = min_pts // len(teamIds)
        for teamId in teamIds:
          k2 = self.TeamPointsKey(k.mainTournamentId, teamId)
          tournamentId = k.mainTournamentId
          is_ugly = any(i.is_ugly for i in self.raw_points[k2])
          i = self.PointsArrayItem(
              k.mainTournamentId,
              srpoints.PROGRESSION_MULTIPLE,
              is_ugly,
              pts,
          )
          result[k2] = (i,)
      self._points = types.MappingProxyType(result)
    return self._points

  @property
  def teamIds(self):
    if self._teamIds is None:
      self._teamIds = frozenset(
          t.teamId for t in self.raw_points
          if self.team_info(
              t.teamId, include_check=False
          ) is not None
      )
    return self._teamIds

  @property
  def team_points(self):
    # team points of main tournaments
    # after multiple applications
    if self._team_points is None:
      ct = self.coach_teams_of_tournaments
      result = {
        k: self.PointsValue(
          any(i.is_ugly for i in points_array),
          sum(i.points for i in points_array),
        )
        for k, points_array in self.points.items()
      }
      self._team_points = types.MappingProxyType(result)
    return self._team_points

  @property
  def team_slots(self):
    if self._team_slots is None:
      b = self.base_team_slots
      self._team_slots = types.MappingProxyType({
          teamId: copy.copy(b)
          for teamId in sorted(self.teamIds)
      })
    return self._team_slots

  @property
  def tournaments(self):
    if self._tournaments is None:
      TI = srdata.TournamentIdx
      gen = srtournament.iter_weeknr_tournaments(self.weeknr)
      self._tournaments = types.MappingProxyType({
          row[TI.ID]: row for row in gen
      })
    return self._tournaments

  @property
  def raw_points(self):
    # team points of individual tournaments
    # before multiple applications
    if self._raw_points is None:
      TI = srdata.TournamentIdx
      result = {}
      for row in self.tournaments.values():
        main_id = top_id = row[TI.TOP_ID]
        if top_id is None:
          continue
        elif top_id == 0:
          main_id = row[TI.ID]
        results = srschedule.get_results(row[TI.ID])
        for teamId, progression in results.items():
          key = self.TeamPointsKey(main_id, teamId)
          is_winner = (teamId == row[TI.WINNER_ID])
          pts = srpoints.calculate(
              row[TI.CLASS], progression, is_winner
          )
          is_ugly_ = srpoints.is_ugly(progression)
          v = self.PointsArrayItem(
              row[TI.ID], progression, is_ugly_, pts
          )
          result.setdefault(key, []).append(v)
      result = types.MappingProxyType({
          k: tuple(result[k]) for k in sorted(result)
      })
      self._raw_points = result
    return self._raw_points

  @property
  def slot_points_included(self):
    return srslot.slot_points_included(self.weeknr)

  @property
  def weeknr(self):
    return self._weeknr

  def reset(self):
    self._coaches = None
    self._coach_points = None
    self._coach_slots = None
    self._coach_teams_of_tournaments = None
    self._enter_tournaments = None
    self._exit_tournaments = None
    self._points = None
    self._raw_points = None
    self._teamIds = None
    self._team_data = None
    self._team_points = None
    self._team_slots = None
    self._tournaments = None

  def team_info(self, teamId, *, include_check=True):
    if include_check and teamId not in self.teamIds:
      raise ValueError('team not in report')
    return srteam.info(teamId, weeknr=self.weeknr)
