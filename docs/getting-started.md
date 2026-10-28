# Getting started

This guide covers installation and the main operations needed to start working with ILOSTAT data in Python.

## Installation

`ilostat` is available from PyPI and requires Python 3.10 or later.

Install the latest release with:

```bash
python -m pip install ilostat
```

To upgrade an existing installation:

```bash
python -m pip install --upgrade ilostat
```

Verify the installation:

```python
import ilostat

print(ilostat.get_toc().head())
```

## Retrieve a dataset

Use `get_df()` to retrieve an ILOSTAT dataset as a pandas DataFrame:

```python
import ilostat

df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
)

print(df.head())
```

Dataset identifiers can be found in the ILOSTAT table of contents.

## Find available datasets

Use `get_toc()`:

```python
toc = ilostat.get_toc()

print(toc.head())
```

The default data segment is `indicator`.

The table of contents is available in English, French, and Spanish:

```python
toc_fr = ilostat.get_toc(
    lang="fr",
)
```

## Filter data

Filters are supplied as a dictionary:

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
        "ref_area": [
            "FRA",
            "CHE",
        ],
        "sex": [
            "SEX_T",
            "SEX_F",
        ],
    },
)
```

## Filter by time

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

ILOSTAT time values remain in their original character representation.

Depending on the dataset frequency, examples include:

```text
2025
2025Q1
2025M01
```

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

Use `type="label"` to return labelled dimensions without their corresponding code columns:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="label",
)
```

Classification dimensions also support `type="label_short"` for compact display labels when available.

## Languages

Labels are available in:

```text
en    English
fr    French
es    Spanish
```

For example:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="both",
    lang="fr",
)
```

## Best-source observations

By default, `get_df()` returns ILOSTAT best-source observations:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    best_source="yes",
)
```

Available options are:

```text
yes    best-source observations
no     non-best-source observations
all    all observations
```

To retrieve all sources:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    best_source="all",
)
```

## Observation notes

Observation notes are automatically labelled when `type="both"` or `type="label"` is requested.

This includes:

```text
note_classif
note_indicator
note_source
```

Observations containing multiple note codes are resolved to their corresponding note labels.

## Retrieve dictionaries

Use `get_dic()` to retrieve an ILOSTAT dictionary:

```python
sex = ilostat.get_dic(
    "sex",
)

print(sex.head())
```

For example:

```text
sex    sex.label
SEX_T  Total
SEX_M  Male
SEX_F  Female
```

Dictionary labels are also available in English, French, and Spanish:

```python
sex_fr = ilostat.get_dic(
    "sex",
    lang="fr",
)
```

## Dataset metadata

Retrieve dataset metadata with:

```python
metadata = ilostat.get_metadata(
    "UNE_TUNE_SEX_AGE_NB_A",
)
```

Dataset-specific dictionaries are available with:

```python
dictionary = ilostat.get_dataset_dic(
    "UNE_TUNE_SEX_AGE_NB_A",
)
```

## SDMX-style access

Use `get_sdmx()` to work with SDMX component names:

```python
df = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    filters={
        "REF_AREA": "FRA",
        "SEX": "SEX_F",
    },
)
```

For example, ILOSTAT dimensions are represented using SDMX-style identifiers such as:

```text
REF_AREA
SOURCE
FREQ
MEASURE
SEX
AGE
TIME_PERIOD
OBS_VALUE
OBS_STATUS
UNIT_MEASURE
UNIT_MULT
```

`get_sdmx()` also provides dataset structures, codelists, and dataflows.

See the SDMX documentation for details.

## Cache

Downloaded resources are cached locally and reused automatically.

Inspect the cache location with:

```python
ilostat.get_cache_dir()
```

Force a refresh with:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    refresh=True,
)
```

Clear the cache with:

```python
ilostat.clean_cache()
```

## Next steps

Continue with:

- [API reference](reference/api.md)
- SDMX data access
- SDMX structures
- SDMX codelists
- SDMX dataflows