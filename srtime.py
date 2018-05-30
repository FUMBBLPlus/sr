import datetime
import math

import pytz

ZONE = 'Europe/Stockholm'
UTC = pytz.utc
TZ = pytz.timezone(ZONE)
ISO_DATE_FMT = '%Y-%m-%d'
ISO_TIME_FMT_S = '%H:%M:%S'
ISO_FMT_F = '%Y-%m-%dT%H:%M:%S.%f'
S_DELIM_ISO_FMT_S = ISO_DATE_FMT + ' ' + ISO_TIME_FMT_S

TURNTIME = datetime.timedelta(seconds=23400)  # 6 hours 30 mins
ZERODATE = datetime.date(2002, 12, 30)
ZEROTIME = UTC.localize(datetime.datetime(2002, 12, 30, 6, 30))

ONEDAY = datetime.timedelta(1)
ONEWEEK = datetime.timedelta(7)


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


def now():
  return datetime.datetime.now(TZ)


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
  dt = ZEROTIME + weeknr * ONEWEEK
  return datetime.date(dt.year, dt.month, dt.day)


def weeknr_lastdate(weeknr):
  return  weeknr_firstday(weeknr) + ONEWEEK - ONEDAY
