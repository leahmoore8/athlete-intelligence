import pandas as pd
from pandas.testing import assert_frame_equal

from src.features import (
    add_aerobic_efficiency_features,
    add_calendar_features,
    add_duration_features,
    add_mvp_run_features,
    add_recovery_spacing_features,
    add_rolling_distance_features,
    add_speed_features,
    add_speed_quality_features,
    add_terrain_features,
    summarize_weekly_training,
)


def test_add_duration_features_converts_timedeltas_to_minutes():
    runs = pd.DataFrame(
        {
            "Moving Time": [pd.Timedelta(hours=1, minutes=30)],
            "Elapsed Time": [pd.Timedelta(hours=1, minutes=45)],
        }
    )

    featured = add_duration_features(runs)

    assert featured.loc[0, "moving_minutes"] == 90
    assert featured.loc[0, "elapsed_minutes"] == 105


def test_add_speed_features_calculates_kilometres_per_hour():
    runs = pd.DataFrame({"Distance": [10.0], "moving_minutes": [50.0]})

    featured = add_speed_features(runs)

    assert featured.loc[0, "average_speed_kmh"] == 12.0


def test_add_speed_features_leaves_zero_duration_missing():
    runs = pd.DataFrame({"Distance": [10.0], "moving_minutes": [0.0]})

    featured = add_speed_features(runs)

    assert pd.isna(featured.loc[0, "average_speed_kmh"])


def test_feature_functions_do_not_mutate_input():
    runs = pd.DataFrame(
        {
            "Moving Time": [pd.Timedelta(minutes=50)],
            "Elapsed Time": [pd.Timedelta(minutes=55)],
        }
    )
    original = runs.copy(deep=True)

    add_duration_features(runs)

    assert_frame_equal(runs, original)

def test_add_calendar_features_extracts_calendar_fields():
    runs = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2026-01-01 08:00:00",
                    "2026-07-11 09:15:11",
                ]
            )
        }
    )

    featured = add_calendar_features(runs)

    assert featured["calendar_year"].tolist() == [
        2026,
        2026,
    ]

    assert featured["calendar_week"].tolist() == [
        1,
        28,
    ]

    assert featured["month"].tolist() == [
        1,
        7,
    ]

    assert featured["day_of_week"].tolist() == [
        "Thursday",
        "Saturday",
    ]

def test_add_mvp_run_features_creates_expected_columns():
    runs = pd.DataFrame(
        {
            "Activity Type": [
                "Running",
                "Treadmill Running",
            ],
            "Date": pd.to_datetime(
                [
                    "2026-01-01 08:00:00",
                    "2026-01-02 08:00:00",
                ]
            ),
            "Distance": [
                10.0,
                5.0,
            ],
            "Moving Time": pd.to_timedelta(
                [
                    "00:50:00",
                    "00:30:00",
                ]
            ),
            "Elapsed Time": pd.to_timedelta(
                [
                    "00:55:00",
                    "00:35:00",
                ]
            ),
            "Avg Pace": [
                5.0,
                6.0,
            ],
            "Avg HR": [
                160.0,
                150.0,
            ],
            "Avg Power": [
                250.0,
                200.0,
            ],
            "Total Ascent": [
                100.0,
                float("nan"),
            ],
        }
    )

    featured = add_mvp_run_features(runs)

    expected_columns = {
        "moving_minutes",
        "elapsed_minutes",
        "average_speed_kmh",
        "speed_from_pace_kmh",
        "speed_difference_pct",
        "speed_quality_flag",
        "climbing_density_m_per_km",
        "pause_ratio",
        "calendar_year",
        "calendar_week",
        "month",
        "day_of_week",
        "days_since_previous_run",
        "rolling_7_day_distance_km",
        "rolling_28_day_distance_km",
        "metres_per_heartbeat",
        "power_to_hr_ratio",
        "speed_to_power_ratio",
    }

    assert expected_columns.issubset(
        featured.columns
    )

    assert len(featured) == len(runs)

    assert featured["average_speed_kmh"].tolist() == [
        12.0,
        10.0,
    ]

    assert featured["speed_quality_flag"].tolist() == [
        False,
        False,
    ]

    assert pd.isna(
        featured.loc[0, "days_since_previous_run"]
    )

    assert (
        featured.loc[1, "days_since_previous_run"]
        == 1
    )

def test_add_mvp_run_features_does_not_mutate_input():
    runs = pd.DataFrame(
        {
            "Activity Type": ["Running"],
            "Date": pd.to_datetime(
                ["2026-01-01 08:00:00"]
            ),
            "Distance": [10.0],
            "Moving Time": pd.to_timedelta(
                ["00:50:00"]
            ),
            "Elapsed Time": pd.to_timedelta(
                ["00:55:00"]
            ),
            "Avg Pace": [5.0],
            "Avg HR": [160.0],
            "Avg Power": [250.0],
            "Total Ascent": [100.0],
        }
    )

    original = runs.copy(deep=True)

    add_mvp_run_features(runs)

    assert_frame_equal(runs, original)

def test_add_rolling_distance_features_uses_time_windows():
    runs = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-01-05",
                    "2026-01-10",
                    "2026-02-10",
                ]
            ),
            "Distance": [
                5.0,
                10.0,
                20.0,
                3.0,
            ],
        }
    )

    featured = add_rolling_distance_features(runs)

    assert featured[
        "rolling_7_day_distance_km"
    ].tolist() == [
        5.0,
        15.0,
        30.0,
        3.0,
    ]

    assert featured[
        "rolling_28_day_distance_km"
    ].tolist() == [
        5.0,
        15.0,
        35.0,
        3.0,
    ]

def test_summarize_weekly_training_aggregates_monday_to_sunday():
    runs = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2026-01-05",
                    "2026-01-07",
                    "2026-01-12",
                ]
            ),
            "Distance": [
                10.0,
                5.0,
                8.0,
            ],
            "Moving Time": pd.to_timedelta(
                [
                    "01:00:00",
                    "00:30:00",
                    "00:45:00",
                ]
            ),
            "Activity Type": [
                "Running",
                "Treadmill Running",
                "Running",
            ],
        }
    )

    weekly = summarize_weekly_training(runs)

    assert weekly["weekly_distance_km"].tolist() == [
        15.0,
        8.0,
    ]

    assert weekly[
        "weekly_running_minutes"
    ].tolist() == [
        90.0,
        45.0,
    ]

    assert weekly["weekly_run_count"].tolist() == [
        2,
        1,
    ]

    assert weekly["week_start"].tolist() == [
        pd.Timestamp("2026-01-05"),
        pd.Timestamp("2026-01-12"),
    ]

def test_add_speed_quality_features_flags_large_difference():
    runs = pd.DataFrame(
        {
            "Avg Pace": [
                5.0,
                5.0,
            ],
            "average_speed_kmh": [
                12.0,
                15.0,
            ],
        }
    )

    featured = add_speed_quality_features(
        runs,
        max_difference_pct=10.0,
    )

    assert featured[
        "speed_from_pace_kmh"
    ].tolist() == [
        12.0,
        12.0,
    ]

    assert featured[
        "speed_difference_pct"
    ].tolist() == [
        0.0,
        25.0,
    ]

    assert featured[
        "speed_quality_flag"
    ].tolist() == [
        False,
        True,
    ]

def test_add_aerobic_efficiency_features_calculates_ratios():
    runs = pd.DataFrame(
        {
            "average_speed_kmh": [
                12.0,
                10.0,
            ],
            "Avg HR": [
                160.0,
                0.0,
            ],
            "Avg Power": [
                240.0,
                0.0,
            ],
        }
    )

    featured = add_aerobic_efficiency_features(
        runs
    )

    assert abs(
        featured.loc[0, "metres_per_heartbeat"]
        - 1.25
    ) < 1e-12

    assert abs(
        featured.loc[0, "power_to_hr_ratio"]
        - 1.5
    ) < 1e-12

    assert abs(
        featured.loc[0, "speed_to_power_ratio"]
        - 0.05
    ) < 1e-12

    assert pd.isna(
        featured.loc[1, "metres_per_heartbeat"]
    )

    assert pd.isna(
        featured.loc[1, "power_to_hr_ratio"]
    )

    assert pd.isna(
        featured.loc[1, "speed_to_power_ratio"]
    )

def test_add_terrain_features_calculates_density_and_pause_ratio():
    runs = pd.DataFrame(
        {
            "Distance": [
                10.0,
                5.0,
            ],
            "Total Ascent": [
                100.0,
                float("nan"),
            ],
            "moving_minutes": [
                50.0,
                30.0,
            ],
            "elapsed_minutes": [
                60.0,
                30.0,
            ],
        }
    )

    featured = add_terrain_features(runs)

    assert featured.loc[
        0,
        "climbing_density_m_per_km",
    ] == 10.0

    assert pd.isna(
        featured.loc[
            1,
            "climbing_density_m_per_km",
        ]
    )

    assert abs(
        featured.loc[0, "pause_ratio"]
        - (10 / 60)
    ) < 1e-12

    assert featured.loc[
        1,
        "pause_ratio",
    ] == 0.0

def test_add_recovery_spacing_features_sorts_and_calculates_gaps():
    runs = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2026-01-03 09:00:00",
                    "2026-01-01 08:00:00",
                    "2026-01-03 17:00:00",
                ]
            ),
            "Distance": [
                10.0,
                5.0,
                7.0,
            ],
        }
    )

    featured = add_recovery_spacing_features(
        runs
    )

    assert featured["Date"].tolist() == [
        pd.Timestamp("2026-01-01 08:00:00"),
        pd.Timestamp("2026-01-03 09:00:00"),
        pd.Timestamp("2026-01-03 17:00:00"),
    ]

    assert pd.isna(
        featured.loc[
            0,
            "days_since_previous_run",
        ]
    )

    assert featured.loc[
        1,
        "days_since_previous_run",
    ] == 2

    assert featured.loc[
        2,
        "days_since_previous_run",
    ] == 0