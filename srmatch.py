import srtime

def finished_time(match, *, is_dst=None):
  s = match["date"] + ' ' + match["time"]
  return srtime.strptime(s, is_dst=is_dst)
