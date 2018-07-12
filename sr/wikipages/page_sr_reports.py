import sr
from .. import roman
from . import helper


class WikiPage(helper.FUMBBLYearWikiPage):
  NAME = "SR-Reports-Y__"

  @property
  def name(self):
    return f'SR-Reports-Y{self.fumbblyear}'

  @property
  def title(self):
    return (
        "OBC Sport SR Rankings Reports of FUMBBL Year "
        f'{roman.to_roman(self.fumbblyear)}'
    )

