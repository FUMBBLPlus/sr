import json
import urllib.request
import xml.etree.ElementTree as ET

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


def _get_xml_obj(url, force_request=False):
  url = url.lower()
  if not force_request and url in cache:
    return cache[url]
  response = urllib.request.urlopen(url)
  data = response.read()
  obj = ET.fromstring(data.decode('utf8'))
  cache[url] = obj
  return obj


def old_get__group_tournaments(groupId, *, force_request=False):
  url = f'https://{host}/xml:group?id={groupId}&op=tourneys'
  return _get_xml_obj(url, force_request)


def old_get__match(matchId, *, force_request=False):
  url = f'https://{host}/xml:matches?m={matchId}'
  return _get_xml_obj(url, force_request).find('match')


def deriv_get__group_tournament(groupId, tournamentId, *,
      force_request=False
  ):
  group_tournaments = get__group_tournaments(
        groupId, force_request=force_request
  )
  for tournament_data in group_tournaments:
    if tournament_data["id"] == tournamentId:
      return tournament_data


def get__coach(coachId, *, force_request=False):
  url = f'https://{host}/api/coach/get/{coachId}'
  return _get_json_obj(url, force_request)


def get__group_tournaments(groupId, *, force_request=False):
  url = f'https://{host}/api/group/tournaments/{groupId}'
  return _get_json_obj(url, force_request)


def get__match_get(matchId, *, force_request=False):
  url = f'https://{host}/api/match/get/{matchId}'
  return _get_json_obj(url, force_request)


def get__roster(rosterId, *, force_request=False):
  url = f'https://{host}/api/roster/get/{rosterId}'
  return _get_json_obj(url, force_request)


def get__team(teamId, *, force_request=False):
  url = f'https://{host}/api/team/get/{teamId}'
  return _get_json_obj(url, force_request)


def get__tournament_schedule(
      tournamentId, *, force_request=False
  ):
  url = f'https://{host}/api/tournament/schedule/{tournamentId}'
  return _get_json_obj(url, force_request)
