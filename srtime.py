import datetime
import math

import pytz

import srdata


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


fumbblyears = None


def current_weeknr():
  return weeknr(now())


def now():
  return datetime.datetime.now(TZ)


def regen_fumbblyears():
  global fumbblyears
  result = {}
  TI = srdata.TournamentIdx
  gen = (
      row for row in srdata.data["tournaments"]
      if TI.FIRST_SLOT_GROUP < len(row)
      and row[TI.FIRST_SLOT_GROUP] == 'FC'
  )
  for y, row in enumerate(gen, 2):
    if y == 2:
      result[y - 1] = range(0, row[TI.ENTER_WEEKNR] + 1)
    start_weeknr = row[TI.ENTER_WEEKNR] + 1
    stop_weeknr = row[TI.EXIT_WEEKNR] + 1
    result[y] = range(start_weeknr, stop_weeknr)
  else:
    result[y] = range(start_weeknr, 999999999)
  fumbblyears = result


def report_date(datetimeobj):
  return weeknr_firstdate(report_weeknr(datetimeobj))


def report_weeknr(datetimeobj):
  return weeknr(datetimeobj) + 1


def report_weeknrs():
  TI = srdata.TournamentIdx
  r = set()
  for row in srdata.data['tournaments']:
    if row[TI.TOP_ID] == 0 and row[TI.WINNER_ID]:
      r.add(row[TI.ENTER_WEEKNR])
      r.add(row[TI.EXIT_WEEKNR])
  return sorted({w for w in r if w <= current_weeknr() + 1})


def strptime(s, fmt=None, *, is_dst=None):
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


def weeknr_firstdate(weeknr):
  dt = weeknr_turntime(weeknr)
  return datetime.date(dt.year, dt.month, dt.day)


def weeknr_firsttime(weeknr):
  return ZEROTIME + weeknr * ONEWEEK


def weeknr_fumbblyear(weeknr):
  for y, r in fumbblyears.items():
    if weeknr in r:
      return y


def weeknr_lastdate(weeknr):
  return  weeknr_firstdate(weeknr) + ONEWEEK - ONEDAY


weeknr_turntime = weeknr_firsttime


def weeknr_lasttime(weeknr):
  return  weeknr_firsttime(weeknr) + ONEWEEK - MICROSECOND
