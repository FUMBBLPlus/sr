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
    p1 = p0.parent / "templates" / self.name
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
