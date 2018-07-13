import itertools
import pathlib
import re

import sr
from .. import fumbblapi


@sr.helper.idkey("name", str)
class NotePage(metaclass=sr.helper.InstanceRepeater):

  tags = sr.settings["note.tags"]
  title = None

  def __init__(self, name):
    pass

  @property
  def url(self):
    owner = sr.settings["note.owner"]
    url = f'/note/{owner}/{self.name}'
    return url

  @property
  def id(self):
    return sr.data["note"][self.name]

  @property
  def template(self):
    p0 = pathlib.Path(__file__)
    p1 = p0.parent / "templates" / f'{self.name}.bbcode'
    with p1.open() as f:
      return f.read()


  def content(self, **kwargs):
    return self.template.format(**kwargs)


  @sr.helper.must_logged_in
  def post(self, **content_kwargs):
    content = self.content(**content_kwargs)
    content = content.replace("\n", "\r\n")  # required
    sr.helper.S.note.edit(
        self.id,
        note = content,
        title = self.title,
        tags = self.tags,
        url = self.name,
    )


class FUMBBLYearNotePage(NotePage):

  NAME = None

  @classmethod
  def of_fumbblyear(cls, fumbblyear):
    name = f'SR-{cls.NAME}-Y{fumbblyear}'
    return cls(name)

  @property
  def fumbblyear(self):
    matchobj = re.search(f'SR-{self.NAME}-Y(\\d+)', self.name)
    if matchobj:
      return int(matchobj.group(1))
