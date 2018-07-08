import itertools
import pathlib

import sr
from .. import fumbblapi



class WikiPage:

  def url(self):
    url = f'https://{fumbblapi.host}/help:{self.name}'
    return url

  @property
  def template(self):
    p0 = pathlib.Path(__file__)
    names = (self.name, self.NAME)
    for name in names:
      p1 = p0.parent / "templates" / name
      if p1.is_file():
        break
    with p1.open() as f:
      return f.read()

  def content(self, **kwargs):
    return self.template.format(**kwargs)


  @sr.helper.must_logged_in
  def post(self,
        summary=None,
        minor_edit=True,
        **content_kwargs
    ):
    content = self.content(**content_kwargs)
    sr.helper.S.helppage.edit(
        self.name, content, summary, minor_edit
    )




def _ftypecast(fumbblyear):
  fumbblyear_ = int(fumbblyear)
  if fumbblyear_ not in sr.time.fumbblyears():
    raise ValueError(f'invalid FUMBBL year: {fumbblyear}')
  return fumbblyear_

@sr.helper.idkey("fumbblyear", _ftypecast)
class FUMBBLYearWikiPage(
    WikiPage,
    metaclass=sr.helper.InstanceRepeater,
):

  def __init__(self, fumbblyear):
    self._weekNrs = ...

  @property
  def reports(self):
    return sorted(
        (sr.report.Report(w) for w in self.weekNrs),
        reverse = True,
    )

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
      self._weekNrs = sr.time.fumbblyears()[self.fumbblyear]
    return self._weekNrs

del _ftypecast




def reporttext(report):
  return f'[#{report.nr}|SR-Report-{report.nr}]'

def tournamentnametext(tournament, boldface_titled=True):
  T = tournament
  text = f'[{T.srname}|{T.http}]'
  if boldface_titled and T.ismain and T.srtitle:
    text = f'__{text}__'
  return text

def tournamentnteamstext(tournament):
  if tournament.iselim:
    return str(tournament.srnteams)
  return " "  # space requires to avoid table cell joins

def tournamentfsgnametext(tournament):
  if tournament.ismain and tournament.srfsgname:
    return tournament.srfsgname
  return " "

def tournamententerdatetext(tournament):
  T = tournament
  if not T.ismain:
    return " "
  if T.main.srenterweekNr is not None:
    report = sr.report.Report(T.main.srenterweekNr)
    datestr = report.date.strftime(sr.time.ISO_DATE_FMT)
    return f'[{datestr}|SR-Report-{report.nr}]'
  else:
    return " "

def tournamentexitdatetext(tournament):
  T = tournament
  if not T.ismain:
    return " "
  if T.main.srexitweekNr is not None:
    w = T.main.srexitweekNr
    known = True
  elif T.main.srlatestexitweekNr is not None:
    w = T.main.srlatestexitweekNr
    known = False
  else:
    return " "
  if w in sr.report.weekNrs():
    assert known
    report = sr.report.Report(w)
    datestr = report.date.strftime(sr.time.ISO_DATE_FMT)
    return f'[{datestr}|SR-Report-{report.nr}]'
  else:
    dateobj = sr.time.firstdate(w)
    datestr = dateobj.strftime(sr.time.ISO_DATE_FMT)
    if known:
      return datestr
    else:
      return f'({datestr})'



def table(rows, align=None, header=None, header_align=None):
  if align is None:
    if rows:
      columns = max(len(row) for row in rows)
      align = 'L' * columns
  if header is not None and header_align is None:
    header_columns = len(header)
    header_align = 'C' * header_columns
  align = ''.join(s.upper() for s in align)
  header_align = ''.join(s.upper() for s in header_align)
  align_trans = {'L': '|<', 'C': '|^', 'R': '|>'}
  align_strs = [align_trans[s] for s in align]
  header_align_strs = [align_trans[s] for s in header_align]
  row_str_gen = (
      ''.join((
          ''.join([str(e) for e in t])
          for t in
          itertools.zip_longest(align_strs, row, fillvalue='')
      ))
      for row in rows
  )
  if header:
    header_str = ''.join((
        ''.join(t)
        for t in
        itertools.zip_longest(
            header_align_strs,
            [f'__{a}__' for a in header],
            fillvalue=''
        )
    ))
    row_str_gen = itertools.chain([header_str], row_str_gen)
  return '\n'.join(row_str_gen)
