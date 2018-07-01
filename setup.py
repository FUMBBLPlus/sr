"""
FUMBBL SR Rankings module and scripts
"""

import pathlib
import re

from setuptools import setup, find_packages


thisdir = pathlib.Path(__file__).parent
srdir = thisdir / "sr"


with (thisdir / "README.md").open(encoding="utf8") as f:
  readme = f.read()


metadata_pobj = re.compile(r"__([a-z]+)__ = \"([^\"]+)")
with (srdir / "__init__.py").open(encoding="utf8") as f:
  initpy = f.read()
metadata = dict(metadata_pobj.findall(initpy))


setup(
  name = "sr",
  version = metadata["version"],
  description = "FUMBBL SR Rankings",
  long_description = readme,
  url = "https://github.com/FUMBBLPlus/sr",
  author = "Szieberth Ádám",
  author_email = "sziebadam@gmail.com",
  license = "MIT",
  classifiers = [
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "Topic :: Games/Entertainment :: Board Games"
      "License :: OSI Approved :: MIT License",
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.6",
  ],
  keywords = [
      "game",
      "fantasyfootball",
      "fumbbl",
  ],
  packages = find_packages(exclude=["test*"]),
  package_dir = {
      "sr": "./sr",
  },
  include_package_data = True,
  package_data={'': ['sr/*.json']},
  install_requires = [
      "pytz",
  ],
  extras_require = {
  },
  scripts = [
      "scripts/set_srdatadir.py",
      "scripts/update_tournaments.py",
  ],
  )
