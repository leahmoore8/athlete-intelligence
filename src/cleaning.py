"""Reusable cleaning helpers for Garmin Connect activity exports.

The functions in this module never mutate their input DataFrame.  The main
``clean_garmin_activities`` pipeline is deliberately composed of small helpers
so notebook steps can be inspected and tested independently.
"""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


MISSING_TOKENS = ("--", "")

DATETIME_COLUMNS = ("Date",)

DURATION_COLUMNS = (
    "Time",
    "Moving Time",
    "Elapsed Time",
    "Best Lap Time",
)

PACE_COLUMNS = ("Avg Pace", "Best Pace")

NUMERIC_COLUMNS = (
    "Distance",
    "Calories",
    "Avg HR",
    "Max HR",
    "Aerobic TE",
    "Avg Run Cadence",
    "Max Run Cadence",
    "Total Ascent",
    "Total Descent",
    "Avg Stride Length",
    "Avg Vertical Ratio",
    "Avg Vertical Oscillation",
    "Avg Ground Contact Time",
    "Normalized Power® (NP®)",
    "Training Stress Score®",
    "Avg Power",
    "Max Power",
    "Steps",
    "Body Battery Drain",
    "Number of Laps",
    "Avg Stress",
    "Max Stress",
    "Min Elevation",
    "Max Elevation",
)

UNUSABLE_COLUMNS = (
    "Avg Stress",
    "Max Stress",
    "Decompression",
    "Training Stress Score®",
)

RUNNING_ACTIVITY_TYPES = ("Running", "Treadmill Running")


def _existing(columns: Iterable[str], frame: pd.DataFrame) -> list[str]:
    """Return requested columns that are present, preserving their order."""

    return [column for column in columns if column in frame.columns]


def normalize_missing_values(
    frame: pd.DataFrame,
    missing_tokens: Iterable[str] = MISSING_TOKENS,
) -> pd.DataFrame:
    """Replace Garmin placeholder strings with pandas missing values."""

    cleaned = frame.copy()
    tokens = set(missing_tokens)
    object_columns = cleaned.select_dtypes(include=["object", "string"]).columns

    for column in object_columns:
        stripped = cleaned[column].astype("string").str.strip()
        cleaned[column] = stripped.mask(stripped.isin(tokens), pd.NA)

    return cleaned


def parse_datetime_columns(
    frame: pd.DataFrame,
    columns: Iterable[str] = DATETIME_COLUMNS,
) -> pd.DataFrame:
    """Parse Garmin datetime columns, coercing invalid values to ``NaT``."""

    cleaned = frame.copy()
    for column in _existing(columns, cleaned):
        cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")
    return cleaned


def _clock_to_timedelta(value: object) -> pd.Timedelta | pd.NaT:
    """Convert HH:MM:SS(.s) or MM:SS(.s) clock text to a timedelta."""

    if pd.isna(value):
        return pd.NaT
    if isinstance(value, pd.Timedelta):
        return value

    text = str(value).strip()
    parts = text.split(":")
    if len(parts) == 2:
        text = f"00:{text}"
    elif len(parts) != 3:
        return pd.NaT

    return pd.to_timedelta(text, errors="coerce")


def parse_duration_columns(
    frame: pd.DataFrame,
    columns: Iterable[str] = DURATION_COLUMNS,
) -> pd.DataFrame:
    """Convert activity duration columns to pandas ``timedelta64`` values."""

    cleaned = frame.copy()
    for column in _existing(columns, cleaned):
        cleaned[column] = cleaned[column].map(_clock_to_timedelta)
    return cleaned


def _pace_to_minutes(value: object) -> float:
    """Convert a Garmin MM:SS pace value to decimal minutes per kilometre."""

    duration = _clock_to_timedelta(value)
    if pd.isna(duration):
        return float("nan")
    return duration.total_seconds() / 60


def parse_pace_columns(
    frame: pd.DataFrame,
    columns: Iterable[str] = PACE_COLUMNS,
) -> pd.DataFrame:
    """Convert pace text to numeric minutes per kilometre."""

    cleaned = frame.copy()
    for column in _existing(columns, cleaned):
        cleaned[column] = cleaned[column].map(_pace_to_minutes).astype("float64")
    return cleaned


def convert_numeric_columns(
    frame: pd.DataFrame,
    columns: Iterable[str] = NUMERIC_COLUMNS,
) -> pd.DataFrame:
    """Remove Garmin formatting and convert measurement columns to numbers."""

    cleaned = frame.copy()
    for column in _existing(columns, cleaned):
        values = cleaned[column].astype("string").str.strip()
        values = values.str.replace(",", "", regex=False)
        values = values.str.replace("%", "", regex=False)
        values = values.str.removeprefix("'")
        cleaned[column] = pd.to_numeric(values, errors="coerce")
    return cleaned


def drop_unusable_columns(
    frame: pd.DataFrame,
    columns: Iterable[str] = UNUSABLE_COLUMNS,
) -> pd.DataFrame:
    """Drop fields documented as unavailable or uninformative for this export."""

    return frame.drop(columns=_existing(columns, frame)).copy()


def filter_running_activities(
    frame: pd.DataFrame,
    activity_types: Iterable[str] = RUNNING_ACTIVITY_TYPES,
) -> pd.DataFrame:
    """Keep outdoor and treadmill runs, retaining their original type labels."""

    if "Activity Type" not in frame.columns:
        raise KeyError("Expected an 'Activity Type' column in the Garmin export")

    return frame.loc[frame["Activity Type"].isin(activity_types)].copy()


def clean_garmin_activities(
    frame: pd.DataFrame,
    *,
    running_only: bool = True,
    activity_types: Iterable[str] = RUNNING_ACTIVITY_TYPES,
) -> pd.DataFrame:
    """Apply the documented Garmin cleaning steps in a reproducible order.

    Treadmill activities are retained by default. Their unavailable elevation
    values remain missing, allowing later elevation-derived features to remain
    missing rather than being incorrectly treated as zero.
    """

    cleaned = normalize_missing_values(frame)
    if running_only:
        cleaned = filter_running_activities(cleaned, activity_types)
    cleaned = parse_datetime_columns(cleaned)
    cleaned = parse_duration_columns(cleaned)
    cleaned = parse_pace_columns(cleaned)
    cleaned = convert_numeric_columns(cleaned)
    cleaned = drop_unusable_columns(cleaned)
    return cleaned.reset_index(drop=True)
