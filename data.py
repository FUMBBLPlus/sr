import json
import pathlib

data = {}

INTKEYS = (
    "fixed_api_schedule",
    "group",
    "rostername",
    "tournament",
)
SETS = "fillerteams", "groups_watched"


def datadir():
  curr_path = pathlib.Path(__file__).parent
  with (curr_path / "settings.json").open() as f:
    settings = json.load(f)
  return curr_path / settings["sr-data.path"]

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
  datadir_ = datadir()
  # filter objects
  if name:
    filegen = [datadir_ / f'{name}.json']
  else:
    filegen = datadir_.glob('*.json')
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
reload()


def save(name):
  name = name.lower()
  s = _dumpfunc[name](name)
  with (datadir() / f'{name}.json').open("w") as f:
    f.write(s)


def dumps_intkey_one_val_per_row(name):
  keyval_strings = ['"{k}": {j}'.format(
          k=k,
          j=json.dumps(v, ensure_ascii=False, sort_keys=True)
      )
      for k, v in sorted(data[name].items())]
  s = "{\n" + ",\n".join(keyval_strings) + "\n}"
  return s

_dumpfunc = {
    "tournament": dumps_intkey_one_val_per_row
}
