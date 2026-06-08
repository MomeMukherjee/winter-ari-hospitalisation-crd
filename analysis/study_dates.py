# =================================================================
# study_dates.py
# Central date definitions for winter ARI study
# All dates as strings ~ ehrQL parses them automatically
#
# DESIGN:
# Each season = one annual extract
# Season defined by WINTER YEAR (year in which winter ends)
# e.g. season_year=2018 covers winter 2017/18
#
# For each season:
#   - Registration lookback start: 1 April of previous year
#     (ensures CRD diagnoses before winter are captured)
#   - Registration requirement: registered >= 12 months
#     before season start
#   - CRD lookback: from 1 April of previous year
#     (not just at season start)
#   - Outcome window: FULL YEAR extract (1 Apr to 31 Mar)
#     Winter spike is identified analytically in R
#     NOT predefined here ~ data-driven threshold approach
#   - Death/alive: must be alive at season start
#
# COVID period flags (assigned in R from admission dates):
#   Pre-COVID:   seasons 2017, 2018, 2019, 2020 (Sep 2016 ~ Feb 2020)
#   COVID:       seasons 2021, 2022 (Mar 2020 ~ Mar 2022)
#   Post-COVID:  seasons 2023, 2024, 2025 (Apr 2022 ~ latest)
# =================================================================

def get_season_dates(season_year: int) -> dict:
    """
    Returns all date strings for a given winter season.
    season_year is the calendar year in which the winter ENDS.
    e.g. season_year=2018 = winter 2017/18

    Earliest valid season_year = 2017
    (needs Apr 2016 lookback ~ study data from Sep 2016)
    """
    prev_year = season_year - 1

    return {
        # Full extract window ~ full respiratory year
        # Apr 1 of prev year to Mar 31 of season year
        "extract_start":    f"{prev_year}-04-01",
        "extract_end":      f"{season_year}-03-31",

        # Registration requirement
        # Must be registered 12 months before extract start
        "reg_lookback":     f"{season_year - 2}-04-01",

        # CRD lookback ~ diagnoses from Apr 1 of prev year
        # (or study start for first season)
        "crd_lookback":     f"{prev_year}-04-01",

        # Season start ~ used for age, alive check
        "season_start":     f"{prev_year}-10-01",

        # Study-wide start ~ for first season only
        "study_start":      "2016-09-01",

        # COVID period boundaries
        "pre_covid_end":    "2020-02-29",
        "covid_start":      "2020-03-01",
        "covid_end":        "2022-03-31",
        "post_covid_start": "2022-04-01",

        # Season label
        "season_label":     f"{prev_year}-{str(season_year)[-2:]}",
        "season_year":      season_year,
    }


# All seasons in the study
ALL_SEASONS = list(range(2017, 2026))
# 2017 = winter 2016/17 (first full winter after Sep 2016 start)
# 2025 = winter 2024/25 (latest available ~ update as data arrives)
