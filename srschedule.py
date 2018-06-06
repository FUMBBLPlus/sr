import functools

import fumbblapi
import srdata
import srmatch
import srtime


def _end_time_passer(schedule, *, is_dst=False, func=None):
  end_time_ = end_time(schedule, is_dst=is_dst)
  if end_time_:
    return func(end_time_)


def end_time(schedule, *, is_dst=None):
  modified_ = modified(schedule, is_dst=is_dst)
  if modified_:
    return modified_
  matches_ = matches(schedule)
  if matches_:
    last_match = fumbblapi.get__match_get(max(matches_))
    return srmatch.finished_time(last_match, is_dst=is_dst)


def get(tournamentId):
  if str(tournamentId) in srdata.data["schedule"]:
    return srdata.data["schedule"][str(tournamentId)]
  else:
    return fumbblapi.get__tournament_schedule(tournamentId)


def has_filler(schedule):
  teams_ = teams(schedule, with_fillers=True)
  return bool(teams_ & srdata.data["fillerteams"])


def highest_match_id(schedule):
  matches_ = matches(schedule)
  if matches_:
    return max(matches_)
  else:
    return None


def matches(schedule):
  matches_ = {
      matchup["result"]["id"]
      for matchup in schedule
      if matchup.get("result", {}).get("id")
  }
  return matches_


def modified(schedule, *, is_dst=None):
  modifieds_ = {
      srtime.strptime(matchup["modified"], is_dst=is_dst)
      for matchup in schedule
      if matchup["modified"] is not None
  }
  if modifieds_:
    return max(modifieds_)
  else:
    return None


report_date = functools.partial(
    _end_time_passer, func=srtime.report_date
)


report_weeknr = functools.partial(
    _end_time_passer, func=srtime.report_weeknr
)


def rounds(schedule):
  rounds = {
      matchup["round"] for matchup in schedule
      if matchup.get('round') is not None
  }
  if rounds:
    return max(rounds)


def size(schedule):
  matchups = {
      matchup for matchup in schedule
      if matchup.get('round') == 1
  }
  return len(matchups) * 2


def teams(schedule, with_fillers=False):
  teams_ = {
      team["id"]
      for matchup in schedule
      for team in matchup["teams"]
      if matchup.get('round') == 1
  }
  if not with_fillers:
    teams_ -= srdata.data["fillerteams"]
  return teams_


weeknr = functools.partial(
    _end_time_passer, func=srtime.weeknr
)
