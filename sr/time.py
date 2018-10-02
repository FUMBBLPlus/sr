import collections
import datetime
import math

import pytz

import sr


ZONE = "Europe/Stockholm"
UTC = pytz.utc
TZ = pytz.timezone(ZONE)
ISO_DATE_FMT = "%Y-%m-%d"
ISO_TIME_FMT_M = "%H:%M"
ISO_TIME_FMT_S = ISO_TIME_FMT_M + ":%S"
ISO_FMT_F = "%Y-%m-%dT%H:%M:%S.%f"
S_DELIM_ISO_FMT_S = ISO_DATE_FMT + " " + ISO_TIME_FMT_S

ZERODATE = datetime.date(2002, 12, 30)
ZEROTIME = TZ.localize(datetime.datetime(2002, 12, 30, 0, 00))

MICROSECOND = datetime.timedelta(microseconds=1)
ONEDAY = datetime.timedelta(1)
ONEWEEK = datetime.timedelta(7)


def current_fumbblyear():
  return fumbblyear(current_weekNr())

def current_weekNr():
  return weekNr(now())

@sr.helper.default_from_func("weekNr", current_weekNr)
def firstdate(weekNr):
  dt = firsttime(weekNr)
  return datetime.date(dt.year, dt.month, dt.day)


@sr.helper.default_from_func("weekNr", current_weekNr)
def firsttime(weekNr):
  return ZEROTIME + weekNr * ONEWEEK


@sr.helper.default_from_func("weekNr", current_weekNr)
def fumbblyear(weekNr):
  for y, r in fumbblyears().items():
    if weekNr in r:
      return y

@sr.helper.default_from_func("fumbblyear", current_fumbblyear)
def fumbblyear_firstdate(fumbblyear):
  return firstdate(fumbblyears()[fumbblyear][0])


@sr.helper.default_from_func("fumbblyear", current_fumbblyear)
def fumbblyear_lastdate(fumbblyear):
  return lastdate(fumbblyears()[fumbblyear][-1])


_fumbblyears = ...
def fumbblyears(*, rebuild=False):
  global _fumbblyears
  maxyearweeks = sr.settings["time.maxyearweeks"]
  if _fumbblyears is ... or rebuild:
    result = {}
    y = 1
    d = collections.deque(sr.tournament.fumbblcups())
    while d:
      T = d.popleft()
      if y == 1:
        stop_weekNr = 1
      start_weekNr = stop_weekNr
      stop_weekNr = T.srenterweekNr + 1
      assert start_weekNr < stop_weekNr
      if maxyearweeks < stop_weekNr - start_weekNr:
        stop_weekNr = start_weekNr + maxyearweeks
        d.appendleft(T)
      result[y] = range(start_weekNr, stop_weekNr)
      y += 1
    else:
      start_weekNr = stop_weekNr
      stop_weekNr = start_weekNr + maxyearweeks
      result[y] = range(start_weekNr, stop_weekNr)
    _fumbblyears = result
  return _fumbblyears


def fumbblyears_unfinalized():
  w = lowest_enterweekNr_of_unexited()
  return sorted(
      y for y, r in fumbblyears().items()
      if w < r.start or w in r
  )


@sr.helper.default_from_func("weekNr", current_weekNr)
def lastdate(weekNr):
  return  firstdate(weekNr) + ONEWEEK - ONEDAY


def lastfumbblyear():
  return sorted(list(fumbblyears()))[-1]


@sr.helper.default_from_func("weekNr", current_weekNr)
def lasttime(weekNr):
  return  firsttime(weekNr) + ONEWEEK - MICROSECOND


def lowest_enterweekNr_of_unexited():
  weekNrs = set(sr.report.weekNrs())
  return min([
      T.srenterweekNr
      for T in sr.tournament.added()
      if T.ismain
      and T.srenterweekNr
      and (
          T.srexitweekNr is None
          or T.srexitweekNr not in weekNrs
      )
  ])


def now():
  return datetime.datetime.now(TZ)


def strptime(s, fmt=None, *, is_dst=False):
  dt = None
  if fmt is None:
    for fmt in (S_DELIM_ISO_FMT_S, ISO_FMT_F, ISO_DATE_FMT):
      try:
        dt = datetime.datetime.strptime(s, fmt)
      except ValueError:
        pass
      else:
        break
    if dt is None:
      raise ValueError("invalid datetime string")
  else:
    dt = datetime.datetime.strptime(s, fmt)
  if not tz_aware(dt):
    dt = TZ.localize(dt, is_dst=is_dst)
  return dt


def tz_aware(datetimeobj):
  dt = datetimeobj
  if dt.tzinfo is not None:
    if dt.tzinfo.utcoffset(dt) is not None:
      return True
  return False


def weekNr(datetimeobj):
  dt = datetimeobj
  if hasattr(dt, "microsecond"):
    days = (dt - ZEROTIME).days
  else:
    days = (dt - ZERODATE).days
  return math.floor(days / 7)
