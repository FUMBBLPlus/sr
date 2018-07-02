import datetime
import math

import pytz

import sr


ZONE = 'Europe/Stockholm'
UTC = pytz.utc
TZ = pytz.timezone(ZONE)
ISO_DATE_FMT = '%Y-%m-%d'
ISO_TIME_FMT_S = '%H:%M:%S'
ISO_FMT_F = '%Y-%m-%dT%H:%M:%S.%f'
S_DELIM_ISO_FMT_S = ISO_DATE_FMT + ' ' + ISO_TIME_FMT_S

ZERODATE = datetime.date(2002, 12, 30)
ZEROTIME = TZ.localize(datetime.datetime(2002, 12, 30, 8, 00))

MICROSECOND = datetime.timedelta(microseconds=1)
ONEDAY = datetime.timedelta(1)
ONEWEEK = datetime.timedelta(7)


def current_weeknr():
  return weeknr(now())


_fumbblyears = ...
def fumbblyears(*, rebuild=False):
  global _fumbblyears
  if _fumbblyears is ... or rebuild:
    result = {}
    for y, T in enumerate(sr.tournament.fumbblcups(), 2):
      start_weeknr = T.srenterweeknr + 1
      stop_weeknr = T.srlatestexitweeknr + 1
      if y == 2:
        result[y - 1] = range(0, start_weeknr)
      result[y] = range(start_weeknr, stop_weeknr)
    else:
      result[y] = range(start_weeknr, 999999999)
    _fumbblyears = result
  return _fumbblyears


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
      raise ValueError('invalid datetime string')
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


def weeknr(datetimeobj):
  dt = datetimeobj
  if hasattr(dt, 'microsecond'):
    days = (dt - ZEROTIME).days
  else:
    days = (dt - ZERODATE).days
  return math.floor(days / 7)


@sr.helper.default_from_func("weeknr", current_weeknr)
def firstdate(weeknr):
  dt = firsttime(weeknr)
  return datetime.date(dt.year, dt.month, dt.day)


@sr.helper.default_from_func("weeknr", current_weeknr)
def firsttime(weeknr):
  return ZEROTIME + weeknr * ONEWEEK


@sr.helper.default_from_func("weeknr", current_weeknr)
def fumbblyear(weeknr):
  for y, r in fumbblyears().items():
    if weeknr in r:
      return y


@sr.helper.default_from_func("weeknr", current_weeknr)
def lastdate(weeknr):
  return  firstdate(weeknr) + ONEWEEK - ONEDAY


@sr.helper.default_from_func("weeknr", current_weeknr)
def lasttime(weeknr):
  return  firsttime(weeknr) + ONEWEEK - MICROSECOND
