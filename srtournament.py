import srdata


def format_(old_group_tournaments, tournamentId):
  for t in old_group_tournaments.iter('tournament'):
    if int(t.attrib["id"]) == tournamentId:
      return t.find('type').text


def prevnext_title(tournament):
  TI = srdata.TournamentIdx
  result = [None, None]
  title = None
  if TI.TITLE < len(tournament):
    title = tournament[TI.TITLE]
  if title:
    i = 0
    for t in srdata.data["tournaments"]:
      if len(t) <= TI.TITLE:
          continue
      if t[TI.TITLE] != title:
          continue
      if t[TI.ID] < tournament[TI.ID]:
        result[0] = t
      elif tournament[TI.ID] < t[TI.ID]:
        result[1] = t
        break
  return result


def weeknr_tournaments(weeknr):
  TI = srdata.TournamentIdx
  for row in srdata.data["tournaments"]:
    if row[TI.TOP_ID]:
      toprow = srdata.data["tournament"][row[TI.TOP_ID]]
    elif row[TI.TOP_ID] is not None:
      toprow = row
    else:
      continue
    if len(toprow) <= TI.EXIT_WEEKNR:
      continue
    enter_weeknr = toprow[TI.ENTER_WEEKNR]
    exit_weeknr = toprow[TI.EXIT_WEEKNR]
    if enter_weeknr is None or exit_weeknr is None:
      continue
    if weeknr in range(enter_weeknr, exit_weeknr):
      yield row
