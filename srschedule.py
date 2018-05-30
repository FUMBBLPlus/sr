import fumbblapi
import srdata
import srmatch
import srtime


def end_time(schedule, *, is_dst=None):
  modified_ = modified(schedule)
  if modified_:
    return modified_
  matches_ = matches(schedule)
  if matches_:
    last_match = fumbblapi.get__match_get(max(matches_))
    return srmatch.finished_time(last_match, is_dst=is_dst)


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


def modified(schedule):
  modifieds_ = {
      srtime.strptime(matchup["modified"])
      for matchup in schedule
      if matchup["modified"] is not None
  }
  if modifieds_:
    return max(modifieds_)
  else:
    return None


def teams(schedule):
  teams_ = {
      team["id"]
      for matchup in schedule
      for team in matchup["teams"]
      if matchup.get('round') == 1
  }
  teams_ -= srdata.data["fillerteams"]
  return teams_


def weeknr(schedule, *, is_dst=False):
  end_time_ = end_time(schedule, is_dst=is_dst)
  if end_time_:
    return srtime.weeknr(end_time_)
