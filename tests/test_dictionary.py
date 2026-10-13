import pandas as pd

import ilostat


def test_get_dic(tmp_path):
    dic = ilostat.get_dic(
        "classif_type",
        cache_dir=tmp_path,
    )

    assert isinstance(dic, pd.DataFrame)
    assert not dic.empty


def test_get_dic_language(tmp_path):
    dic = ilostat.get_dic(
        "classif_type",
        lang="fr",
        cache_dir=tmp_path,
    )

    assert isinstance(dic, pd.DataFrame)
    assert not dic.empty


def test_get_dic_creates_cache(tmp_path):
    ilostat.get_dic(
        "classif_type",
        cache_dir=tmp_path,
    )

    expected = (
        tmp_path
        / "dic"
        / "classif_type_en.parquet"
    )

    assert expected.exists()