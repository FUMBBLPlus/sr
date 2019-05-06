import copy
import math
import re

import sr
from .. import bbcode
from . import helper
from . import page_rrr_masters

class _NotePage(page_rrr_masters._NotePage):

  def iter_teamperformances(self):
    bracket = self.link.split("-")[1].upper()
    groupIds = {7922}
    for T in sorted(sr.tournament.added()):
      if T.group.id not in groupIds:
        continue
      if T.status != "completed":
        continue
      name_parts = T.srname.upper().split()
      if name_parts[0] != "BARB":
        continue
      if name_parts[-1] != bracket:
        continue
      for TP in T.teamperformances:
        if not TP.team.roster:
          continue
        yield TP


LO_NotePage = sr.helper.idkey("link", str)(_NotePage)(
    "BARB-LO-Masters"
)  # singleton
MI_NotePage = sr.helper.idkey("link", str)(_NotePage)(
    "BARB-MI-Masters"
)  # singleton
HI_NotePage = sr.helper.idkey("link", str)(_NotePage)(
    "BARB-HI-Masters"
)  # singleton
