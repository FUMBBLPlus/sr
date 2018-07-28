from . import helper

from . import page_sr
from . import page_sr_report
from . import page_sr_reports
from . import page_sr_tournaments
from . import page_sr_tournaments_pending

page = {
    "SR": page_sr,
    "SR-Report-n": page_sr_report,
    "SR-Reports-Yn": page_sr_reports,
    "SR-Tournaments-Yn": page_sr_tournaments,
    "SR-Tournaments-Pending": page_sr_tournaments_pending,
}

del page_sr
del page_sr_report
del page_sr_reports
del page_sr_tournaments
del page_sr_tournaments_pending
