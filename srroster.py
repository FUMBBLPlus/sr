import srdata


def name(rosterId, weeknr=None):
  li = srdata.data["rostername"][int(rosterId)]
  if weeknr is None:
    return li[-1][2]
  else:
    weeknr = int(weeknr)
  for start_weeknr, stop_weeknr, name in li:
    if weeknr in range(start_weeknr, stop_weeknr):
      return name
  else:
    return name
