# ilostat

Python tools for accessing and working with [ILOSTAT](https://ilostat.ilo.org/) data.

ilostat provides direct access to ILOSTAT data as pandas DataFrames, with filtering, multilingual labels, caching, metadata and dictionaries, together with SDMX-style data access and SDMX-ML 3.1 dataset structures.

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

## SDMX

`ilostat` provides SDMX-style access to ILOSTAT data, dataset structures and codelists through `get_sdmx()`.

### SDMX data

Use `get_sdmx()` to retrieve data using SDMX component names:

```python
import ilostat

df = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    filters={
        "REF_AREA": "FRA",
        "SEX": "SEX_F",
        "TIME_PERIOD": "2020:2025",
    },
)
```

ILOSTAT dataset dimensions are mapped to SDMX-style components such as:

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

Classification dimensions are derived from the dataset metadata. For example, an ILOSTAT `classif1` dimension representing age is exposed as `AGE`.

The DataFrame interface supports codes and localized labels:

```python
df = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="both",
    lang="fr",
)
```

Available label languages are English (`en`), French (`fr`) and Spanish (`es`).

### SDMX structure

Use `resource="structure"` to retrieve the structure associated with a dataset:

```python
structure = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    type="both",
)

print(structure)
```

The structure DataFrame describes the dataset components using:

```text
COMPONENT_ID
ROLE
POSITION
REPRESENTATION
COMPONENT_NAME
CODELIST
```

Coded components are associated with canonical ILOSTAT codelists, for example:

```text
REF_AREA       cl_ref_area
SOURCE         cl_source
FREQ           cl_freq
MEASURE        cl_measure
SEX            cl_sex
AGE            cl_age
OBS_STATUS     cl_obs_status
UNIT_MEASURE   cl_unit_measure
UNIT_MULT      cl_unit_mult
BEST_SOURCE    cl_best_source
```

Non-coded components such as `TIME_PERIOD` and `OBS_VALUE` do not use codelists.

Structure component names are available in English, French and Spanish:

```python
structure = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    type="both",
    lang="fr",
)
```

### SDMX codelists

Use `resource="codelist"` and an SDMX component identifier to retrieve the codelist associated with that component:

```python
age = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="codelist",
    component="AGE",
)
```

Codelist DataFrames use normalized component names:

```text
age                  age.label
AGE_YTHADULT_YGE15   Age (Youth, adults): 15+
AGE_YTHADULT_Y15-64  Age (Youth, adults): 15-64
...
```

The applicable codelist is determined from the dataset structure, so the same interface can be used for other coded components:

```python
areas = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="codelist",
    component="REF_AREA",
)

sex = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="codelist",
    component="SEX",
    lang="fr",
)
```

Components without a coded representation, such as `TIME_PERIOD`, do not have a codelist.

### SDMX structure formats

Structure and codelist resources can be serialized as SDMX-ML 3.1 or SDMX-JSON 2.1.

For a dataset structure:

```python
xml = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    format="sdmx-ml",
)

json_text = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    format="sdmx-json",
)
```

For a codelist:

```python
xml = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="codelist",
    component="AGE",
    format="sdmx-ml",
)

json_text = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="codelist",
    component="AGE",
    format="sdmx-json",
)
```

The default format remains a pandas DataFrame:

```python
structure = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    format="dataframe",
)
```

SDMX-ML 3.1 and SDMX-JSON 2.1 structure and codelist outputs are validated during package testing against the official SDMX schemas.

## Main API

The main public functions are:

```python
ilostat.get_df()
ilostat.get_sdmx()
ilostat.get_toc()
ilostat.get_dic()
ilostat.get_dataset_dic()
ilostat.get_metadata()
ilostat.get_cache_dir()
ilostat.clean_cache()
```

`get_df()` provides direct access to the ILOSTAT bulk-data representation.

`get_sdmx()` provides SDMX-style data access, dataset structures and component codelists, with SDMX-ML 3.1 and SDMX-JSON 2.1 serialization for structure resources.

`get_toc()`, `get_dic()`, `get_dataset_dic()`, and `get_metadata()` provide access to the supporting ILOSTAT metadata resources.

## Cache

`ilostat` caches downloaded data and metadata locally to avoid repeatedly downloading the same resources.

### Default cache

No cache configuration is required:

```python
import ilostat

df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
)
```

When `cache_dir` is not specified, `ilostat` uses the operating system's standard user cache location.

You can inspect that location with:

```python
ilostat.get_cache_dir()
```

The default cache is persistent: cached files remain available after the Python session ends and can be reused by later sessions.

This improves performance and reduces unnecessary downloads. However, ILOSTAT datasets can be large, so using many datasets may progressively increase local cache size.

### Custom cache directory

A custom cache location can be specified with `cache_dir`:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    cache_dir="D:/ilostat_cache",
)
```

The same cache can be used by other ILOSTAT operations:

```python
sdmx = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    cache_dir="D:/ilostat_cache",
)
```

The custom location can be inspected with:

```python
ilostat.get_cache_dir(
    "D:/ilostat_cache",
)
```

### Cache versions and refresh

Cached datasets and dataset-specific resources are versioned using the ILOSTAT `last.update` timestamp.

When the current version is already cached, it can be reused without downloading the resource again. When a newer version is downloaded, obsolete cached versions of the same resource are removed automatically.

Use `refresh=True` to force a refresh of the relevant metadata before checking the cache:

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

### Clearing the cache

Cached files are not automatically deleted when a Python session ends.

To clear the default ILOSTAT cache:

```python
ilostat.clean_cache()
```

To clear a custom cache:

```python
ilostat.clean_cache(
    cache_dir="D:/ilostat_cache",
)
```

`clean_cache()` removes cached files and empty subdirectories while preserving the cache root directory.

For users working with many or very large ILOSTAT datasets, a custom `cache_dir` provides explicit control over local disk usage.

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