import fumbblapi


def format_(groupId, tournamentId):
  ts = fumbblapi.old_get__group_tournaments(groupId)
  for t in ts.iter('tournament'):
    if int(t.attrib["id"]) == tournamentId:
      return t.find('type').text
