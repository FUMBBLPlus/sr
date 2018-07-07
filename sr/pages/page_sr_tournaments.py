import sr
from .. import roman
from . import helper


class WikiPage(helper.FUMBBLYearWikiPage):
  NAME = "SR-Tournaments-Y__"

  @property
  def name(self):
    return f'SR-Tournaments-Y{self.fumbblyear}'

  @property
  def title(self):
    return (
        "OBC Sport SR Rankings Tournaments of FUMBBL Year "
        f'{roman.to_roman(self.fumbblyear)}'
    )
