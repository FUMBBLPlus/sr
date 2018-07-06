import pathlib

from .. import fumbblapi

try:
  import fumbbl_session as S
except ImportError:
  S = None

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
