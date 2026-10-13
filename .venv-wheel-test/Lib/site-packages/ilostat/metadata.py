from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from .cache import get_cache_dir

BASE_URL = "https://rplumber.ilo.org/files"

VALID_LANGUAGES = {"en", "fr", "es"}

_REFRESHED_TOCS: set[tuple[str, str, str]] = set()


def get_toc(
    segment: str = "indicator",
    lang: str = "en",
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> pd.DataFrame:
    """
    Retrieve an ILOSTAT table of contents.

    The TOC is refreshed from the ILOSTAT server once per Python
    session for each segment, language, and cache directory.

    Parameters
    ----------
    segment : str, default "indicator"
        ILOSTAT data segment.

    lang : {"en", "fr", "es"}, default "en"
        Language of the table of contents.

    cache_dir : str, pathlib.Path or None, default None
        Directory used to cache downloaded files.

    refresh : bool, default False
        If True, force a new download of the table of contents.

    Returns
    -------
    pandas.DataFrame
        ILOSTAT table of contents.
    """
    lang = lang.lower()

    if lang not in VALID_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{lang}'. "
            f"Choose from {sorted(VALID_LANGUAGES)}."
        )

    cache_path = get_cache_dir(cache_dir)

    toc_file = (
        cache_path
        / segment
        / f"table_of_contents_{lang}.parquet"
    )

    toc_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cache_key = (
        str(cache_path.resolve()),
        segment,
        lang,
    )

    should_download = (
        refresh
        or cache_key not in _REFRESHED_TOCS
        or not toc_file.exists()
    )

    if should_download:
        url = (
            f"{BASE_URL}/{segment}/"
            f"table_of_contents_{lang}.parquet"
        )

        response = requests.get(
            url,
            timeout=60,
        )
        response.raise_for_status()

        toc_file.write_bytes(
            response.content
        )

        _REFRESHED_TOCS.add(cache_key)

    return pd.read_parquet(toc_file)


def get_last_update(
    dataset_id: str,
    segment: str = "indicator",
    lang: str = "en",
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> str | None:
    """
    Return the last.update value for an ILOSTAT dataset.
    """
    toc = get_toc(
        segment=segment,
        lang=lang,
        cache_dir=cache_dir,
        refresh=refresh,
    )

    row = toc.loc[
        toc["id"] == dataset_id
    ]

    if row.empty:
        return None

    value = row.iloc[0]["last.update"]

    if pd.isna(value):
        return None

    return str(value)


def get_metadata(
    dataset_id: str,
    segment: str = "indicator",
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> dict[str, Any]:
    """
    Retrieve metadata for an ILOSTAT dataset.

    Parameters
    ----------
    dataset_id : str
        ILOSTAT dataset identifier.

    segment : str, default "indicator"
        ILOSTAT data segment.

    cache_dir : str, pathlib.Path or None, default None
        Directory used to cache downloaded files.

    refresh : bool, default False
        If True, download the metadata again even if a cached
        copy already exists.

    Returns
    -------
    dict
        Dataset metadata.
    """
    cache_path = get_cache_dir(cache_dir)

    metadata_file = (
        cache_path
        / segment
        / f"{dataset_id}_meta.json"
    )

    metadata_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if refresh or not metadata_file.exists():
        url = (
            f"{BASE_URL}/{segment}/"
            f"{dataset_id}_meta.json"
        )

        response = requests.get(
            url,
            timeout=60,
        )
        response.raise_for_status()

        metadata_file.write_bytes(
            response.content
        )

    with metadata_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)