import itertools
import math
import pathlib
import re

import sr
from .. import bbcode
from .. import fumbblapi


@sr.helper.idkey("link", str)
class NotePage(metaclass=sr.helper.InstanceRepeater):

  KEY = None

  tags = sr.settings["note.tags"]
  title = None

  def __init__(self, link):
    pass

  @property
  def url(self):
    return noteurl(self.link)

  @property
  def id(self):
    return sr.data["note"].get(self.link, 0)
  @id.setter
  def id(self, value):
    value = int(value)
    sr.data["note"][self.link] = value
    sr._data.save("note")

  @property
  def template(self):
    p0 = pathlib.Path(__file__)
    for name in (self.link, self.KEY):
      p1 = p0.parent / "templates" / f'{name}.bbcode'
      if p1.is_file():
        break
    with p1.open() as f:
      return f.read()


  def bbcurl(self, name=None):
    return bbcnoteurl(self.link, name)


  def content(self, **kwargs):
    return self.template.format(**kwargs)


  @sr.helper.must_logged_in
  def post(self, **content_kwargs):
    content_ = self.content(**content_kwargs)
    content_ = content_.replace("\n", "\r\n")  # required
    note_kwargs = dict(
        note = content_,
        title = self.title,
        tags = self.tags,
        url = self.link,
    )
    if self.id:
      sr.helper.S.note.edit(self.id, **note_kwargs)
    else:
      self.id = sr.helper.S.note.create(**note_kwargs)


class FUMBBLYearNotePage(NotePage):

  NAME = None

  def __init__(self, link):
    self._weekNrs = ...
    super().__init__(link)

  @property
  def datestr(self):
    fromdatestr = self.fromdate.strftime(sr.time.ISO_DATE_FMT)
    todate = self.todate
    if todate is not None:
      todatestr = todate.strftime(sr.time.ISO_DATE_FMT)
      return f'from {fromdatestr} to {todatestr}'
    else:
      return f'from {fromdatestr}'

  @classmethod
  def of_fumbblyear(cls, fumbblyear):
    name = f'SR-{cls.NAME}-Y{fumbblyear}'
    return cls(name)

  @property
  def fromdate(self):
    return sr.time.fumbblyear_firstdate(self.fumbblyear)

  @property
  def fumbblyear(self):
    matchobj = re.search(f'SR-{self.NAME}-Y(\\d+)', self.link)
    if matchobj:
      return int(matchobj.group(1))

  @property
  def reports(self):
    return sorted(
        (sr.report.Report.ofweekNr(w) for w in self.weekNrs),
        reverse = True,
    )

  @property
  def todate(self):
    if self.fumbblyear != sr.time.lastfumbblyear():
      return sr.time.fumbblyear_lastdate(self.fumbblyear)

  @property
  def tournaments(self):
    weekNrs = self.weekNrs
    return sr.tournament.sort(
        (
            t for t in sr.tournament.all()
            if t.main.srenterweekNr in self.weekNrs
        ),
        reverse = True,
    )

  @property
  def weekNrs(self):
    if self._weekNrs is ...:
      weekNrs0 = set(sr.time.fumbblyears()[self.fumbblyear])
      weeknrs1 = set(sr.report.weekNrs())
      weekNrs = weekNrs0 & weeknrs1
      self._weekNrs = weekNrs
    return self._weekNrs



def bbccoach(coach):
  if coach:
    return bbcode.url(coach.http, coach.name)
  else:
    return coach.name

def bbcenterdate(tournament):
  T = tournament
  if not T.ismain:
    return ""
  if T.main.srenterweekNr is not None:
    report = sr.report.Report.ofweekNr(T.main.srenterweekNr)
    datestr = report.date.strftime(sr.time.ISO_DATE_FMT)
    return bbcreport(report, datestr)
  else:
    return ""

def bbcexitdate(tournament):
  T = tournament
  if not T.ismain:
    return ""
  if T.main.srexitweekNr is not None:
    w = T.main.srexitweekNr
    known = True
  else:
    known = False
    if T.main.srtitle:
      w = T.main.srlatestexitweekNr
      fstr = '→ {}'
    else:
      w = T.main.srearliestexitweekNr
      fstr = '{} →'
  if w is None:
    return " "
  reportNr = sr.report.weekNrs().get(w)
  if reportNr:
    assert known
    report = sr.report.Report(reportNr)
    datestr = report.date.strftime(sr.time.ISO_DATE_FMT)
    return bbcreport(report, datestr)
  else:
    dateobj = sr.time.firstdate(w)
    datestr = dateobj.strftime(sr.time.ISO_DATE_FMT)
    if known:
      return datestr
    else:
      return fstr.format(datestr)

def bbcfsgname(tournament):
  if tournament.ismain and tournament.srfsgname:
    return tournament.srfsgname
  return ""

def bbcmove(moveval):
  if moveval == 0:
    return ""
  elif moveval == math.inf:
    return bbcode.size("NEW", 8)
  elif moveval == -math.inf:
    return bbcode.size("OUT", 8)
  elif 0 < moveval:
    return f'↑{bbcode.size(moveval, 8)}'
  elif moveval < 0:
    return f'↓{bbcode.size(abs(moveval), 8)}'

def bbcnoteurl(link, name=None):
  if name is None:
    name = link
  return bbcode.url(noteurl(link), name)

def bbcnteams(tournament):
  if tournament.iselim:
    srnteams = tournament.srnteams
    if srnteams:
      return str(srnteams)
    else:
      return sr.tournament.SRClass.NONE
  return ""

def bbcteam(team):
  if team:
    return bbcode.url(team.http, team.name)
  else:
    return team.name

def bbctournament(
    tournament,
    boldface_titled=True,
    italic_notinyear=True,
):
  T = tournament
  s = bbcode.url(T.http, T.srname)
  if boldface_titled and T.ismain and T.srtitle:
    s = bbcode.b(s)
  if italic_notinyear and T.ismain and T.fumbblyear_in is None:
    s = bbcode.i(s)
  return s

def bbcreport(report, name=None):
  if name is None:
    name = f'{report.nr}'
  return bbcnoteurl(f'SR-Report-{report.nr}', str(name))


def noteurl(link):
  owner = sr.settings["note.owner"]
  return f'/note/{owner}/{link}'
