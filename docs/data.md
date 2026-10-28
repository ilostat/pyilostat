# Data access

`ilostat` retrieves ILOSTAT bulk data directly as pandas DataFrames.

## Retrieve a dataset

Use `get_df()` with an ILOSTAT dataset identifier:

```python
import ilostat

df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
)

print(df.head())
```

Dataset identifiers can be discovered with:

```python
toc = ilostat.get_toc()
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

Partial matching is supported:

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

## Filter by time

Use `timefrom` and `timeto`:

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

Time values remain in their original ILOSTAT representation, for example:

```text
2025
2025Q1
2025M01
```

depending on dataset frequency.

## Codes and labels

By default, `get_df()` returns ILOSTAT codes:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="code",
)
```

Use `type="both"` to return codes together with labels:

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

Classification dimensions also support `type="label_short"` for compact display labels when available.

## Languages

Labels are available in English, French, and Spanish:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="both",
    lang="fr",
)
```

Supported language codes are:

```text
en
fr
es
```

## Observation notes

Observation notes are labelled automatically when `type="both"` or `type="label"` is requested.

This includes:

```text
note_classif
note_indicator
note_source
```

Observations containing multiple note codes are resolved to their corresponding note labels.

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

Retrieve all sources with:

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

## Data segments

ILOSTAT bulk data can be retrieved by indicator or reference area.

Indicator is the default:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
)
```

Reference-area datasets can be retrieved with:

```python
df = ilostat.get_df(
    "FRA_A",
    segment="ref_area",
)
```

## SDMX-style data access

For SDMX component names, use `get_sdmx()`:

```python
df = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    filters={
        "REF_AREA": "FRA",
        "SEX": "SEX_F",
        "TIME_PERIOD": "2020:2025",
    },
)
```

See the [SDMX documentation](sdmx/index.md) for structures, codelists, and dataflows.