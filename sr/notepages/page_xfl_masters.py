import copy
import math
import re

import sr
from .. import bbcode
from . import helper
from . import page_rrr_masters

class _NotePage(page_rrr_masters._NotePage):

  def iter_teamperformances(self):
    groupIds = 2410, 10407
    for T in sorted(sr.tournament.added()):
      if T.group.id not in groupIds:
        continue
      if T.status != "completed":
        continue
      if "master" in T.srname.lower():
        continue
      winner_sh = sr.data["rostershorthand"][T.winner.roster.id]
      for TP in T.teamperformances:
        if not TP.team.roster:
          continue
        sh = sr.data["rostershorthand"][TP.team.roster.id]
        # In some rare cases a different race may get into an
        # other race's XFL.
        # examples:
        # XFL V WOOD ELF / Cheech n Chongs Elf Dreams
        # XFL VI GOBLIN / Doomy Diggers
        if sh != winner_sh:
          #print(T, TP.team)
          continue
        yield TP


NotePage = sr.helper.idkey("link", str)(_NotePage)(
    "XFL-Masters"
)  # singleton
