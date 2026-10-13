from __future__ import annotations

from pathlib import Path

from platformdirs import user_cache_dir


def _format_last_update(last_update: str) -> str:
    """
    Convert an ILOSTAT last.update value to a cache timestamp.

    Example
    -------
    '20/09/2026 07:34:56' -> '20260920T073456'
    """
    date_part, time_part = last_update.split(" ")

    day, month, year = date_part.split("/")
    hour, minute, second = time_part.split(":")

    return f"{year}{month}{day}T{hour}{minute}{second}"


def _versioned_cache_filename(
    dataset_id: str,
    segment: str,
    last_update: str,
    suffix: str,
) -> str:
    """
    Build a versioned cache filename.

    Examples
    --------
    Dataset:
    indicator-UNE_TUNE_SEX_AGE_NB_A-20260930T070804.parquet

    Dictionary:
    indicator-UNE_TUNE_SEX_AGE_NB_A-20260930T070804_dic.json
    """
    timestamp = _format_last_update(last_update)

    return (
        f"{segment}-"
        f"{dataset_id}-"
        f"{timestamp}"
        f"{suffix}"
    )


def _cache_filename(
    dataset_id: str,
    segment: str,
    last_update: str,
) -> str:
    """
    Build the filename for a cached ILOSTAT dataset.
    """
    return _versioned_cache_filename(
        dataset_id=dataset_id,
        segment=segment,
        last_update=last_update,
        suffix=".parquet",
    )


def _remove_old_cache_files(
    cache_dir: Path,
    dataset_id: str,
    segment: str,
    keep_file: Path,
    suffix: str = ".parquet",
) -> None:
    """
    Remove obsolete cached versions of an ILOSTAT resource.

    Parameters
    ----------
    cache_dir : pathlib.Path
        Segment cache directory.

    dataset_id : str
        ILOSTAT dataset identifier.

    segment : str
        ILOSTAT data segment.

    keep_file : pathlib.Path
        Current cached file that must be preserved.

    suffix : str, default ".parquet"
        Resource filename suffix.
    """
    pattern = (
        f"{segment}-"
        f"{dataset_id}-"
        f"*{suffix}"
    )

    for file in cache_dir.glob(pattern):
        if file != keep_file:
            file.unlink()


def get_cache_dir(
    cache_dir: str | Path | None = None,
) -> Path:
    """
    Return the ILOSTAT cache directory.

    Parameters
    ----------
    cache_dir : str, pathlib.Path or None
        Custom cache directory. If None, use the operating system's
        standard user cache directory.

    Returns
    -------
    pathlib.Path
        Cache directory.
    """
    if cache_dir is None:
        path = Path(
            user_cache_dir("ilostat")
        )
    else:
        path = Path(cache_dir).expanduser()

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path