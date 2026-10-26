import pandas as pd

import ilostat

DATASET_ID = "CCF_XOXR_CUR_RT_A"
SECOND_DATASET_ID = "EMP_TEMP_SEX_AGE_NB_A"
LABEL_DATASET_ID = "UNE_TUNE_SEX_AGE_NB_A"


def test_get_df_note_labels(tmp_path):
    df = ilostat.get_df(
        LABEL_DATASET_ID,
        type="both",
        best_source="all",
        cache_dir=tmp_path,
    )

    assert "note_classif.label" in df.columns
    assert "note_indicator.label" in df.columns
    assert "note_source.label" in df.columns

def test_get_df_multiple_note_labels(tmp_path):
    df = ilostat.get_df(
        LABEL_DATASET_ID,
        type="both",
        best_source="all",
        cache_dir=tmp_path,
    )

    rows = df.loc[
        df["note_source"] == "S3:20_T2:83"
    ]

    assert not rows.empty

    labels = rows["note_source.label"]

    assert labels.str.contains(
        "Data reference period: September",
        regex=False,
    ).all()

    assert labels.str.contains(
        " | ",
        regex=False,
    ).all()

def test_get_df(tmp_path):
    df = ilostat.get_df(
        DATASET_ID,
        cache_dir=tmp_path,
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_get_df_creates_cache(tmp_path):
    ilostat.get_df(
        DATASET_ID,
        cache_dir=tmp_path,
    )

    segment_dir = tmp_path / "indicator"

    cached_files = list(
        segment_dir.glob(
            f"{DATASET_ID}-*.parquet"
        )
    )

    assert len(cached_files) == 1
    assert cached_files[0].exists()

def test_best_source_yes(tmp_path):
    df = ilostat.get_df(
        DATASET_ID,
        best_source="yes",
        cache_dir=tmp_path,
    )

    assert "best_source" not in df.columns


def test_best_source_all(tmp_path):
    df = ilostat.get_df(
        DATASET_ID,
        best_source="all",
        cache_dir=tmp_path,
    )

    assert "best_source" in df.columns


def test_invalid_best_source(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        ilostat.get_df(
            DATASET_ID,
            best_source="invalid",
            cache_dir=tmp_path,
        )

def test_get_df_type_code(tmp_path):
    df = ilostat.get_df(
        DATASET_ID,
        type="code",
        cache_dir=tmp_path,
    )

    assert not any(
        column.endswith(".label")
        for column in df.columns
    )


def test_get_df_type_both(tmp_path):
    df = ilostat.get_df(
        DATASET_ID,
        type="both",
        cache_dir=tmp_path,
    )

    assert "ref_area" in df.columns
    assert "ref_area.label" in df.columns

    assert "indicator" in df.columns
    assert "indicator.label" in df.columns


def test_get_df_type_label(tmp_path):
    df = ilostat.get_df(
        DATASET_ID,
        type="label",
        cache_dir=tmp_path,
    )

    assert "ref_area" not in df.columns
    assert "ref_area.label" in df.columns

    assert "indicator" not in df.columns
    assert "indicator.label" in df.columns


def test_get_df_invalid_type(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        ilostat.get_df(
            DATASET_ID,
            type="invalid",
            cache_dir=tmp_path,
        )

def test_get_df_french_labels(tmp_path):
    df = ilostat.get_df(
        DATASET_ID,
        type="both",
        lang="fr",
        cache_dir=tmp_path,
    )

    assert "ref_area.label" in df.columns

    france = df.loc[
        df["ref_area"] == "FRA",
        "ref_area.label",
    ]

    if not france.empty:
        assert france.iloc[0] == "France"

def test_get_df_invalid_language(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        ilostat.get_df(
            DATASET_ID,
            type="both",
            lang="de",
            cache_dir=tmp_path,
        )

def test_get_df_multiple_datasets(tmp_path):
    df = ilostat.get_df(
        [
            LABEL_DATASET_ID,
            SECOND_DATASET_ID,
        ],
        filters={
            "ref_area": "FRA",
            "timefrom": 2020,
        },
        cache_dir=tmp_path,
    )

    assert not df.empty

    indicators = set(
        df["indicator"].dropna().unique()
    )

    assert len(indicators) == 2

def test_get_df_multiple_datasets_tuple(tmp_path):
    df = ilostat.get_df(
        (
            LABEL_DATASET_ID,
            SECOND_DATASET_ID,
        ),
        filters={
            "ref_area": "FRA",
            "timefrom": 2020,
        },
        cache_dir=tmp_path,
    )

    assert not df.empty

def test_get_df_empty_dataset_list(tmp_path):
    import pytest

    with pytest.raises(
        ValueError,
        match="at least one dataset identifier",
    ):
        ilostat.get_df(
            [],
            cache_dir=tmp_path,
        )