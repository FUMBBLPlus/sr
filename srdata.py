import json
import pathlib


data = None
directory = None


def load(directory_):
  global directory
  global data
  paths = pathlib.Path(directory_).glob('*.json')
  if not paths:
    raise ValueError('wrong directory')
  data = {}
  for _p in paths:
    with _p.open() as _f:
      data[_p.stem] = json.load(_f)
  try:
    data['fillerteams'] = set(data['fillerteams'])
    data['tournament'] = {t[0]: t for t in data['tournaments']}
  except KeyError:
    data = None
    raise ValueError('wrong directory')
  directory = directory_
