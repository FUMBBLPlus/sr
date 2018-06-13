import fumbblapi
import srdata


def format_(groupId, tournamentId):
  ts = fumbblapi.old_get__group_tournaments(groupId)
  for t in ts.iter('tournament'):
    if int(t.attrib["id"]) == tournamentId:
      return t.find('type').text


def get_class_by_teams(rank, level, format__, teams):
  class3 = f'{rank}/{level}/{format__}'
  alloc_keys0 = srdata.data["points"].keys()
  alloc_keys = {k for k in alloc_keys0 if k.startswith(class3)}
  size_classes0 = [
      a.split('/')[-1].split('-') for a in alloc_keys
  ]
  size_classes1 = [
      ([t[0], t[1]] if len(t)==1 else t) for t in size_classes0
  ]
  size_classes = sorted(
      [range(int(t[0]), int(t[1]) + 1) for t in size_classes1],
      key=lambda r: (r.start, r.stop)
  )
  for r in size_classes:
    if teams in r:
      class4 = f'{class3}/{r.start}-{r.stop-1}'
      return class4
