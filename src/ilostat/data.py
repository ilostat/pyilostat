from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

from .cache import (
    _cache_filename,
    _remove_old_cache_files,
    get_cache_dir,
)
from .dictionary import get_dataset_dic
from .filters import apply_filters
from .labels import add_labels, labels_only
from .metadata import get_last_update

BASE_URL = "https://rplumber.ilo.org/files"


def _get_df_single(
    dataset_id: str,
    segment: str = "indicator",
    type: str = "code",
    lang: str = "en",
    filters: dict | None = None,
    best_source: str = "yes",
    fixed: bool = True,
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> pd.DataFrame:
    """
    Retrieve an ILOSTAT dataset as a pandas DataFrame.

    Parameters
    ----------
    dataset_id : str
        ILOSTAT dataset identifier.

    segment : str, default "indicator"
        ILOSTAT bulk-data segment.

    type : {"code", "label", "both"}, default "code"
        Output representation for coded dimensions.

        "code" returns codes only.
        "both" returns codes and labels.
        "label" returns labelled dimensions.

    lang : {"en", "fr", "es"}, default "en"
        Language used for labels.

    filters : dict or None, default None
        Filters applied to the dataset.

    best_source : {"yes", "no", "all"}, default "yes"
        Select best-source observations.

    fixed : bool, default True
        If True, treat filter values as literal strings.

    cache_dir : str, pathlib.Path or None, default None
        Directory used to cache downloaded files.

    refresh : bool, default False
        If True, refresh the table of contents before checking
        the cached dataset.

    Returns
    -------
    pandas.DataFrame
        Requested ILOSTAT dataset.
    """
    type = type.lower()

    if type not in {"code", "label", "both"}:
        raise ValueError(
            "Invalid type value. "
            "Choose from 'code', 'label', or 'both'."
        )

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

    filename = _cache_filename(
        dataset_id=dataset_id,
        segment=segment,
        last_update=last_update,
    )

    segment_dir = cache_path / segment
    segment_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset_file = segment_dir / filename

    if not dataset_file.exists():
        url = (
            f"{BASE_URL}/{segment}/"
            f"{dataset_id}.parquet"
        )

        response = requests.get(
            url,
            timeout=60,
        )
        response.raise_for_status()

        dataset_file.write_bytes(
            response.content
        )

        _remove_old_cache_files(
            cache_dir=segment_dir,
            dataset_id=dataset_id,
            segment=segment,
            keep_file=dataset_file,
        )

    df = pd.read_parquet(dataset_file)

    best_source = best_source.lower()

    if best_source not in {"yes", "no", "all"}:
        raise ValueError(
            "Invalid best_source value. "
            "Choose from 'yes', 'no', or 'all'."
        )

    if "best_source" in df.columns:
        if best_source == "yes":
            df = df.loc[
                df["best_source"] == 1
            ]
        elif best_source == "no":
            df = df.loc[
                df["best_source"] == 0
            ]

    df = apply_filters(
        df,
        filters=filters,
        fixed=fixed,
    )

    if type in {"label", "both"}:
        dic = get_dataset_dic(
            dataset_id=dataset_id,
            segment=segment,
            cache_dir=cache_dir,
            refresh=refresh,
        )

        df = add_labels(
            df,
            dic,
            lang=lang,
        )

        if type == "label":
            df = labels_only(df)

    if best_source == "yes":
        df = df.drop(
            columns=["best_source"],
            errors="ignore",
        )

    return df

def get_df(
    dataset_id: str | list[str] | tuple[str, ...],
    segment: str = "indicator",
    type: str = "code",
    lang: str = "en",
    filters: dict | None = None,
    best_source: str = "yes",
    fixed: bool = True,
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> pd.DataFrame:
    """
    Retrieve one or more ILOSTAT datasets.

    Parameters
    ----------
    dataset_id : str, list of str, or tuple of str
        One or more ILOSTAT dataset identifiers.

    segment : str, default "indicator"
        ILOSTAT bulk-data segment.

    type : {"code", "label", "both"}, default "code"
        Output representation for coded dimensions.

    lang : {"en", "fr", "es"}, default "en"
        Language used for labels.

    filters : dict or None, default None
        Filters applied to each dataset.

    best_source : {"yes", "no", "all"}, default "yes"
        Select best-source observations.

    fixed : bool, default True
        If True, treat filter values as literal strings.

    cache_dir : str, pathlib.Path or None, default None
        Directory used to cache downloaded files.

    refresh : bool, default False
        If True, refresh metadata before checking cached data.

    Returns
    -------
    pandas.DataFrame
        Requested ILOSTAT data.
    """
    if isinstance(dataset_id, str):
        dataset_ids = [dataset_id]
    else:
        dataset_ids = list(dataset_id)

    if not dataset_ids:
        raise ValueError(
            "dataset_id must contain at least one dataset identifier."
        )

    frames = [
        _get_df_single(
            dataset_id=current_id,
            segment=segment,
            type=type,
            lang=lang,
            filters=filters,
            best_source=best_source,
            fixed=fixed,
            cache_dir=cache_dir,
            refresh=refresh,
        )
        for current_id in dataset_ids
    ]

    return pd.concat(
        frames,
        ignore_index=True,
        sort=False,
    )