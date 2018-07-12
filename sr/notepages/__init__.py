from . import helper

from . import page_sr
from . import page_sr_reports
from . import page_sr_tournaments

page = {
    "SR": page_sr,
    "SR-Reports-Y__": page_sr_reports,
    "SR-Tournaments-Y__": page_sr_tournaments,
}

del page_sr
del page_sr_reports
del page_sr_tournaments
