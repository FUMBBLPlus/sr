import json
import pathlib


class Settings:

  PREFIX = "sr"

  files = (
      pathlib.Path.home() / ".fumbblplus/srsettings.json",
      pathlib.Path(__file__).parent / "srsettings.default.json"
  )

  def __init__(self):
    self._settings = {p: dict() for p in self.files}
    for p in self.files:
      if p.is_file():
        with p.open(encoding="utf8") as f:
          self._settings[p] = json.load(f)

  def __getitem__(self, key):
    exc = None
    for p in self.files:
      try:
        return self._settings[p][f'{self.PREFIX}.{key}']
      except KeyError as exc_:
        exc = exc_

  def __setitem__(self, key, value):
    p = self.files[0]
    self._settings[p][f'{self.PREFIX}.{key}'] = value
    p.parent.mkdir(parents=True, exist_ok=True)  # ensure dir
    with p.open("w", encoding="utf8") as f:
      json.dump(
          self._settings[p],
          f,
          indent="\t",
          ensure_ascii=False,
          sort_keys=True,
      )

settings = Settings()  # singleton
