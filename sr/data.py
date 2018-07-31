import json
import pathlib

import sr

data = {}

INTKEYS = (
    "coach",
    "api_fixed_get__tournament_schedule",
    "group",
    "rostername",
    "team",
    "tournament",
)
SETS = "fillerteams", "observed_groups"

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
    with p.open(encoding="utf8") as f:
      o = json.load(f)
    name = p.stem.lower()
    if name in INTKEYS:
      o = {int(k): v for k, v in o.items()}
    elif name in SETS:
      o = set(o)
    data[name] = o
  return True
reload()


def rankings_file(reportNr, name):
  foldernum = int(reportNr) // 100 * 100
  foldername = f'{foldernum:0>7}'
  filename = f'{reportNr:0>7}{name.lower()[0]}.json'
  return srdatadir() / "rankings" / foldername / filename

def delete_rankings(reportNr, name):
  p = rankings_file(reportNr, name)
  if p.is_file():
    p.unlink()  # delete file

def load_rankings(reportNr, name):
  FullRankingsRow = sr.report.Report.FullRankingsRow
  pi = FullRankingsRow._fields.index("Performer")
  pi -= 1  # rownum (first column) is excluded from the dump
  if name == "coach":
    Pcls = sr.coach.Coach
  elif name == "team":
    Pcls = sr.team.Team
  p = rankings_file(reportNr, name)
  if p.is_file():
    with p.open() as f:
      rankings_ = json.load(f)  # teamIds are strings
    return tuple(
        FullRankingsRow(*(
            [rownum] + r[:pi] + [Pcls(r[pi])] + r[pi+1:]
        ))
        for rownum, r in enumerate(rankings_, 1)
    )

def save_rankings(reportNr, name):
  FullRankingsRow = sr.report.Report.FullRankingsRow
  pi = FullRankingsRow._fields.index("Performer")
  report = sr.report.Report(reportNr)
  rankings = getattr(report, f'{name}fullrankings')
  rankings_ = [list(r) for r in rankings]
  for r in rankings_:
    r[pi] = r[pi].id
  rankings_ = [r[1:] for r in rankings_]  # rownum is skipped
  p = rankings_file(reportNr, name)
  p.parent.mkdir(parents=True, exist_ok=True)  # ensure dir
  with p.open("w") as f:
    f.write(dumps_one_obj_per_row(rankings_))


def results_file(tournamentId):
  foldernum = int(tournamentId) // 1000 * 1000
  foldername = f'{foldernum:0>8}'
  filename = f'{tournamentId:0>8}.json'
  return srdatadir() / "results" / foldername / filename


def delete_results(tournamentId):
  p = results_file(tournamentId)
  if p.is_file():
    p.unlink()  # delete file


def load_results(tournamentId):
  p = results_file(tournamentId)
  if p.is_file():
    with p.open() as f:
      results_ = json.load(f)  # teamIds are strings
    return {
        sr.team.Team(int(t)):
        [sr.tournament.Matchup.Result(c) for c in r]
        for t, r in results_.items()
    }


def save_results(tournamentId):
  strresults = sr.tournament.Schedule(tournamentId).strresults
  results_ = {T.id: s for T, s in strresults.items()}
  p = results_file(tournamentId)
  p.parent.mkdir(parents=True, exist_ok=True)  # ensure dir
  with p.open("w") as f:
    json.dump(results_, f, indent='\t', sort_keys=True)


def save(name):
  name = name.lower()
  if name not in _dumpfunc:
    s = json.dumps(
        data[name],
        ensure_ascii = False,
        indent = "\t",
        sort_keys = True,
    )
  else:
    s = _dumpfunc[name](name)
  srdatadir_ = srdatadir()
  if not srdatadir_:
    return False
  with (srdatadir_ / f'{name}.json').open("w", encoding="utf8") as f:
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

def dumps_one_obj_per_row(listofobjs):
  substrings = [
      json.dumps(o, ensure_ascii=False, sort_keys=True)
      for o in listofobjs
  ]
  s = "[\n" + ",\n".join(substrings) + "\n]"
  return s


_dumpfunc = {
    "coach": dumps_intkey_one_val_per_row,
    "group": dumps_intkey_one_val_per_row,
    "team": dumps_intkey_one_val_per_row,
    "tournament": dumps_intkey_one_val_per_row,
}
