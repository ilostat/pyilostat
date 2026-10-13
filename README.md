# ilostat

Python tools for accessing and working with [ILOSTAT](https://ilostat.ilo.org/) data.

`ilostat` provides direct access to ILOSTAT bulk datasets as pandas DataFrames, with filtering, multilingual labels, caching, and access to ILOSTAT metadata and dictionaries.

## Installation

For development, install the package from the project directory:

```bash
python -m pip install -e .
```

To include development and testing dependencies:

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
yes   best source only
no    non-best source only
all   all sources
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

## License

MIT License.