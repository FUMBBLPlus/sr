import copy
import math
import re

import sr
from .. import bbcode
from . import helper


class _NotePage(helper._NotePage):

  Result = sr.tournament.Matchup.Result
  flagsortkey = {"": 0, "•": 1, "f": 2, "W": 3}
  _rostershorthands = {
      s: rosterId
      for rosterId, s in sr.data["rostershorthand"].items()
  }
  winresults = {Result.win}
  finalistresults = {
      Result.loss,
      Result.bye,
      Result.conceded,
      Result.fortfeit,
  }
  minwon = 1

  def __init__(self, link):
    super().__init__(link)
    self._rawdata = ...
    self._tooltips = ...

  @property
  def rostershorthands(self):
    return tuple(sorted(
      self._rostershorthands,
      key=lambda s: sr.roster.Roster(
          self._rostershorthands[s]
      ).name,
  ))


  @property
  def minwonstr(self):
    if self.minwon == 1:
      return "1 race"
    else:
      return f'{self.minwon} races'

  @property
  def rawdata(self):
    if self._rawdata is ...:
      self._rawdata = {}
      for TP in self.iter_teamperformances():
        self.update_rawdata(TP)
    return self._rawdata

  def iter_rawtablerows(self):
    rawdata = self.rawdata
    coaches = sorted(
        self.rawdata,
        key=self.rawdatasortkey,
        reverse=True,
    )
    prevnr = None
    prevsortkey = None
    for rownum, coach in enumerate(coaches, 1):
      sortkey = self.rawdatasortkey(coach)
      if sortkey == prevsortkey:
        nr = prevnr
      else:
        nr = rownum
      d = rawdata[coach]
      row = [rownum, sortkey, nr, coach]
      row.extend([
          (tuple(d[sh]) if d[sh] else None)
          for sh in self.rostershorthands
      ])
      yield tuple(row)
      prevnr = nr
      prevsortkey = sortkey

  @property
  def rawtable(self):
    return tuple(self.iter_rawtablerows())

  def iter_teamperformances(self):
    groupId = 2294
    srnteamsrange = range(15, 17)
    for T in sorted(sr.tournament.added()):
      if T.group.id != groupId:
        continue
      if T.status != "completed":
        continue
      if T.srnteams not in srnteamsrange:
        #print(T)
        continue
      for TP in T.teamperformances:
        if not TP.team.roster:
          continue
        yield TP

  def rawdatasortkey(self, coach):
    d = self._rawdata[coach]
    key = {"W": 0, "f": 0, "•": 0, "WTId": 0}
    for flag, T in (v for v in d.values() if v):
        key[flag] += 1
        if flag == "W":
            key["WTId"] = max(key["WTId"], T.id)
    key["WTId"] = -key["WTId"]
    return list(key.values())

  def update_rawdata(self, TP):
    d = self._rawdata
    Result = sr.tournament.Matchup.Result
    T = TP.tournament
    if TP.results[-1][0] in self.winresults:
      flag = "W"
    elif TP.results[-1][0] in self.finalistresults:
      flag = "f"
    elif {r[2] for r in TP.results if r[2]}:  # played
      flag = "•"
    else:
      #print(T, TP, TP.team, TP.results)
      return
    coach = TP.team.coach
    if coach not in d:
      d[coach] = {sh: None for sh in self.rostershorthands}
    sh = sr.data["rostershorthand"][TP.team.roster.id]
    replace = False
    if d[coach][sh] is None:
      replace = True
    else:
      flag0, T0 = d[coach][sh]
      if self.flagsortkey[flag0] < self.flagsortkey[flag]:
        replace = True
      elif flag == flag0:
        # first winner is preferred
        if flag in {"W"} and T.id < T0.id:
          replace = True
        # last non-winner is preferred
        elif flag in {"•", "f"} and T0.id < T.id:
          replace = True
    if replace:
      d[coach][sh] = [flag, T]


  @property
  def tooltips(self):
    if self._tooltips is ...:
      self._tooltips = []
      for sh in self.rostershorthands:
        rosterId = self._rostershorthands[sh]
        roster = sr.roster.Roster(rosterId)
        self._tooltips.append(
            f'[block=tooltip id={sh}]{roster.name}[/block]'
        )
    return self._tooltips

  def table(self, masters=True):
    rostershorthands = self.rostershorthands
    header=[
        "Nr",
        "Coach",
    ]
    for sh in rostershorthands:
      rosterId = self._rostershorthands[sh]
      roster = sr.roster.Roster(rosterId)
      header.append(f'[block tooltip={sh}]{sh}[/block]')
    def rowgen():
      prevNr = None
      for r in self.iter_rawtablerows():
        rownum, sortkey, nr, coach, *vals = r
        Nw = sortkey[0]
        if Nw == len(rostershorthands):
          if not masters:
            continue
        elif masters:
          break
        elif Nw < self.minwon:
          break
        Nr = (str(nr) if nr != prevNr else "")
        Coach = helper.bbccoach(coach)
        row = [Nr, Coach]
        for i, v in enumerate(vals):
          if v is None:
            row.append("")
          else:
            sh = rostershorthands[i]
            flag, T = v
            row.append(
                #f'[block tooltip={sh}]' +
                helper.bbctournament(
                    T,
                    name=flag,
                    boldface_titled=False,
                    italic_notinyear=False,
                    )
                #+ "[/block]"
            )
        yield row
        prevNr = nr
    rows = tuple(rowgen())
    align="CL" + "C" * len(rostershorthands)
    widths = [
        "46px",
        "170px",
    ]
    widths.extend([None] * len(rostershorthands))
    return bbcode.table(
        rows,
        align=align,
        header=header,
        widths=widths,
    )

  def content(self):
    return super().content(
        masterstable = self.table(masters=True),
        minwonstr = self.minwonstr,
        winnerstable = self.table(masters=False),
        tooltips = f'\\{bbcode.N}'.join(self.tooltips),
    )


NotePage = sr.helper.idkey("link", str)(_NotePage)(
    "RRR-GrandMasters"
)  # singleton
