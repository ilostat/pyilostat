# SDMX

`ilostat` provides an SDMX-oriented interface to ILOSTAT through `get_sdmx()`.

## Data

Retrieve data using SDMX component identifiers:

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

Typical SDMX components include:

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

Classification dimensions are derived from dataset metadata. For example, an ILOSTAT `classif1` dimension representing age is exposed as `AGE`.

## Resources

`get_sdmx()` currently supports:

```text
data
structure
codelist
dataflow
```

### Structure

```python
structure = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
)
```

See [Structures](structure.md).

### Codelist

```python
age = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="codelist",
    component="AGE",
)
```

See [Codelists](codelist.md).

### Dataflow

```python
dataflows = ilostat.get_sdmx(
    resource="dataflow",
)
```

See [Dataflows](dataflow.md).

## Formats

The default format is a pandas DataFrame:

```python
structure = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    format="dataframe",
)
```

Structure, codelist, and dataflow resources can also be serialized as:

```text
sdmx-ml
sdmx-json
```

The package targets:

- **SDMX-ML 3.1**
- **SDMX-JSON 2.1**

These outputs are validated during package testing against the official SDMX schemas.

## Languages

SDMX labels and names are available in English, French, and Spanish:

```python
structure = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    type="both",
    lang="fr",
)
```

Supported codes are:

```text
en
fr
es
```