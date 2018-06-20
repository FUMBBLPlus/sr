import json

import fumbblapi
import srroster

deleted_team = '{"players": []}'

def info(teamId, weeknr=None):
  teamId = int(teamId)
  team_data = fumbblapi.get__team(teamId)
  if team_data == json.loads(deleted_team):
    return
  coach = team_data["coach"]["name"]
  name = team_data["name"]
  rosterId = team_data["roster"]["id"]
  if weeknr is None:
    roster = team_data["roster"]["name"]
  else:
    roster = srroster.name(rosterId, weeknr)
  return {
      'id': teamId,
      'coach': coach,
      'name': name,
      'roster': roster,
      'rosterId': rosterId,
  }

