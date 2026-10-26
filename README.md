# ilostat

Python tools for accessing and working with [ILOSTAT](https://ilostat.ilo.org/) data.

`ilostat` provides direct access to ILOSTAT bulk datasets as pandas DataFrames, with filtering, multilingual labels, caching, and access to ILOSTAT metadata and dictionaries.

## Installation

Install `ilostat` from PyPI:

```bash
python -m pip install ilostat
```

For development, clone the repository and install the package in editable mode with the development and testing dependencies:

```bash
python -m pip install -e ".[dev]"
```

## Quick start

```python
import ilostat

df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A"
)

df.head()
```

## Filter data

Filters are supplied as a dictionary.

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    filters={
        "ref_area": "FRA",
        "sex": "SEX_F",
    },
)
```

Multiple values can be supplied:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    filters={
        "ref_area": ["FRA", "CHE"],
        "sex": ["SEX_T", "SEX_F"],
    },
)
```

Partial matching is supported. For example:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    filters={
        "sex": "T",
    },
)
```

Use `fixed=False` for regular-expression matching:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    filters={
        "ref_area": "FRA|CHE",
    },
    fixed=False,
)
```

### Filter by year

Use `timefrom` and `timeto` to restrict the time range:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    filters={
        "ref_area": "FRA",
        "timefrom": 2020,
        "timeto": 2025,
    },
)
```

The `time` column is returned in its original ILOSTAT character format, for example:

```text
2025
2025Q1
2025M01
```

depending on the dataset frequency.

## Codes and labels

By default, `get_df()` returns ILOSTAT codes:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="code",
)
```

Use `type="both"` to return codes together with their labels:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="both",
)
```

For example:

```text
ref_area  ref_area.label  sex    sex.label
FRA       France          SEX_T  Total
```

Use `type="label"` to retain labelled dimensions without their corresponding code columns:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="label",
)
```

Label languages currently supported are English, French and Spanish:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="both",
    lang="fr",
)
```

Available language codes are:

```text
en
fr
es
```

## Notes

ILOSTAT observation notes are labelled automatically when `type="both"` or `type="label"` is requested.

This includes:

```text
note_classif
note_indicator
note_source
```

Observations containing multiple note codes are resolved to their corresponding note labels.

## Best source

By default, `get_df()` returns ILOSTAT best-source observations:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    best_source="yes",
)
```

Available options are:

```text
yes    best source only
no     non-best source only
all    all sources
```

For example:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    best_source="all",
)
```

## Multiple datasets

Several datasets can be retrieved in one call:

```python
df = ilostat.get_df(
    [
        "UNE_TUNE_SEX_AGE_NB_A",
        "EMP_TEMP_SEX_AGE_NB_A",
    ],
    filters={
        "ref_area": "FRA",
        "timefrom": 2020,
    },
)
```

The datasets are combined into a single pandas DataFrame.

## Table of contents

Use `get_toc()` to retrieve the ILOSTAT table of contents:

```python
toc = ilostat.get_toc()

toc.head()
```

The default segment is `indicator`.

A reference-area table of contents can also be retrieved:

```python
toc = ilostat.get_toc(
    segment="ref_area"
)
```

The table of contents is available in English, French and Spanish:

```python
toc = ilostat.get_toc(
    lang="fr"
)
```

## Dictionaries

ILOSTAT dictionaries can be retrieved with `get_dic()`:

```python
sex = ilostat.get_dic("sex")

sex.head()
```

For example:

```text
sex    sex.label
SEX_T  Total
SEX_M  Male
SEX_F  Female
```

Other dictionaries include, for example:

```python
ref_area = ilostat.get_dic("ref_area")
classif1 = ilostat.get_dic("classif1")
source = ilostat.get_dic("source")
obs_status = ilostat.get_dic("obs_status")
```

Dictionary labels are available in English, French and Spanish:

```python
sex_fr = ilostat.get_dic(
    "sex",
    lang="fr",
)
```

## Data segments

ILOSTAT bulk data can be retrieved by indicator or reference area.

Indicator is the default:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A"
)
```

Reference-area datasets can be retrieved with:

```python
df = ilostat.get_df(
    "FRA_A",
    segment="ref_area",
)
```

## Caching

Downloaded datasets and their dataset-specific dictionaries are cached locally.

By default, `ilostat` uses the operating system's standard user cache directory.

A custom cache directory can be supplied:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    cache_dir=r"J:\my\ilostat\cache",
)
```

Cached datasets are versioned using the ILOSTAT `last.update` value from the table of contents. When a dataset is updated, the current version is downloaded and obsolete cached versions are removed.

Use `refresh=True` to force a refresh of the relevant metadata before checking the cache:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    refresh=True,
)
```

## Main API

```python
ilostat.get_df()
ilostat.get_toc()
ilostat.get_dic()
ilostat.get_dataset_dic()
ilostat.get_metadata()
```

The main data retrieval interface is:

```python
ilostat.get_df(
    dataset_id,
    segment="indicator",
    type="code",
    lang="en",
    filters=None,
    best_source="yes",
    fixed=True,
    cache_dir=None,
    refresh=False,
)
```

## Cache

`ilostat` caches downloaded data and metadata locally to avoid downloading the same resources repeatedly.

### Default cache

By default, no cache configuration is required:

```python
import ilostat

df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
)
```

When `cache_dir` is not specified, `ilostat` uses the operating system's standard user cache location.

You can see the location used on your system with:

```python
ilostat.get_cache_dir()
```

The default cache is **persistent**: cached files remain available after the Python session ends and are reused by later sessions.

This improves performance and reduces unnecessary downloads. However, ILOSTAT datasets can be large, and using many different datasets may progressively increase the size of the local cache.

Users who prefer not to use space in their operating system user cache can specify their own cache directory.

### Custom cache directory

Use `cache_dir` to store cached resources in a location of your choice:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    cache_dir="D:/ilostat_cache",
)
```

The same cache directory can be shared across ILOSTAT operations:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    cache_dir="D:/ilostat_cache",
)

sdmx = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    cache_dir="D:/ilostat_cache",
)
```

The custom directory can be inspected with:

```python
ilostat.get_cache_dir(
    "D:/ilostat_cache",
)
```

### Cache versions and refresh

Cached resources are versioned using the ILOSTAT `last.update` timestamp.

When the current version is already available locally, `ilostat` can reuse it instead of downloading the resource again.

When a newer version of the same resource is cached, obsolete cached versions of that resource are removed automatically.

To force a fresh retrieval, use:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    refresh=True,
)
```

The same `refresh` option can be used together with a custom cache:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    cache_dir="D:/ilostat_cache",
    refresh=True,
)
```

### Clearing the cache

Cached files are not automatically deleted when a Python session ends.

To remove all resources stored in the default ILOSTAT cache:

```python
ilostat.clean_cache()
```

To clean a custom ILOSTAT cache:

```python
ilostat.clean_cache(
    cache_dir="D:/ilostat_cache",
)
```

`clean_cache()` removes the cached files and empty subdirectories while preserving the cache root directory.

For users working with many or very large ILOSTAT datasets, using a custom `cache_dir` and cleaning it when no longer needed provides explicit control over local disk usage.

## Development

Run the test suite with:

```bash
python -m pytest
```

Run code-quality checks with:

```bash
python -m ruff check src tests
```

Build the package with:

```bash
python -m build
```

## Author

**David Bescond**  
International Labour Organization  
[ORCID: 0000-0002-1642-0304](https://orcid.org/0000-0002-1642-0304)

## Citation

If you use `ilostat` in research or publications, please cite the package using the citation metadata provided in [`CITATION.cff`](CITATION.cff).

## Software license

`ilostat` is distributed under the [BSD 2-Clause License](LICENSE).

Copyright © 2026 International Labour Organization.

## ILOSTAT data licensing

ILOSTAT databases and datasets, together with their accompanying referential metadata, published by the International Labour Organization (ILO) as of 3 May 2023 are licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/), unless otherwise indicated.

Users may reuse, share and adapt this material in accordance with the terms of the licence and must give appropriate credit to the International Labour Organization (ILO) as the source.

The licensing of ILOSTAT data and metadata is separate from the BSD 2-Clause License applying to the `ilostat` Python software.

For full information on ILO copyright, data licensing, third-party material and other rights and permissions, see the [ILO Rights and permissions](https://www.ilo.org/rights-and-permissions) page.