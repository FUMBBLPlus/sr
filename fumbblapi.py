import json
import urllib.request


host = 'fumbbl.com'

cache = {
}

def _get_json_obj(url, force_request=False):
  url = url.lower()
  if not force_request and url in cache:
    return cache[url]
  response = urllib.request.urlopen(url)
  data = response.read()
  obj = json.loads(data)
  cache[url] = obj
  return obj


def get__group_tournaments(groupId, *, force_request=False):
  url = f'https://{host}/api/group/tournaments/{groupId}'
  return _get_json_obj(url, force_request)


def get__match_get(matchId, *, force_request=False):
  url = f'https://{host}/api/match/get/{matchId}'
  return _get_json_obj(url, force_request)


def get__tournament_schedule(
      tournamentId, *, force_request=False
  ):
  url = f'https://{host}/api/tournament/schedule/{tournamentId}'
  return _get_json_obj(url, force_request)
