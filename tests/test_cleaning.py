import pandas as pd
from pandas.testing import assert_frame_equal

from src.cleaning import (
    clean_garmin_activities,
    convert_numeric_columns,
    filter_running_activities,
    normalize_missing_values,
    parse_duration_columns,
    parse_pace_columns,
)


def test_normalize_missing_values_handles_garmin_placeholders():
    raw = pd.DataFrame({"Total Ascent": ["--", "  ", "112"]})

    cleaned = normalize_missing_values(raw)

    assert cleaned["Total Ascent"].isna().tolist() == [True, True, False]
    assert raw["Total Ascent"].tolist() == ["--", "  ", "112"]


def test_convert_numeric_columns_removes_export_formatting():
    raw = pd.DataFrame(
        {
            "Calories": ["1,225"],
            "Body Battery Drain": ["'-23"],
            "Avg Vertical Ratio": ["8.2%"],
        }
    )

    cleaned = convert_numeric_columns(raw)

    assert cleaned.loc[0, "Calories"] == 1225
    assert cleaned.loc[0, "Body Battery Drain"] == -23
    assert cleaned.loc[0, "Avg Vertical Ratio"] == 8.2


def test_duration_and_pace_parsing_support_fractional_seconds():
    raw = pd.DataFrame(
        {
            "Moving Time": ["01:46:49"],
            "Best Lap Time": ["00:00:19.6"],
            "Avg Pace": ["5:38"],
        }
    )

    cleaned = parse_duration_columns(raw)
    cleaned = parse_pace_columns(cleaned)

    assert cleaned.loc[0, "Moving Time"] == pd.Timedelta(hours=1, minutes=46, seconds=49)
    assert cleaned.loc[0, "Best Lap Time"] == pd.Timedelta(seconds=19.6)
    assert abs(cleaned.loc[0, "Avg Pace"] - (5 + 38 / 60)) < 1e-12


def test_filter_running_activities_keeps_outdoor_and_treadmill_runs():
    raw = pd.DataFrame(
        {"Activity Type": ["Running", "Treadmill Running", "Cycling"]}
    )

    cleaned = filter_running_activities(raw)

    assert cleaned["Activity Type"].tolist() == ["Running", "Treadmill Running"]


def test_cleaning_pipeline_drops_unusable_fields_and_preserves_missing_elevation():
    raw = pd.DataFrame(
        {
            "Activity Type": ["Treadmill Running", "Cycling"],
            "Date": ["2026-07-11 09:15:11", "2026-07-10 09:00:00"],
            "Distance": ["5.00", "20.00"],
            "Moving Time": ["00:25:00", "01:00:00"],
            "Avg Pace": ["5:00", "3:00"],
            "Total Ascent": ["--", "100"],
            "Avg Stress": ["--", "--"],
            "Max Stress": ["--", "--"],
            "Decompression": ["No", "No"],
            "Training Stress Score®": ["0.0", "0.0"],
        }
    )

    cleaned = clean_garmin_activities(raw)

    assert len(cleaned) == 1
    assert cleaned.loc[0, "Activity Type"] == "Treadmill Running"
    assert pd.isna(cleaned.loc[0, "Total Ascent"])
    assert pd.api.types.is_datetime64_any_dtype(cleaned["Date"])
    assert cleaned.loc[0, "Moving Time"] == pd.Timedelta(minutes=25)
    assert cleaned.loc[0, "Avg Pace"] == 5.0
    assert not set(
        ["Avg Stress", "Max Stress", "Decompression", "Training Stress Score®"]
    ).intersection(cleaned.columns)


def test_cleaning_pipeline_does_not_mutate_input():
    raw = pd.DataFrame(
        {
            "Activity Type": ["Running"],
            "Date": ["2026-07-11 09:15:11"],
            "Distance": ["19.00"],
        }
    )
    original = raw.copy(deep=True)

    clean_garmin_activities(raw)

    assert_frame_equal(raw, original)
