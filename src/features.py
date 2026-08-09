"""Feature-engineering architecture for cleaned Garmin running activities.

Implementation convention
-------------------------
Each ``add_*`` function should:

1. accept a cleaned runs DataFrame;
2. make a copy instead of mutating the input;
3. add clearly named feature columns;
4. preserve missing values when required inputs are missing or zero; and
5. return the new DataFrame.

Functions beginning with ``summarize_*`` return a separate aggregate table
rather than adding columns to individual runs.
"""

from __future__ import annotations

import pandas as pd


# ---------------------------------------------------------------------------
# Shared validation helpers
# ---------------------------------------------------------------------------

def require_columns(runs: pd.DataFrame, columns: list[str]) -> None:
    missing_columns = [
        column
        for column in columns
        if column not in runs.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

# ---------------------------------------------------------------------------
# Training volume features
# ---------------------------------------------------------------------------


def add_recovery_spacing_features(runs: pd.DataFrame) -> pd.DataFrame:
    """Add the number of days since the athlete's previous run.

    Planned column:
    - ``days_since_previous_run``

    Required input: ``Date``.

    TODO: Copy the data, sort chronologically, calculate the difference between
    consecutive run datetimes, and decide whether the final value should use
    fractional days or calendar-day boundaries.
    """

    raise NotImplementedError


def add_rolling_distance_features(runs: pd.DataFrame) -> pd.DataFrame:
    """Add recent distance totals using calendar-based rolling windows.

    Planned columns:
    - ``rolling_7_day_distance_km``
    - ``rolling_28_day_distance_km``

    Required inputs: ``Date`` and ``Distance``.

    TODO: Sort by date and use time-based windows. Document whether each window
    includes the current run; the recommended definition includes it.
    """

    raise NotImplementedError


def summarize_weekly_training(runs: pd.DataFrame) -> pd.DataFrame:
    """Return one row per calendar week containing volume aggregates.

    Planned columns:
    - ``weekly_distance_km``
    - ``weekly_running_minutes``
    - ``weekly_run_count``

    Required inputs: ``Date``, ``Distance``, and ``Moving Time``.

    Weekly TSS is excluded because the current export contains only zero TSS
    values and the cleaning pipeline removes that column.
    """

    raise NotImplementedError


# ---------------------------------------------------------------------------
# Intensity features
# ---------------------------------------------------------------------------


def add_duration_features(runs: pd.DataFrame) -> pd.DataFrame:

    require_columns(runs, ["Moving Time", "Elapsed Time"])

    runs_with_features = runs.copy()

    runs_with_features["moving_minutes"] = (
        runs_with_features["Moving Time"].dt.total_seconds() / 60
    )

    runs_with_features["elapsed_minutes"] = (
        runs_with_features["Elapsed Time"].dt.total_seconds() / 60
    )

    return runs_with_features


def add_speed_features(runs: pd.DataFrame) -> pd.DataFrame:
    require_columns(runs, ["Distance", "moving_minutes"])

    runs_with_features = runs.copy()

    valid_time = runs_with_features["moving_minutes"] > 0

    runs_with_features["average_speed_kmh"] = pd.NA

    runs_with_features.loc[valid_time, "average_speed_kmh"] = (
        runs_with_features.loc[valid_time, "Distance"]
        / (
            runs_with_features.loc[valid_time, "moving_minutes"]
            / 60
        )
    )

    runs_with_features["average_speed_kmh"] = pd.to_numeric(
        runs_with_features["average_speed_kmh"]
    )

    return runs_with_features


def add_optional_intensity_features(runs: pd.DataFrame) -> pd.DataFrame:
    """Add intensity features currently marked Later in the plan.

    Potential columns:
    - ``relative_hr_intensity``
    - ``aerobic_effect_per_minute``

    Relative HR intensity also requires an explicitly documented athlete
    maximum heart rate. TSS per minute is excluded for the current export.
    """

    raise NotImplementedError


# ---------------------------------------------------------------------------
# Aerobic-efficiency features
# ---------------------------------------------------------------------------


def add_aerobic_efficiency_features(runs: pd.DataFrame) -> pd.DataFrame:
    """Add transparent cardiovascular-efficiency proxy features.

    Planned MVP columns:
    - ``heart_rate_efficiency_proxy`` = average speed / average HR
    - ``power_to_hr_ratio`` = average power / average HR
    - ``speed_to_power_ratio`` = average speed / average power

    Possible Later column:
    - ``pace_per_watt`` = average pace / average power

    Required inputs depend on the feature. Preserve missing values whenever HR,
    power, speed, or pace is missing or zero. These are project-defined proxies,
    not clinical measurements of running economy.
    """

    raise NotImplementedError


# ---------------------------------------------------------------------------
# Terrain features
# ---------------------------------------------------------------------------


def add_terrain_features(runs: pd.DataFrame) -> pd.DataFrame:
    """Add features describing climbing and stopped time.

    Planned MVP columns:
    - ``climbing_density_m_per_km`` = total ascent / distance
    - ``pause_ratio`` = (elapsed time - moving time) / elapsed time

    Possible Later column:
    - ``ascent_per_hour`` = total ascent / moving time in hours

    Missing treadmill elevation must remain missing rather than becoming zero.
    Rate features must remain missing when their denominator is zero.
    """

    raise NotImplementedError


# ---------------------------------------------------------------------------
# Running-mechanics features (Later)
# ---------------------------------------------------------------------------


def add_running_mechanics_features(runs: pd.DataFrame) -> pd.DataFrame:
    """Add the individual mechanics features marked Later in the plan.

    Potential columns:
    - ``estimated_stride_count``
    - ``vertical_movement_per_step``
    - ``ground_contact_load_proxy``

    Do not create a combined mechanics-efficiency score until the component
    measures have been explored and a defensible method has been selected.
    """

    raise NotImplementedError


# ---------------------------------------------------------------------------
# Time and context features
# ---------------------------------------------------------------------------


def add_calendar_features(runs: pd.DataFrame) -> pd.DataFrame:
    """Add calendar fields derived from the activity date.

    Planned MVP columns:
    - ``month``
    - ``calendar_week``
    - ``calendar_year`` (needed so week numbers remain unambiguous)

    Possible Later column:
    - ``day_of_week``
    """

    raise NotImplementedError


def add_activity_title_features(runs: pd.DataFrame) -> pd.DataFrame:
    """Create initial workout labels from activity-title keywords.

    Candidate keywords from the plan include easy, tempo, interval, race, and
    long. Inspect real titles and document precedence rules before implementing
    the labels; do not silently treat unmatched titles as a known workout type.
    """

    raise NotImplementedError


def add_distance_category(runs: pd.DataFrame) -> pd.DataFrame:
    """Assign the Later-stage short, medium, and long distance categories.

    Distance thresholds require an explicit athlete- and project-level decision
    before this function is implemented.
    """

    raise NotImplementedError


# ---------------------------------------------------------------------------
# MVP orchestration
# ---------------------------------------------------------------------------


def add_mvp_run_features(runs: pd.DataFrame) -> pd.DataFrame:
    """Apply implemented MVP per-run feature functions in dependency order.

    Intended order:
    1. duration;
    2. speed;
    3. terrain;
    4. calendar;
    5. recovery spacing;
    6. rolling distance;
    7. aerobic efficiency; and
    8. activity-title features.

    Weekly summaries are intentionally separate because they return one row per
    week rather than one row per activity.
    """

    raise NotImplementedError


# ---------------------------------------------------------------------------
# Comparison analyses belong in src/analysis.py
# ---------------------------------------------------------------------------

# The pace-heart-rate trend, aerobic-efficiency trend, and comparable-run score
# compare multiple activities. They are analyses rather than raw per-run feature
# transformations, so their reusable functions should live in ``analysis.py``
# after the underlying features above have been implemented and validated.
