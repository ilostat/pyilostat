import pandas as pd

import ilostat
from ilostat.sdmx import (
    _add_value_labels,
    _apply_sdmx_operator_filters,
    _extract_constant_filters,
    _format_sdmx_time_period,
    _get_component_map,
    _split_sdmx_filters,
    _translate_sdmx_filters,
)


def test_get_component_map():
    meta = {
        "dimensions": {
            "ref_area": {
                "api_name": "ref_area",
            },
            "sex": {
                "api_name": "sex",
                "type": "SEX",
            },
            "age": {
                "api_name": "classif1",
                "type": "AGE",
            },
        }
    }

    result = _get_component_map(meta)

    assert result == {
        "REF_AREA": "ref_area",
        "SEX": "sex",
        "AGE": "classif1",
    }


def test_classification_label():
    df = pd.DataFrame({
        "AGE": [
            "AGE_YTHADULT_Y15-24",
        ]
    })

    dimension = {
        "api_name": "classif1",
        "values": [
            {
                "code": "AGE_YTHADULT_Y15-24",
                "label": {
                    "en": "Age (Youth, adults): 15-24 years",
                },
                "display": {
                    "en": "15-24",
                },
            }
        ],
    }

    _add_value_labels(
        out=df,
        column="AGE",
        dimension=dimension,
        lang="en",
        type="label",
    )

    assert (
        df.loc[0, "AGE"]
        == "Age (Youth, adults): 15-24 years"
    )


def test_classification_label_short():
    df = pd.DataFrame({
        "AGE": [
            "AGE_YTHADULT_Y15-24",
        ]
    })

    dimension = {
        "api_name": "classif1",
        "values": [
            {
                "code": "AGE_YTHADULT_Y15-24",
                "label": {
                    "en": "Age (Youth, adults): 15-24 years",
                },
                "display": {
                    "en": "15-24",
                },
            }
        ],
    }

    _add_value_labels(
        out=df,
        column="AGE",
        dimension=dimension,
        lang="en",
        type="label_short",
    )

    assert df.loc[0, "AGE"] == "15-24"


def test_classification_both():
    df = pd.DataFrame({
        "AGE": [
            "AGE_YTHADULT_Y15-24",
        ]
    })

    dimension = {
        "api_name": "classif1",
        "values": [
            {
                "code": "AGE_YTHADULT_Y15-24",
                "label": {
                    "en": "Age (Youth, adults): 15-24 years",
                },
                "display": {
                    "en": "15-24",
                },
            }
        ],
    }

    _add_value_labels(
        out=df,
        column="AGE",
        dimension=dimension,
        lang="en",
        type="both",
    )

    assert (
        df.loc[0, "AGE"]
        == "AGE_YTHADULT_Y15-24"
    )

    assert (
        df.loc[0, "AGE_LABEL"]
        == "Age (Youth, adults): 15-24 years"
    )

def test_non_classification_uses_display():
    df = pd.DataFrame({
        "SEX": ["SEX_F"]
    })

    dimension = {
        "api_name": "sex",
        "values": [
            {
                "code": "SEX_F",
                "label": {
                    "en": "Sex: Female",
                },
                "display": {
                    "en": "Female",
                },
            }
        ],
    }

    _add_value_labels(
        out=df,
        column="SEX",
        dimension=dimension,
        lang="en",
        type="label",
    )

    assert df.loc[0, "SEX"] == "Female"

def test_translate_sdmx_filters():
    meta = {
        "dimensions": {
            "ref_area": {
                "api_name": "ref_area",
            },
            "sex": {
                "api_name": "sex",
                "type": "SEX",
            },
            "age": {
                "api_name": "classif1",
                "type": "AGE",
            },
        }
    }

    filters = {
        "REF_AREA": "FRA",
        "SEX": "SEX_F",
        "AGE": "AGE_YTHADULT_Y15-24",
        "TIME_PERIOD": "2024",
    }

    result = _translate_sdmx_filters(
        filters,
        meta,
    )

    assert result == {
        "ref_area": "FRA",
        "sex": "SEX_F",
        "classif1": "AGE_YTHADULT_Y15-24",
        "time": "2024",
    }

def test_constant_filters_match():
    meta = {
        "dataset": {
            "frequency": {
                "code": "A",
            }
        },
        "sdmx": {
            "measure": {
                "code": "UNE_TUNE_NB",
            },
        },
    }

    filters, matches = _extract_constant_filters(
        {
            "REF_AREA": "FRA",
            "FREQ": "A",
            "MEASURE": "UNE_TUNE_NB",
        },
        meta,
    )

    assert matches is True
    assert filters == {
        "REF_AREA": "FRA",
    }


def test_constant_frequency_does_not_match():
    meta = {
        "dataset": {
            "frequency": {
                "code": "A",
            }
        },
        "sdmx": {
            "measure": {
                "code": "UNE_TUNE_NB",
            },
        },
    }

    filters, matches = _extract_constant_filters(
        {
            "REF_AREA": "FRA",
            "FREQ": "Q",
        },
        meta,
    )

    assert matches is False
    assert filters == {
        "REF_AREA": "FRA",
    }


def test_constant_measure_does_not_match():
    meta = {
        "dataset": {
            "frequency": {
                "code": "A",
            }
        },
        "sdmx": {
            "measure": {
                "code": "UNE_TUNE_NB",
            },
        },
    }

    filters, matches = _extract_constant_filters(
        {
            "MEASURE": "XXX",
        },
        meta,
    )

    assert matches is False
    assert filters == {}

def test_split_sdmx_filters():
    filters = {
        "REF_AREA": "FRA",
        "SEX": "SEX_F",
        "TIME_PERIOD": {
            "ge": "2020",
            "le": "2024",
        },
    }

    simple, operators = _split_sdmx_filters(
        filters
    )

    assert simple == {
        "REF_AREA": "FRA",
        "SEX": "SEX_F",
    }

    assert operators == {
        "TIME_PERIOD": {
            "ge": "2020",
            "le": "2024",
        }
    }


def test_apply_sdmx_operator_filters():
    df = pd.DataFrame({
        "TIME_PERIOD": [
            "2020",
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
        ],
        "OBS_VALUE": [
            10,
            11,
            12,
            13,
            14,
            15,
        ],
    })

    result, remaining = (
        _apply_sdmx_operator_filters(
            df=df,
            filters={
                "TIME_PERIOD": {
                    "gt": "2022",
                    "lt": "2024",
                }
            },
        )
    )

    assert result[
        "TIME_PERIOD"
    ].tolist() == [
        "2023",
    ]

    assert result[
        "OBS_VALUE"
    ].tolist() == [
        13,
    ]

    assert remaining is None

def test_time_period_operators_use_year():
    df = pd.DataFrame({
        "TIME_PERIOD": [
            "2023M12",
            "2024M01",
            "2024M06",
            "2024M12",
            "2025M01",
        ],
        "OBS_VALUE": [
            1,
            2,
            3,
            4,
            5,
        ],
    })

    result, _ = (
        _apply_sdmx_operator_filters(
            df=df,
            filters={
                "TIME_PERIOD": {
                    "ge": "2024",
                    "le": "2024",
                }
            },
        )
    )

    assert result[
        "TIME_PERIOD"
    ].tolist() == [
        "2024M01",
        "2024M06",
        "2024M12",
    ]

def test_time_period_operator_returns_whole_year():
    df = pd.DataFrame({
        "TIME_PERIOD": [
            "2023Q4",
            "2024Q1",
            "2024Q2",
            "2024Q3",
            "2024Q4",
            "2025Q1",
        ],
    })

    result, _ = (
        _apply_sdmx_operator_filters(
            df=df,
            filters={
                "TIME_PERIOD": {
                    "eq": "2024",
                }
            },
        )
    )

    assert result[
        "TIME_PERIOD"
    ].tolist() == [
        "2024Q1",
        "2024Q2",
        "2024Q3",
        "2024Q4",
    ]

def test_sdmx_time_period_annual():
    values = pd.Series([
        "2023",
        "2024",
    ])

    result = _format_sdmx_time_period(
        values
    )

    assert result.tolist() == [
        "2023",
        "2024",
    ]


def test_sdmx_time_period_quarterly():
    values = pd.Series([
        "2024Q1",
        "2024Q4",
    ])

    result = _format_sdmx_time_period(
        values
    )

    assert result.tolist() == [
        "2024-Q1",
        "2024-Q4",
    ]


def test_sdmx_time_period_monthly():
    values = pd.Series([
        "2024M01",
        "2024M12",
    ])

    result = _format_sdmx_time_period(
        values
    )

    assert result.tolist() == [
        "2024-M01",
        "2024-M12",
    ]

def test_sdmx_both_adds_dataset_level_labels():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        type="both",
    )

    assert "FREQ_LABEL" in df.columns
    assert "MEASURE_LABEL" in df.columns
    assert "UNIT_MEASURE_LABEL" in df.columns
    assert "UNIT_MULT_LABEL" in df.columns

    assert df["FREQ"].eq("A").all()
    assert df["FREQ_LABEL"].eq("Annual").all()

    assert df["MEASURE"].eq(
        "UNE_DEAP_RT"
    ).all()

    assert df["UNIT_MEASURE"].eq(
        "PT"
    ).all()

    assert df["UNIT_MEASURE_LABEL"].eq(
        "%"
    ).all()

    assert df["UNIT_MULT"].astype(str).eq(
        "0"
    ).all()

    assert df["UNIT_MULT_LABEL"].eq(
        "units"
    ).all()


def test_sdmx_source_label():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        type="both",
        filters={
            "SOURCE": "BA:148",
        },
    )

    assert "SOURCE_LABEL" in df.columns

    assert df["SOURCE"].eq(
        "BA:148"
    ).all()

    assert df["SOURCE_LABEL"].eq(
        "LFS - Employment Survey"
    ).all()


def test_sdmx_observation_status_label():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        type="both",
        best_source="all",
    )

    status = df.loc[
        df["OBS_STATUS"].notna(),
        [
            "OBS_STATUS",
            "OBS_STATUS_LABEL",
        ],
    ]

    assert not status.empty

    known = status[
        status["OBS_STATUS"].eq("B")
    ]

    if not known.empty:
        assert known[
            "OBS_STATUS_LABEL"
        ].eq(
            "Break in series"
        ).all()


def test_sdmx_note_labels():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        type="both",
        best_source="all",
    )

    assert "NOTE_SOURCE_LABEL" in df.columns
    assert "NOTE_INDICATOR_LABEL" in df.columns
    assert "NOTE_CLASSIF_LABEL" in df.columns

    notes = df.loc[
        df["NOTE_SOURCE"].eq(
            "R1:3513"
        )
    ]

    if not notes.empty:
        assert notes[
            "NOTE_SOURCE_LABEL"
        ].eq(
            "Repository: ILO-STATISTICS - "
            "Micro data processing"
        ).all()


def test_sdmx_drops_physical_indicator():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
    )

    assert "indicator" not in df.columns


def test_sdmx_column_order():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        type="both",
    )

    columns = list(
        df.columns
    )

    expected_order = [
        "STRUCTURE",
        "STRUCTURE_ID",
        "STRUCTURE_NAME",
        "ACTION",
        "REF_AREA",
        "REF_AREA_LABEL",
        "SOURCE",
        "SOURCE_LABEL",
        "FREQ",
        "FREQ_LABEL",
        "MEASURE",
        "MEASURE_LABEL",
        "SEX",
        "SEX_LABEL",
        "AGE",
        "AGE_LABEL",
        "TIME_PERIOD",
        "OBS_VALUE",
        "OBS_STATUS",
        "OBS_STATUS_LABEL",
        "UNIT_MEASURE",
        "UNIT_MEASURE_LABEL",
        "UNIT_MULT",
        "UNIT_MULT_LABEL",
        "NOTE_SOURCE",
        "NOTE_SOURCE_LABEL",
        "NOTE_INDICATOR",
        "NOTE_INDICATOR_LABEL",
        "NOTE_CLASSIF",
        "NOTE_CLASSIF_LABEL",
    ]

    positions = [
        columns.index(column)
        for column in expected_order
        if column in columns
    ]

    assert positions == sorted(
        positions
    )


def test_sdmx_best_source_column():
    default = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
    )

    all_sources = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        best_source="all",
    )

    non_best = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        best_source="no",
    )

    assert "BEST_SOURCE" not in default.columns

    assert "BEST_SOURCE" in all_sources.columns
    assert "BEST_SOURCE" in non_best.columns

    assert all_sources.columns[-1] == (
        "BEST_SOURCE"
    )

    assert non_best.columns[-1] == (
        "BEST_SOURCE"
    )