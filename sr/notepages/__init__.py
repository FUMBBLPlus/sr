from . import helper

from . import page_barb_gmasters
from . import page_rrr_gmasters
from . import page_sr
from . import page_sr_coach_famous
from . import page_sr_coach_points
from . import page_sr_coach_records
from . import page_sr_report
from . import page_sr_reports
from . import page_sr_team_famous
from . import page_sr_team_records
from . import page_sr_tournaments
from . import page_sr_tournaments_pending
from . import page_xfl_gmasters

page = {
    "BARB-w-GrandMasters": page_barb_gmasters,
    "RRR-GrandMasters": page_rrr_gmasters,
    "SR": page_sr,
    "SR-Coach-Famous": page_sr_coach_famous,
    "SR-Coach-Records": page_sr_coach_records,
    "SR-Coach-Points-name": page_sr_coach_points,
    "SR-Report-n": page_sr_report,
    "SR-Reports-Yn": page_sr_reports,
    "SR-Team-Famous": page_sr_team_famous,
    "SR-Team-Records": page_sr_team_records,
    "SR-Tournaments-Yn": page_sr_tournaments,
    "SR-Tournaments-Pending": page_sr_tournaments_pending,
    "XFL-GrandMasters": page_xfl_gmasters,
}

del page_barb_gmasters
del page_rrr_gmasters
del page_sr
del page_sr_coach_famous
del page_sr_coach_points
del page_sr_coach_records
del page_sr_report
del page_sr_reports
del page_sr_team_famous
del page_sr_team_records
del page_sr_tournaments
del page_sr_tournaments_pending
del page_xfl_gmasters
