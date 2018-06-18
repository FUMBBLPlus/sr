import fumbblapi
import srdata
import srmatch


def calculate(class_, progression, is_winner):
  class_parts = class_.split('/')
  keyclass = get_keyclass(class_)
  points = srdata.data["points"][keyclass]
  parts1 = [s.strip() for s in points.split('*')]
  parts1[0] = int(parts1[0])
  if class_parts[0] == 'E':
    parts2 = [int(s.strip()) for s in parts1[1].split('-')]
    pts = parts1[:1] + parts2
    normprog = list(reversed(list(enumerate(progression, 1))))
    wskip = 0
    for rou, res in normprog:
      if res in 'CFQ':
        wskip += 1
      elif res == 'W' and wskip:
        wskip -= 1
      elif res == 'W':
        break
    else:
      if wskip:
        return 0
      else:
        rou = 0
    return pts[rou]
  else:
    parts1[2] = int(parts1[2])
    parts2 = [int(s.strip()) for s in parts1[1].split('/')]
    pts = parts1[0]
    for res in progression:
      if res in 'CFQ':
        pts -= sum(parts2[:2])
      elif res in 'WDL':
        pts += parts2['WDL'.index(res)]
    if is_winner:
      pts += parts1[2]
    pts = max(0, pts)
    return pts


def get_keyclass(class_):
  points = srdata.data["points"]
  if class_ in points:
    return class_
  class_parts = class_.split('/')
  try:
    v = int(class_parts[-1])
  except ValueError:
    raise KeyError()
  for k in points:
    k_parts = k.split('/')
    if (
        len(k_parts) == len(class_parts)
        and k_parts[:-1] == class_parts[:-1]
        and '-' in k_parts[-1]
      ):
      start, end = [int(a) for a in k_parts[-1].split('-')]
      r = range(start, end + 1)
      if v in r:
        return k
  raise KeyError()


def is_ugly(progression):
  return bool(set(progression) & set('CFQ'))


def total_points_allocated(class_):
  points = srdata.data["points"]
  rule = points[class_]
  initial, _p = [a.strip() for a in rule.split('*')]
  initial = int(initial)
  ps = [int(a.strip()) for a in reversed(_p.split('-'))]
  ps.append(initial)
  result = ps[0]
  for i, p in enumerate(ps[1:]):
    result += p * 2**i
  return result
