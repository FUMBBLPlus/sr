__version__ = "0.1.0"

# prioriy modules
from . import settings as _settings
settings = _settings.settings
loginsettings = _settings.loginsettings
from . import data as _data
data = _data.data
from . import helper
from . import time

# standard modules
from . import coach
from . import group
from . import match
from . import report
from . import roster
from . import slot
from . import team
try:
    from . import tournament
except:
    pass
else:
    # second pass modules
    from . import performance

    # pages
    from . import notepages
