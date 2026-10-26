from pathlib import Path

from ilostat.cache import (
    _cache_filename,
    _format_last_update,
    get_cache_dir,
)


def test_custom_cache_dir(tmp_path):
    cache = tmp_path / "ilostat-cache"

    result = get_cache_dir(cache)

    assert result == cache
    assert result.exists()
    assert result.is_dir()


def test_custom_cache_dir_string(tmp_path):
    cache = tmp_path / "ilostat-cache"

    result = get_cache_dir(str(cache))

    assert result == Path(cache)
    assert result.exists()


def test_format_last_update():
    result = _format_last_update(
        "20/09/2026 07:34:56"
    )

    assert result == "20260920T073456"


def test_cache_filename():
    result = _cache_filename(
        dataset_id="CPI_XCPI_COI_RT_A",
        last_update="20/09/2026 07:34:56",
    )

    assert (
        result
        == "CPI_XCPI_COI_RT_A-20260920T073456.parquet"
    )