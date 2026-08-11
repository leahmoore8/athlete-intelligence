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


def add_recovery_spacing_features(
    runs: pd.DataFrame,
) -> pd.DataFrame:
    require_columns(
        runs,
        ["Date"],
    )

    runs_with_features = (
        runs.copy()
        .sort_values("Date")
        .reset_index(drop=True)
    )

    activity_date = (
        runs_with_features["Date"].dt.normalize()
    )

    runs_with_features["days_since_previous_run"] = (
        activity_date
        .diff()
        .dt.days
        .astype("Int64")
    )

    return runs_with_features


def add_rolling_distance_features(runs: pd.DataFrame) -> pd.DataFrame:
    require_columns(runs, ["Date", "Distance"])

    runs_with_features = (
        runs.copy()
        .sort_values("Date")
        .reset_index(drop=True)
    )

    runs_with_features["rolling_7_day_distance_km"] = (
        runs_with_features
        .rolling(
            window="7D",
            on="Date",
            min_periods=1,
        )["Distance"]
        .sum()
    )

    runs_with_features["rolling_28_day_distance_km"] = (
        runs_with_features
        .rolling(
            window="28D",
            on="Date",
            min_periods=1,
        )["Distance"]
        .sum()
    )

    return runs_with_features


def summarize_weekly_training(runs: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        runs,
        [
            "Date",
            "Distance",
            "Moving Time",
            "Activity Type",
        ],
    )

    runs_with_week = runs.copy()

    # Define each calendar week as Monday through Sunday
    runs_with_week["week_start"] = (
        runs_with_week["Date"]
        .dt.to_period("W-SUN")
        .dt.start_time
    )

    weekly_training = (
        runs_with_week
        .groupby("week_start", as_index=False)
        .agg(
            weekly_distance_km=(
                "Distance",
                "sum",
            ),
            weekly_running_minutes=(
                "Moving Time",
                lambda durations: (
                    durations.dt.total_seconds().sum() / 60
                ),
            ),
            weekly_run_count=(
                "Activity Type",
                "count",
            ),
        )
        .sort_values("week_start")
        .reset_index(drop=True)
    )

    return weekly_training


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

def add_speed_quality_features(
    runs: pd.DataFrame,
    max_difference_pct: float = 10.0,
) -> pd.DataFrame:
    require_columns(
        runs,
        [
            "Avg Pace",
            "average_speed_kmh",
        ],
    )

    if max_difference_pct < 0:
        raise ValueError(
            "max_difference_pct cannot be negative"
        )

    runs_with_features = runs.copy()

    valid_pace = runs_with_features["Avg Pace"].where(
        runs_with_features["Avg Pace"] > 0
    )

    runs_with_features["speed_from_pace_kmh"] = (
        60 / valid_pace
    )

    runs_with_features["speed_difference_pct"] = (
        (
            runs_with_features["average_speed_kmh"]
            - runs_with_features["speed_from_pace_kmh"]
        ).abs()
        / runs_with_features["speed_from_pace_kmh"]
        * 100
    )

    speed_quality_flag = (
        runs_with_features["speed_difference_pct"]
        > max_difference_pct
    ).astype("boolean")

    runs_with_features["speed_quality_flag"] = (
        speed_quality_flag.mask(
            runs_with_features["speed_difference_pct"].isna(),
            pd.NA,
        )
    )

    return runs_with_features


def add_intensity_features(
    runs: pd.DataFrame,
    athlete_max_hr: float,
) -> pd.DataFrame:
    require_columns(
        runs,
        [
            "Avg HR",
            "Aerobic TE",
            "moving_minutes",
        ],
    )

    if athlete_max_hr <= 0:
        raise ValueError(
            "athlete_max_hr must be greater than zero"
        )

    runs_with_features = runs.copy()

    valid_hr = (
        runs_with_features["Avg HR"].notna()
        & (runs_with_features["Avg HR"] > 0)
    )

    runs_with_features["relative_hr_intensity"] = pd.NA

    runs_with_features.loc[
        valid_hr,
        "relative_hr_intensity",
    ] = (
        runs_with_features.loc[valid_hr, "Avg HR"]
        / athlete_max_hr
    )

    valid_aerobic_effect = (
        runs_with_features["Aerobic TE"].notna()
        & runs_with_features["moving_minutes"].notna()
        & (runs_with_features["moving_minutes"] > 0)
    )

    runs_with_features["aerobic_effect_per_minute"] = pd.NA

    runs_with_features.loc[
        valid_aerobic_effect,
        "aerobic_effect_per_minute",
    ] = (
        runs_with_features.loc[
            valid_aerobic_effect,
            "Aerobic TE",
        ]
        / runs_with_features.loc[
            valid_aerobic_effect,
            "moving_minutes",
        ]
    )

    runs_with_features["relative_hr_intensity"] = (
        pd.to_numeric(
            runs_with_features["relative_hr_intensity"]
        )
    )

    runs_with_features["aerobic_effect_per_minute"] = (
        pd.to_numeric(
            runs_with_features["aerobic_effect_per_minute"]
        )
    )

    return runs_with_features

# ---------------------------------------------------------------------------
# Aerobic-efficiency features
# ---------------------------------------------------------------------------


def add_aerobic_efficiency_features(runs: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        runs,
        [
            "average_speed_kmh",
            "Avg HR",
            "Avg Power",
        ],
    )

    runs_with_features = runs.copy()

    valid_hr = runs_with_features["Avg HR"].where(
        runs_with_features["Avg HR"] > 0
    )

    valid_power = runs_with_features["Avg Power"].where(
        runs_with_features["Avg Power"] > 0
    )

    speed_metres_per_minute = (
        runs_with_features["average_speed_kmh"] * 1000
        / 60
    )

    runs_with_features["metres_per_heartbeat"] = (
        speed_metres_per_minute / valid_hr
    )

    runs_with_features["power_to_hr_ratio"] = (
        valid_power / valid_hr
    )

    runs_with_features["speed_to_power_ratio"] = (
        runs_with_features["average_speed_kmh"] / valid_power
    )

    return runs_with_features


# ---------------------------------------------------------------------------
# Terrain features
# ---------------------------------------------------------------------------


def add_terrain_features(
    runs: pd.DataFrame,
) -> pd.DataFrame:
    require_columns(
        runs,
        [
            "Distance",
            "Total Ascent",
            "moving_minutes",
            "elapsed_minutes",
        ],
    )

    runs_with_features = runs.copy()

    valid_distance = runs_with_features["Distance"].where(
        runs_with_features["Distance"] > 0
    )

    valid_elapsed_time = runs_with_features[
        "elapsed_minutes"
    ].where(
        runs_with_features["elapsed_minutes"] > 0
    )

    runs_with_features["climbing_density_m_per_km"] = (
        runs_with_features["Total Ascent"] / valid_distance
    )

    runs_with_features["pause_ratio"] = (
        (runs_with_features["elapsed_minutes"] - runs_with_features["moving_minutes"])
        / valid_elapsed_time
    )

    return runs_with_features


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
    require_columns(
        runs,
        ["Date"],
    )

    runs_with_features = runs.copy()

    iso_calendar = (
        runs_with_features["Date"]
        .dt.isocalendar()
    )

    runs_with_features["calendar_year"] = (
        iso_calendar["year"]
    )

    runs_with_features["calendar_week"] = (
        iso_calendar["week"]
    )

    runs_with_features["month"] = (
        runs_with_features["Date"].dt.month
    )

    runs_with_features["day_of_week"] = (
        runs_with_features["Date"].dt.day_name()
    )

    return runs_with_features


def add_distance_category(runs: pd.DataFrame) -> pd.DataFrame:
    """Assign the Later-stage short, medium, and long distance categories.

    Distance thresholds require an explicit athlete- and project-level decision
    before this function is implemented.
    """

    raise NotImplementedError


# ---------------------------------------------------------------------------
# MVP orchestration
# ---------------------------------------------------------------------------


def add_mvp_run_features(
    runs: pd.DataFrame,
    *,
    speed_difference_threshold_pct: float = 10.0,
) -> pd.DataFrame:
    runs_with_features = add_duration_features(runs)
    runs_with_features = add_speed_features(runs_with_features)

    runs_with_features = add_speed_quality_features(
        runs_with_features,
        max_difference_pct=speed_difference_threshold_pct,
    )

    runs_with_features = add_terrain_features(
        runs_with_features
    )

    runs_with_features = add_calendar_features(
        runs_with_features
    )

    runs_with_features = add_recovery_spacing_features(
        runs_with_features
    )

    runs_with_features = add_rolling_distance_features(
        runs_with_features
    )

    runs_with_features = add_aerobic_efficiency_features(
        runs_with_features
    )

    return runs_with_features


# ---------------------------------------------------------------------------
# Comparison analyses belong in src/analysis.py
# ---------------------------------------------------------------------------

# The pace-heart-rate trend, aerobic-efficiency trend, and comparable-run score
# compare multiple activities. They are analyses rather than raw per-run feature
# transformations, so their reusable functions should live in ``analysis.py``
# after the underlying features above have been implemented and validated.
