import json
import pathlib
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import sr

import yarl


host = 'fumbbl.com'


cache = {
}


def url2path(url):
  y = yarl.URL(url)
  # sort query
  y = y.with_query({k: y.query[k] for k in sorted(y.query)})
  p = sr._data.srdatadir() / "fumbblapl_cache"
  for part in  y.parts[1:-1]:
    p /= urllib.parse.quote(part, "")
  filename = urllib.parse.quote(y.parts[-1], "")
  if y.query:
    filename += urllib.parse.quote("?" + y.query_string, "")
  p /= filename
  return p


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


def get__coach(coachId, *, force_request=False):
  url = f'https://{host}/api/coach/get/{coachId}'
  return _get_json_obj(url, force_request)


def get__coach_search(term, *, force_request=False):
  url = f'https://{host}/api/coach/search/{term}'
  return _get_json_obj(url, force_request)


def get__group_tournaments(groupId, *, force_request=False):
  url = f'https://{host}/api/group/tournaments/{groupId}'
  return _get_json_obj(url, force_request)


def get__match(matchId, *, force_request=False):
  url = f'https://{host}/api/match/get/{matchId}'
  return _get_json_obj(url, force_request)


def get__roster(rosterId, *, force_request=False):
  url = f'https://{host}/api/roster/get/{rosterId}'
  return _get_json_obj(url, force_request)


def get__team(teamId, *, force_request=False):
  url = f'https://{host}/api/team/get/{teamId}'
  return _get_json_obj(url, force_request)


def get__tournament_schedule(
      tournamentId, *, force_request=False,
      replace_with_fixed=True,
      load_cached=True,
  ):
  srdataname = "api_fixed_get__tournament_schedule"
  if tournamentId in sr.data[srdataname] and replace_with_fixed:
    return sr.data[srdataname][tournamentId]
  if load_cached:
    obj = sr._data.load_fumbblapi_cache_schedule(tournamentId)
    if obj is not None:
      return obj
  url = f'https://{host}/api/tournament/schedule/{tournamentId}'
  return _get_json_obj(url, force_request)
