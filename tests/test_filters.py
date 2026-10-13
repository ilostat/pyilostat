import pandas as pd
import pytest

from ilostat.filters import apply_filters


def test_filter_exact_partial_code():
    df = pd.DataFrame(
        {
            "sex": ["SEX_T", "SEX_M", "SEX_F"],
            "obs_value": [10, 20, 30],
        }
    )

    result = apply_filters(
        df,
        filters={"sex": "T"},
    )

    assert result["sex"].tolist() == ["SEX_T"]


def test_filter_multiple_values():
    df = pd.DataFrame(
        {
            "sex": ["SEX_T", "SEX_M", "SEX_F"],
            "obs_value": [10, 20, 30],
        }
    )

    result = apply_filters(
        df,
        filters={"sex": ["T", "F"]},
    )

    assert result["sex"].tolist() == ["SEX_T", "SEX_F"]


def test_filter_multiple_columns():
    df = pd.DataFrame(
        {
            "ref_area": ["FRA", "FRA", "CHE"],
            "sex": ["SEX_T", "SEX_F", "SEX_T"],
            "obs_value": [10, 20, 30],
        }
    )

    result = apply_filters(
        df,
        filters={
            "ref_area": "FRA",
            "sex": "T",
        },
    )

    assert len(result) == 1
    assert result.iloc[0]["ref_area"] == "FRA"
    assert result.iloc[0]["sex"] == "SEX_T"


def test_filter_regex():
    df = pd.DataFrame(
        {
            "sex": ["SEX_T", "SEX_M", "SEX_F"],
        }
    )

    result = apply_filters(
        df,
        filters={"sex": r"SEX_[MF]"},
        fixed=False,
    )

    assert result["sex"].tolist() == ["SEX_M", "SEX_F"]


def test_filter_unknown_column():
    df = pd.DataFrame(
        {
            "sex": ["SEX_T"],
        }
    )

    with pytest.raises(ValueError):
        apply_filters(
            df,
            filters={"unknown": "ABC"},
        )

def test_timefrom():
    df = pd.DataFrame(
        {
            "time": [
                "2018",
                "2019",
                "2020",
                "2021",
            ],
        }
    )

    result = apply_filters(
        df,
        filters={"timefrom": 2020},
    )

    assert result["time"].tolist() == [
        "2020",
        "2021",
    ]


def test_timeto():
    df = pd.DataFrame(
        {
            "time": [
                "2018",
                "2019",
                "2020",
                "2021",
            ],
        }
    )

    result = apply_filters(
        df,
        filters={"timeto": 2019},
    )

    assert result["time"].tolist() == [
        "2018",
        "2019",
    ]


def test_time_range_quarterly():
    df = pd.DataFrame(
        {
            "time": [
                "2019Q4",
                "2020Q1",
                "2020Q4",
                "2021Q1",
                "2022Q1",
            ],
        }
    )

    result = apply_filters(
        df,
        filters={
            "timefrom": 2020,
            "timeto": 2021,
        },
    )

    assert result["time"].tolist() == [
        "2020Q1",
        "2020Q4",
        "2021Q1",
    ]


def test_time_range_monthly():
    df = pd.DataFrame(
        {
            "time": [
                "2019M12",
                "2020M01",
                "2020M12",
                "2021M01",
            ],
        }
    )

    result = apply_filters(
        df,
        filters={
            "timefrom": "2020",
            "timeto": "2020",
        },
    )

    assert result["time"].tolist() == [
        "2020M01",
        "2020M12",
    ]