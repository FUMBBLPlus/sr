import re

import sr
from .. import roman
from . import helper


class NotePage(helper.NotePage):

  @classmethod
  def of_fumbblyear(cls, fumbblyear):
    name = f'SR-Reports-Y{fumbblyear}'
    return cls(name)

  @property
  def fumbblyear(self):
    matchobj = re.search(r'SR-Reports-Y(\d+)', self.name)
    if matchobj:
      return int(matchobj.group(1))

