import copy
import json
import pathlib

import sr

data = {}

INTKEYS = (
    "coach",
    "api_fixed_get__tournament_schedule",
    "group",
    "rostername",
    "rostershorthand",
    "team",
    "tournament",
)
SETS = (
    "fillerteams",
    "observed_groups",
    "coachpointsnote",
)

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


def save(name):
  name = name.lower()
  if name not in _dumpfunc:
    if name in SETS:
      data_ = sorted(data[name])
    else:
      data_ = data[name]
    s = json.dumps(
        data_,
        ensure_ascii = False,
        indent = "\t",
        sort_keys = True,
    )
  else:
    s = _dumpfunc[name](name)
  srdatadir_ = srdatadir()
  if not srdatadir_:
    return False
  pathobj = srdatadir_ / f'{name}.json'
  with pathobj.open("w", encoding="utf8") as f:
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
  Result = sr.tournament.Matchup.Result
  p = results_file(tournamentId)
  if p.is_file():
    with p.open() as f:
      results_ = json.load(f)
    d = {}
    for teamIdstr, li in results_.items():
      team = sr.team.Team(int(teamIdstr))
      for item in li:
        if item is not None:
          resultobjvalue, oppoteamId, matchId = item
          item[0] = resultobj = Result(resultobjvalue)
          if oppoteamId is not None:
            item[1] = oppoobj = sr.team.Team(oppoteamId)
          if matchId is not None:
            item[2] = matchobj = sr.match.Match(matchId)
      d[team] = li
    return d

def save_results(tournamentId):
  p = results_file(tournamentId)
  if p.is_file():
    return False
  results = sr.tournament.Schedule(tournamentId).results
  d = {}
  for Te, _li in results.items():
    teamId = Te.id
    li = copy.deepcopy(_li)  # I protect the original object
    for item in li:
      if item is not None:
        resultobj, oppoobj, matchobj = item
        item[0] = resultobjvalue = resultobj.value
        if oppoobj is not None:
          item[1] = oppoteamId = oppoobj.id
        if matchobj is not None:
          item[2] = matchId = matchobj.id
    # JSON object keys are strings but the encoder converts
    # integers automatically plus the JSON will be sorted.
    d[teamId] = li
  p.parent.mkdir(parents=True, exist_ok=True)  # ensure dir
  with p.open("w") as f:
    json.dump(d, f, indent='\t', sort_keys=True)
  return True




def fumbblapi_cache_schedule_file(tournamentId):
  foldernum = int(tournamentId) // 1000 * 1000
  foldername = f'{foldernum:0>8}'
  filename = f'{tournamentId:0>8}.json'
  return (
      srdatadir() / "fumbblapi_cache" / "schedule"
      / foldername / filename
  )

def delete_fumbblapi_cache_schedule(tournamentId):
  p = fumbblapi_cache_schedule_file(tournamentId)
  if p.is_file():
    p.unlink()  # delete file


def load_fumbblapi_cache_schedule(tournamentId):
  p = fumbblapi_cache_schedule_file(tournamentId)
  if p.is_file():
    with p.open() as f:
      return json.load(f)

def save_fumbblapi_cache_schedule(tournamentId):
  obj = sr.fumbblapi.get__tournament_schedule(
      tournamentId,
      replace_with_fixed=False,
  )
  p = fumbblapi_cache_schedule_file(tournamentId)
  p.parent.mkdir(parents=True, exist_ok=True)  # ensure dir
  with p.open("w") as f:
    json.dump(obj, f, indent='\t', sort_keys=True)
