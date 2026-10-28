# ilostat

**Python tools for accessing and working with ILOSTAT data**

`ilostat` provides direct access to ILOSTAT data as pandas DataFrames, with filtering, multilingual labels, metadata, caching, dictionaries, and SDMX-style access.

---

## Installation

Install the latest release from PyPI:

```bash
python -m pip install ilostat
```

## Quick start

Retrieve an ILOSTAT dataset directly as a pandas DataFrame:

```python
import ilostat

df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    filters={
        "ref_area": "FRA",
    },
)

print(df.head())
```

## SDMX access

`ilostat` also provides an SDMX-oriented interface:

```python
df = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    filters={
        "REF_AREA": "FRA",
        "SEX": "SEX_F",
    },
)
```

Dataset structures, codelists, and dataflows can be accessed using SDMX conventions.

Structure, codelist, and dataflow resources can also be serialized as **SDMX-ML 3.1** and **SDMX-JSON 2.1**.

## Main features

<div class="grid cards" markdown>

-   :material-database-search: **Data access**

    Retrieve ILOSTAT datasets directly as pandas DataFrames with `get_df()`.

-   :material-filter: **Filtering**

    Filter by reference area, sex, classification, source, time period, and other dataset dimensions.

-   :material-translate: **Multilingual labels**

    Work with codes and labels in English, French, and Spanish.

-   :material-database-sync: **Local cache**

    Downloaded data and metadata are cached locally and reused automatically.

-   :material-code-json: **SDMX**

    Access data, structures, codelists, and dataflows using SDMX conventions.

-   :material-book-open-variant: **Metadata**

    Retrieve tables of contents, dictionaries, dataset metadata, and dataset-specific dictionaries.

</div>

## Codes and labels

By default, `get_df()` returns ILOSTAT codes.

Use `type="both"` to return codes together with their labels:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="both",
    lang="en",
)
```

Labels are available in English, French, and Spanish:

```python
df = ilostat.get_df(
    "UNE_TUNE_SEX_AGE_NB_A",
    type="both",
    lang="fr",
)
```

## SDMX resources

### Dataset structure

Retrieve the SDMX structure associated with a dataset:

```python
structure = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
)

print(struct