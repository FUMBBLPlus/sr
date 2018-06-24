import json
import urllib.request
import xml.etree.ElementTree as ET

host = 'fumbbl.com'


def _get_json_obj(url):
  url = url.lower()
  response = urllib.request.urlopen(url)
  data = response.read()
  obj = json.loads(data)
  return obj


def _get_xml_obj(url):
  url = url.lower()
  response = urllib.request.urlopen(url)
  data = response.read()
  obj = ET.fromstring(data.decode('utf8'))
  return obj


def old_get__group_tournaments(groupId):
  url = f'https://{host}/xml:group?id={groupId}&op=tourneys'
  return _get_xml_obj(url)


def old_get__match(matchId):
  url = f'https://{host}/xml:matches?m={matchId}'
  return _get_xml_obj(url).find('match')


def get__coach(coachId):
  url = f'https://{host}/api/coach/get/{coachId}'
  return _get_json_obj(url)


def get__group_tournaments(groupId):
  url = f'https://{host}/api/group/tournaments/{groupId}'
  return _get_json_obj(url)


def get__match(matchId):
  url = f'https://{host}/api/match/get/{matchId}'
  return _get_json_obj(url)


def get__roster(rosterId):
  url = f'https://{host}/api/roster/get/{rosterId}'
  return _get_json_obj(url)


def get__team(teamId):
  url = f'https://{host}/api/team/get/{teamId}'
  return _get_json_obj(url)


def get__tournament_schedule(tournamentId):
  url = f'https://{host}/api/tournament/schedule/{tournamentId}'
  return _get_json_obj(url)
