import functools
import math

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
  DATA_NAME = "fixed_api_schedule"
  if str(tournamentId) in srdata.data[DATA_NAME]:
    return srdata.data[DATA_NAME][str(tournamentId)]
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


def is_elim(schedule):
  size0 = size(schedule)
  rounds_ = {
      matchup["round"] for matchup in schedule
      if matchup.get('round') is not None
  }
  R = max(rounds_)
  for r in range(2, R + 1):
    size1 = size(schedule, round_=r)
    if size1 != size0:
      return True
  return False


def matches(schedule):
  matches_ = {
      matchup["result"]["id"]
      for matchup in schedule
      if matchup.get("result", {}).get("id")
  }
  return matches_


def matchups_of_round(schedule, round_):
  return [
      matchup for matchup in schedule
      if matchup.get('round') == round_
  ]


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


def positions(schedule):
  return {matchup["position"] for matchup in schedule}


report_date = functools.partial(
    _end_time_passer, func=srtime.report_date
)


report_weeknr = functools.partial(
    _end_time_passer, func=srtime.report_weeknr
)


def results(schedule, *, is_elim_=None):
  if is_elim_ is None:
    is_elim_ = is_elim(schedule)
  schedule = sort(schedule)
  teams_ = teams(schedule, round_=None)
  results_ = {teamId: [] for teamId in teams_}
  n_rounds = rounds(schedule, is_elim_=is_elim_)
  for r in range(1, n_rounds + 1):
    for li in results_.values():
      li.append('.')
    for p in matchups_of_round(schedule, r):
      re = p.get("result", {"id": 0, "winner": 0})
      matchId = re["id"]
      winner = int(re["winner"])
      if matchId:
        old_match = fumbblapi.old_get__match(matchId)
        conceded = srmatch.conceded(old_match)
        scores = {re["teams"][i]["score"] for i in range(2)}
        draw = (len(scores) == 1)
      else:
        conceded = None
        draw = False
      p_teams = {di["id"] for di in p["teams"]}
      p_teams &= teams_
      for teamId in p_teams:
        li = results_[teamId]
        if matchId and draw and not is_elim_:
          li[-1] = 'D'  # draw by match
        elif matchId and teamId == winner:
          li[-1] = 'W'  # win by match
        elif matchId and teamId == conceded:
          li[-1] = 'C'  # conceded on a match
        elif matchId:
          li[-1] = 'L'  # loss by match
        elif teamId == winner and len(p_teams) == 2:
          li[-1] = 'B'  # bye against a real team
        elif teamId == winner:
          li[-1] = 'b'  # bye against a filler team
        elif winner:
          li[-1] = 'F'  # fortfeit
        else:
          li[-1] = '?'  # pending
  results_ = {
      teamId: ''.join(li) for teamId, li in results_.items()
  }
  return results_


def round_started(schedule, round_):
  return any(
      p["result"]["id"]
      for p in matchups_of_round(schedule, round_)
  )


def rounds(schedule, is_elim_=None):
  if is_elim_ is None:
    is_elim_ = is_elim(schedule)
  if is_elim_:
    p = max(positions(matchups_of_round(schedule, 1)))
    # p=1 for final; 3 for semi-final; 7 for quaterfinal; etc.
    r = int(math.log(p + 1, 2))
  else:
    rounds_ = {
        matchup["round"] for matchup in schedule
        if matchup.get('round') is not None
    }
    if not rounds_:
      r = 0
    else:
      r = max(rounds_)
    # Sometimes non-elimination format tournaments' round value
    # is unset by tournament admins and they only realize that
    # when another round gets drawn after the intended end of
    # the tournament. They then forfeit all matches of the last
    # round. SR should not treat these forfeits as real ones.
    # Example tournamentId: 19144.
    round_started_ = False
    while r and not round_started_:
      round_started_ = round_started(schedule, r)
      if not round_started_:
        r -= 1
  return r


def size(schedule, *, round_=1):
  return len(matchups_of_round(schedule, round_)) * 2


def sort(schedule):
  return sorted(schedule, key=lambda p: (
      p["round"],
      p["position"],
  ))


def teams(schedule, with_fillers=False, round_=1):
  if round_:
    teams_ = {
        team["id"]
        for matchup in matchups_of_round(schedule, round_)
        for team in matchup["teams"]
    }
  else:
    teams_ = {
        team["id"]
        for matchup in schedule
        for team in matchup["teams"]
    }
  if not with_fillers:
    teams_ -= srdata.data["fillerteams"]
  return teams_


weeknr = functools.partial(
    _end_time_passer, func=srtime.weeknr
)
