import enum
import json
import pathlib


data = None
directory = None


class TournamentIdx(enum.IntEnum):
  ID = 0
  TOP_ID = 1
  GROUP_ID = 2
  NAME = 3
  CLASS = 4
  WINNER_ID = 5
  TITLE = 6
  FIRST_SLOT_GROUP = 7
  ENTER_WEEKNR = 8
  EXIT_WEEKNR = 9


def load(directory_):
  global directory
  global data
  directory_ = pathlib.Path(directory_)
  paths = directory_.glob('*.json')
  if not paths:
    raise ValueError('wrong directory')
  data = {}
  for _p in paths:
    with _p.open() as _f:
      data[_p.stem] = json.load(_f)
  try:
    data['fillerteams'] = set(data['fillerteams'])
    data['rostername'] = {
        int(rosterId): li
        for rosterId, li in data['rostername'].items()
    }
    data['tournament'] = {
        t[TournamentIdx.ID]: t for t in data['tournaments']
    }
  except KeyError:
    data = None
    raise ValueError('wrong directory')
  directory = directory_
