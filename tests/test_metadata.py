import pandas as pd

import ilostat


def test_get_toc_indicator(tmp_path):
    toc = ilostat.get_toc(
        segment="indicator",
        cache_dir=tmp_path,
    )

    assert isinstance(toc, pd.DataFrame)
    assert not toc.empty
    assert "id" in toc.columns
    assert "last.update" in toc.columns


def test_get_toc_ref_area(tmp_path):
    toc = ilostat.get_toc(
        segment="ref_area",
        cache_dir=tmp_path,
    )

    assert isinstance(toc, pd.DataFrame)
    assert not toc.empty
    assert "id" in toc.columns
    assert "last.update" in toc.columns


def test_get_toc_language(tmp_path):
    toc = ilostat.get_toc(
        segment="indicator",
        lang="fr",
        cache_dir=tmp_path,
    )

    assert isinstance(toc, pd.DataFrame)
    assert not toc.empty


def test_get_toc_creates_cache(tmp_path):
    ilostat.get_toc(
        segment="indicator",
        cache_dir=tmp_path,
    )

    expected = (
        tmp_path
        / "indicator"
        / "table_of_contents_en.parquet"
    )

    assert expected.exists()