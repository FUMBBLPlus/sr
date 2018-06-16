import fumbblapi
import srdata
import srmatch


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
