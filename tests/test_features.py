import pandas as pd
from pandas.testing import assert_frame_equal

from src.features import add_duration_features, add_speed_features


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
