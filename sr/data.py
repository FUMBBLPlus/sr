import json
import pathlib

import sr

data = {}

INTKEYS = (
    "fixed_api_schedule",
    "group",
    "rostername",
    "tournament",
)
SETS = "fillerteams", "groups_watched"

curr_path = pathlib.Path(__file__).parent

def srdatadir():
  srdatadir = sr.settings["sr-data.path"]
  if srdatadir:
    p = pathlib.Path(srdatadir)
    if p.is_dir():
      return p

def reload(name=None):
  if name is not None:
    name = name.lower()
  # cleanup
  keys = set(data.keys())
  if name:
    keys &= {name}
  for k in keys:
    del data[k]
  # get sr-data path
  srdatadir_ = srdatadir()
  if not srdatadir_:
    return False
  # filter objects
  if name:
    filegen = [srdatadir_ / f'{name}.json']
  else:
    filegen = srdatadir_.glob('*.json')
  # read objects
  for p in filegen:
    with p.open() as f:
      o = json.load(f)
    name = p.stem.lower()
    if name in INTKEYS:
      o = {int(k): v for k, v in o.items()}
    elif name in SETS:
      o = set(o)
    data[name] = o
  return True
reload()


def save(name):
  name = name.lower()
  s = _dumpfunc[name](name)
  srdatadir_ = srdatadir()
  if not srdatadir_:
    return False
  with (srdatadir_ / f'{name}.json').open("w") as f:
    f.write(s)
  return True


def dumps_intkey_one_val_per_row(name):
  keyval_strings = ['"{k}": {j}'.format(
          k=k,
          j=json.dumps(v, ensure_ascii=False, sort_keys=True)
      )
      for k, v in sorted(data[name].items())]
  s = "{\n" + ",\n".join(keyval_strings) + "\n}"
  return s

_dumpfunc = {
    "coach": dumps_intkey_one_val_per_row,
    "team": dumps_intkey_one_val_per_row,
    "tournament": dumps_intkey_one_val_per_row,
}
