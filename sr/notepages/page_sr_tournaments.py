import sr
from .. import roman
from . import helper


class NotePage(helper.NotePage):

  @classmethod
  def of_fumbblyear(cls, fumbblyear):
    name = f'SR-Tournaments-Y{fumbblyear}'
    return cls(name)
