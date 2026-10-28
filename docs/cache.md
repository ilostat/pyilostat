# Cache

`ilostat` caches downloaded data and metadata locally to avoid repeatedly downloading the same resources.

## Default cache

No cache configuration is required:

```python
import ilostat

df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
)
```

When `cache_dir` is not specified, `ilostat` uses the operating system's standard user cache location.

Inspect the location with:

```python
ilostat.get_cache_dir()
```

The cache is persistent and can be reused by later Python sessions.

## Custom cache directory

Specify a custom cache with `cache_dir`:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    cache_dir="D:/ilostat_cache",
)
```

The same cache can be used by SDMX operations:

```python
structure = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    cache_dir="D:/ilostat_cache",
)
```

Inspect a custom cache location with:

```python
ilostat.get_cache_dir(
    "D:/ilostat_cache",
)
```

## Cache versions

Dataset-specific cached resources are versioned using the ILOSTAT `last.update` timestamp.

When the current version is already cached, it can be reused without downloading the resource again.

When a newer version is downloaded, obsolete cached versions of the same resource are removed automatically.

## Refresh resources

Use `refresh=True` to force a refresh of the relevant metadata before checking cached resources:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    refresh=True,
)
```

The option can also be used with a custom cache:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    cache_dir="D:/ilostat_cache",
    refresh=True,
)
```

## Dataflow update information

The SDMX Dataflow catalogue exposes the ILOSTAT `LAST_UPDATE` value:

```python
dataflows = ilostat.get_sdmx(
    resource="dataflow",
)
```

The result includes:

```text
DATAFLOW_ID
DATAFLOW_NAME
LAST_UPDATE
```

This can be used to identify datasets that have changed since a previous retrieval.

## Clear the cache

Cached files are not automatically deleted when a Python session ends.

Clear the default cache with:

```python
ilostat.clean_cache()
```

Clear a custom cache with:

```python
ilostat.clean_cache(
    cache_dir="D:/ilostat_cache",
)
```

`clean_cache()` removes cached files and empty subdirectories while preserving the cache root directory.