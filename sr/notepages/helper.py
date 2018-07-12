import itertools
import pathlib

import sr
from .. import fumbblapi


@sr.helper.idkey("name", str)
class NotePage(metaclass=sr.helper.InstanceRepeater):

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
  def post(self,
        summary=None,
        minor_edit=True,
        **content_kwargs
    ):
    content = self.content(**content_kwargs)
    sr.helper.S.helppage.edit(
        self.name, content, summary, minor_edit
    )
