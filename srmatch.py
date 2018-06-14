import srtime


def conceded(old_match):
  for team in ('home', 'away'):
    a = old_match.find(team).attrib
    if a.get('conceded', 'false').lower() == 'true':
      return int(a['id'])


def finished_time(match, *, is_dst=None):
  s = match["date"] + ' ' + match["time"]
  return srtime.strptime(s, is_dst=is_dst)
