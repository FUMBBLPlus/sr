#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import functools
import pathlib
import re
import sys

import sr


inpcodes = None


def enter_info(T):
  enterweekNr = T.srenterweekNr
  if enterweekNr:
    date = sr.time.firstdate(enterweekNr)
    return f'{date} [{enterweekNr}]'
  else:
    return 'unknown'


def exit_info(T):
  exitweekNr = T.srlatestexitweekNr
  if exitweekNr:
    islatest = (exitweekNr == T.srexitweekNr)
    date = sr.time.firstdate(exitweekNr)
    if islatest:
      return f'{date} [{exitweekNr}]'
    else:
      return f'({date}) [{exitweekNr}]'
  else:
    return 'unknown'


def inpcode_removing(impcode):
  def real_decorator(func):
    @functools.wraps(func)
    def wrapper(T):
      inpcodes.remove(impcode)
      result = func(T)
      return result
    return wrapper
  return real_decorator


@inpcode_removing(1000)
def input_srname(T):
  print('SR Standard Tournament Name?')
  print(
      '  list<n>: '
      'lists the previous <n> tournaments of the same group'
      ' (n: integer; default=5)'
  )
  print(f'  <Enter>: unchange ("{T.srname}")')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I.startswith("LIST"):
      n = I[4:]
      if not n:
        n = 5
      elif n.isdecimal():
        n = int(n)
      else:
        continue
      tournaments = sorted(
          {T2 for T2 in T.group.tournaments if T2.id < T.id}
      )[-n:]
      for T2 in tournaments:
        print_tournament_short(T2)
      continue
    elif I != "":
      T.srname = I
      break


@inpcode_removing(2000)
def input_main(T):
  print('Main Tournament ID?')
  print('  ?: unknown')
  print('  0: this')
  print(f'  <Enter>: unchange ({T.maintournamentId})')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in ("?", "UNKNOWN", "<UNKNOWN>"):
      I = None
    elif I in ("0", "THIS", "<THIS>"):
      I = 0
    elif I.isdecimal():
      I = int(I)
    elif I:
      continue
    if I != "":
      T.maintournamentId = I
    break


@inpcode_removing(2910)
def input_formatchar(T):
  print('Format Character?')
  print('  ?: unknown')
  print('  E: elimination')
  print('  N: non-elimination')
  print(f'  <Enter>: unchange ({T.srformatchar})')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in ("?", "UNKNOWN", "<UNKNOWN>"):
      I = None
    elif I in ("E", "ELIMINATION"):
      I = "E"
    elif I in ("N", "NON-ELIMINATION"):
      I = "N"
    elif I:
      continue
    if I != "":
      T.srformatchar = I
    break


@inpcode_removing(2920)
def input_rank(T):
  print('Rank?')
  print('  ?: unknown')
  print('  MI: minor')
  print('  MA: major')
  print('  QU: major qualifier')
  print(f'  <Enter>: unchange ({T.rank})')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in ("?", "UNKNOWN", "<UNKNOWN>"):
      I = None
    elif I in ("MI", "MINOR"):
      I = "MI"
    elif I in ("MA", "MAJOR"):
      I = "MA"
    elif I in ("QU", "MAJOR QUALIFIER", "QUALIFIER"):
      I = "QU"
    elif I:
      continue
    if I != "":
      T.rank = I
    break


@inpcode_removing(2930)
def input_level(T):
  if T.rank is None:
    inpcodes.add(2920)
    return
  print('Level?')
  print('  ?: unknown')
  print('  <n>: level <n> (n: integer)')
  print(f'  <Enter>: unchange ({T.level})')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in ("?", "UNKNOWN", "<UNKNOWN>"):
      I = None
    elif I.isdecimal():
      I = int(I)
    elif I:
      continue
    if I != "":
      level, prev_level = I, T.level
      if prev_level is None:
        prev_level = 1
      T.level = level
      if T.rank in ("MA", "MI") and level < prev_level:
        for T2 in set(T.qualifiers):
          if T2.level is not None and T.level <= T2.level:
            T2.main = None
            print((
              'Main tournament of'
              f' {T2.srname} ({T2.id})'
              ' is now unknown.'
            ))
      elif T.rank in ("MA", "MI") and prev_level < level:
        inpcodes.add(2931)
      elif T.rank in ("QU") and prev_level < level:
        if T.main and main.level is not None:
          if main.level <= level:
            T.main = None
        if not T.main:
          print('Main tournament is now unknown.')
    break


@inpcode_removing(2931)
def input_qualifiers(T):
  print((
      'Please decide whether the following tounaments are '
      'qualifiers of this one (Y/N)?'
  ))
  for T2 in sr.tournament.main_unknown():
    if T2.level and T.level <= T2.level:
      continue
    if sr.helper.YesNoInput(f'{T2.srname} ({T2.id}))')():
      T2.main = T
      if T2.level is None and T.level == 2:
        T2.level = 1


@inpcode_removing(2940)
def input_srnteams(T):
  print('Teams (number of non-filler teams in round 1)?')
  print('  ?: unknown')
  print('  <n>: number of teams (n: integer)')
  print(f'  <Enter>: unchange ({T.srnteams})')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in ("?", "UNKNOWN", "<UNKNOWN>"):
      I = None
    elif I.isdecimal():
      I = int(I)
    elif I:
      continue
    if I != "":
      T.srnteams = I
    break


@inpcode_removing(3000)
def input_srclass(T):
  print('Which class item you wan to change?')
  accepted = {"", "1", "2", "3"}
  print('  1: formatchar')
  print('  2: rank')
  print('  3: level')
  if T.iselim:
    print('  4: teams')
    accepted.add("4")
  print('  <Enter>: none')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I not in accepted:
      continue
    if I != "":
      inpcodes.add(2900 + 10 * int(I))
      inpcodes.add(3000)
    break


@inpcode_removing(4000)
def input_srtitle(T):
  print('Title?')
  print('  -: none')
  print('  ?: unknown')
  print('  list: lists existing titles')
  print(f'  <Enter>: unchanged ("{T.srtitle}")')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in (
        "", "ENTER", "<ENTER>", "UNCHANGED", "<UNCHANGED>"
    ):
      break
    elif I in ("LIST", "<LIST>"):
      print("; ".join(sorted(sr.tournament.srtitles())))
      continue
    elif I in ("-", "NONE", "<NONE>"):
      I = ""
    elif I in ("?", "UNKNOWN", "<UNKNOWN>"):
      I = None
    else:
      if I not in sr.tournament.srtitles():
        text = 'Are you sure to add a new title? (Y/N)'
        if not sr.helper.YesNoInput(text)():
          continue
    T.srtitle = I
    if T.srtitle and T.srenterweekNr is not None:
      tournaments = {
          T2 for T2 in sr.tournament.added()
          if T2.ismain
          and T2.srtitle == T.srtitle
          and T2.srexitweekNr is None
          and T2 is not T
      }
      if tounaments:
        print(
            "Please review unfinalized tournaments "
            "with same title!"
        )
        edit_tournaments(tournaments)
    break


@inpcode_removing(5000)
def input_srfsgname(T):
  print('First Slot Group?')
  print('  ?: unknown')
  print('  FC: FUMBBL Cup')
  print('  MA: major')
  print('  R: regular')
  print('  NE: not eligible')
  print(f'  <Enter>: unchanged ("{T.srfsgname}")')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in (
        "", "ENTER", "<ENTER>", "UNCHANGED", "<UNCHANGED>"
    ):
      break
    elif I in ("?", "UNKNOWN", "<UNKNOWN>"):
      I = None
    elif I in ("FC", "FUMBBLCUP", "FUMBBL CUP"):
      I = "FC"
    elif I in ("MA", "MAJOR"):
      I = "MA"
    elif I in ("R", "REGULAR"):
      I = "R"
    elif I in ("NE", "NOTELIGIBLE", "NOT ELIGIBLE"):
      I = "NE"
    else:
      continue
    T.srfsgname = I
    break


@inpcode_removing(6000)
def input_srenter(T):
  print('Enter weekNr (integer) or date (YYYY-MM-DD)?')
  print('  ?: unknown')
  print(f'  <Enter>: unchanged ({enter_info(T)})')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in (
        "", "ENTER", "<ENTER>", "UNCHANGED", "<UNCHANGED>"
    ):
      break
    elif I in ("?", "UNKNOWN", "<UNKNOWN>"):
      I = None
    elif I.isdecimal():
      I = int(I)
    else:
      try:
        dt = sr.time.strptime(I)
      except ValueError:
        continue
      else:
        dt = datetime.date(dt.year, dt.month, dt.day)
        I = sr.time.weekNr(dt)
    T.srenterweekNr = I
    break


@inpcode_removing(7000)
def input_srexit(T):
  print('Exit weekNr (integer) or date (YYYY-MM-DD)?')
  print('  ?: unknown')
  print(f'  <Enter>: unchanged ({exit_info(T)})')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in (
        "", "ENTER", "<ENTER>", "UNCHANGED", "<UNCHANGED>"
    ):
      break
    elif I in ("?", "UNKNOWN", "<UNKNOWN>"):
      I = None
    elif I.isdecimal():
      I = int(I)
    else:
      try:
        dt = sr.time.strptime(I)
      except ValueError:
        continue
      else:
        dt = datetime.date(dt.year, dt.month, dt.day)
        I = sr.time.weekNr(dt)
    T.srexitweekNr = I
    break


@inpcode_removing(88888888)
def input_tournamentdone(T):
  print('What to set now?')
  print('  1: name')
  print('  2: main tournament ID')
  print('  3: class')
  print('  4: title')
  print('  5: first slot group name')
  print('  6: enter date [weekNr]')
  print('  7: exit date [weekNr]')
  print('  i: info')
  print('  <Enter>: done')
  sys.stdout.flush()
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in ("", "ENTER", "<ENTER>", "DONE", "<DONE>"):
      break
    elif I in ("1", "NAME"):
      I = 1
    elif I in (
        "2", "MAIN", "MAINTOURNAMENT", "MAIN TOURNAMENT",
        "MAINTOURNAMENTID", "MAIN TOURNAMENT ID",
    ):
      I = 2
    elif I in ("3", "CLASS"):
      I = 3
    elif I in ("4", "TITLE"):
      I = 4
    elif I in (
        "5", "FSG", "FSGNAME", "FIRSTSLOTGROUP",
        "FIRST SLOT GROUP", "FIRSTSLOTGROUPNAME",
        "FIRST SLOT GROUP NAME",
    ):
      I = 5
    elif I in (
        "6", "ENTER", "ENTERWEEKNR", "ENTER WEEKNR",
        "ENTERDATE", "ENTER DATE",
    ):
      I = 6
    elif I in (
        "7", "EXIT", "EXITWEEKNR", "EXIT WEEKNR", "EXITDATE",
        "EXIT DATE",
    ):
      I = 7
    elif I in ("I", "INFO"):
      print()
      print_tournament(T)
      inpcodes.add(88888888)
      break
    else:
      continue
    inpcodes.add(1000 * I)
    inpcodes.add(88888888)
    break


def print_tournament(T):
  print(f'name: {T.srname}')
  print(f'groupId: {T.group.id}')
  print(f'tournamentId: {T.id}')
  if T.ismain:
    mainstr = "this"
  elif T.main:
    mainstr = T.main.srname
  else:
    mainstr = "unknown"
  print(f'main tournament: {mainstr}')
  print(f'class: {T.srclassval}')
  if T.ismain:
    if T.srtitle:
        print(f'title: {T.srtitle}')
    else:
        print('title: none')
    print(f'first slot group: {T.srfsgname}')
    print(f'enter: {enter_info(T)}')
    print(f'exit: {exit_info(T)}')


def print_tournament_short(T, indent=0):
  print("" * indent + f'[{T.id}] {T.srname}')


def tournament_inpcodes(T):
  result = {88888888}
  if T.srname != T.srdatasrname:
    result.add(1000)
  if T.rank is None:
    result.add(2920)
  if T.level is None:
    result.add(2930)
  elif 1 < T.level and T.srisnew:
    result.add(2931)
  return result


def save():
  print("Saving tournaments...")
  for T in sorted(sr.tournament.changed()):
    print_tournament_short(T, indent=2)
    T.srnewdata_apply()
    T.schedule.save_results()
  print("Saving Tournament data...")
  sr._data.save("tournament")
  print("Saving coach data...")
  sr.coach.save()
  print("Saving team data...")
  sr.team.save()
  print("Saving DONE.")


def edit_searched_tournaments():
  print("Search by:")
  print("  1: name (regular expression)")
  print("  2: groupId")
  print("  3: tournamentId")
  print("  E: exit")
  while True:
    I = input(sr.helper.Input.prompt).strip().upper()
    if I in ("1", "NAME"):
      name_pattern = sr.helper.Input("Name")()
      tournaments = {
          T for T in sr.tournament.all_()
          if re.match(name_pattern, T.srname)
      }
      edit_tournaments(tournaments)
    elif I in ("2", "GROUP", "GROUPID", "GROUP ID"):
      group = sr.group.Group(
          sr.helper.IntegerInput("groupId")()
      )
      edit_tournaments(group.tournaments)
    elif I in (
        "3", "TOURNAMENT", "TOURNAMENTID", "TOURNAMENT ID"
    ):
      tournamentId = sr.helper.IntegerInput("tournamentId")()
      tournament = sr.tournament.Tournament(tournamentId)
      edit_tournaments([tournament])
    elif I not in ("E", "EXIT"):
      continue
    break


def edit_tournaments(tournaments=None):
  global inpcodes
  if tournaments is None:
    print('Please wait...')
    tournaments = sr.tournament.changed()
  for T in sorted(tournaments):
    print()
    print("-" * 79)
    print()
    print_tournament(T)
    sys.stdout.flush()
    inpcodes = tournament_inpcodes(T)
    while inpcodes:
      i = min(inpcodes)
      if i == 1000:
        input_srname(T)
      elif i == 2000:
        input_main(T)
      elif i == 2910:
        input_formatchar(T)
      elif i == 2920:
        input_rank(T)
      elif i == 2930:
        input_level(T)
      elif i == 2931:
        input_qualifiers(T)
      elif i == 2940:
        input_srnteams(T)
      elif i == 3000:
        input_srclass(T)
      elif i == 4000:
        input_srtitle(T)
      elif i == 5000:
        input_srfsgname(T)
      elif i == 6000:
        input_srenter(T)
      elif i == 7000:
        input_srexit(T)
      elif i == 88888888:
        input_tournamentdone(T)


def year_end_exit_weeknumber():
  fc = sr.tournament.fumbblcups()[-1]
  weekNr = fc.srenterweekNr
  tournaments0 = sr.tournament.offumbblyear(fc.fumbblyear)
  tournaments = sorted(
      T for T in tournaments0
      if T.ismain
      and not T.srtitle
      and T.srexitweekNr is None
  )
  for T in tournaments:
    srexitweekNr = max(weekNr, T.srenterweekNr + 52)
    T.srexitweekNr = srexitweekNr
  print(", ".join(str(T) for T in tournaments))


def main():
  while True:
    print(f'Tournaments: {len(sr.tournament.added())}')
    print("Options:")
    print("  1: edit/review changed tournaments")
    print("  2: edit searched tournaments")
    print("  3: year end exit weeknumber set")
    print("  S: save and quit")
    print("  Q: quit without saving")
    while True:
      I = input(sr.helper.Input.prompt).strip().upper()
      if I in ("1", "EDIT", "EDIT CHANGED", "CHANGED"):
        edit_tournaments()
        print()
        print("=" * 79)
        print()
        break
      elif I in ("2", "EDIT SEARCHED", "SEARCH"):
        edit_searched_tournaments()
        print()
        print("=" * 79)
        print()
        break
      elif I in ("3", "YEAR END", "EXIT"):
        year_end_exit_weeknumber()
        print()
        print("=" * 79)
        print()
        break
      elif I in ("S", "SAVE"):
        save()
        return
      elif I in ("Q", "QUIT"):
        return

if __name__ == "__main__":
  usage = "usage: sr_update_tournaments.py"
  if len(sys.argv) > 1:
      print(usage)
      sys.exit()
  try:
    main()
  except KeyboardInterrupt:
    pass
