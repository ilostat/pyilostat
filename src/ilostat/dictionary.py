from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from .cache import (
    _remove_old_cache_files,
    _versioned_cache_filename,
    get_cache_dir,
)
from .metadata import get_last_update

BASE_URL = "https://rplumber.ilo.org/files/dic"
DATA_BASE_URL = "https://rplumber.ilo.org/files"

VALID_LANGUAGES = {"en", "fr", "es"}

_REFRESHED_DICS: set[tuple[str, str, str]] = set()


def get_dic(
    dic: str,
    lang: str = "en",
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> pd.DataFrame:
    """
    Retrieve an ILOSTAT dictionary.

    Parameters
    ----------
    dic : str
        Dictionary name, for example "ref_area", "sex",
        or "classif_type".

    lang : {"en", "fr", "es"}, default "en"
        Dictionary language.

    cache_dir : str, pathlib.Path or None, default None
        Directory used to cache downloaded dictionaries.

    refresh : bool, default False
        If True, force a new download of the dictionary.

    Returns
    -------
    pandas.DataFrame
        Requested ILOSTAT dictionary.
    """
    lang = lang.lower()

    if lang not in VALID_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{lang}'. "
            f"Choose from {sorted(VALID_LANGUAGES)}."
        )

    cache_path = get_cache_dir(cache_dir)

    dic_dir = cache_path / "dic"
    dic_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    dic_file = dic_dir / f"{dic}_{lang}.parquet"

    cache_key = (
        str(cache_path.resolve()),
        dic,
        lang,
    )

    should_download = (
        refresh
        or cache_key not in _REFRESHED_DICS
        or not dic_file.exists()
    )

    if should_download:
        url = (
            f"{BASE_URL}/"
            f"{dic}_{lang}.parquet"
        )

        response = requests.get(
            url,
            timeout=60,
        )
        response.raise_for_status()

        dic_file.write_bytes(
            response.content
        )

        _REFRESHED_DICS.add(cache_key)

    return pd.read_parquet(dic_file)


def get_dataset_dic(
    dataset_id: str,
    segment: str = "indicator",
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> dict[str, Any]:
    """
    Retrieve the dataset-specific ILOSTAT dictionary.

    The cached dictionary is versioned using the dataset
    last.update value from the table of contents.

    Parameters
    ----------
    dataset_id : str
        ILOSTAT dataset identifier.

    segment : str, default "indicator"
        ILOSTAT data segment.

    cache_dir : str, pathlib.Path or None, default None
        Directory used to cache downloaded files.

    refresh : bool, default False
        If True, refresh the table of contents before checking
        the cached dictionary.

    Returns
    -------
    dict
        Dataset-specific dictionary.
    """
    cache_path = get_cache_dir(cache_dir)

    last_update = get_last_update(
        dataset_id=dataset_id,
        segment=segment,
        cache_dir=cache_dir,
        refresh=refresh,
    )

    if last_update is None:
        raise ValueError(
            f"Dataset '{dataset_id}' was not found "
            f"in the '{segment}' table of contents."
        )

    segment_dir = cache_path / segment
    segment_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = _versioned_cache_filename(
        dataset_id=dataset_id,
        last_update=last_update,
        suffix="_dic.json",
    )

    dic_file = segment_dir / filename

    if not dic_file.exists():
        url = (
            f"{DATA_BASE_URL}/{segment}/"
            f"{dataset_id}_dic.json"
        )

        response = requests.get(
            url,
            timeout=60,
        )
        response.raise_for_status()

        dic_file.write_bytes(
            response.content
        )

        _remove_old_cache_files(
            cache_dir=segment_dir,
            dataset_id=dataset_id,
            keep_file=dic_file,
            suffix="_dic.json",
        )

    with dic_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)