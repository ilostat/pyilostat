# SDMX structures

Use `resource="structure"` to retrieve the structure associated with an ILOSTAT dataset.

## DataFrame

```python
import ilostat

structure = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    type="both",
)

print(structure)
```

The structure DataFrame describes components using:

```text
COMPONENT_ID
ROLE
POSITION
REPRESENTATION
COMPONENT_NAME
CODELIST
```

Typical components include dimensions, the time dimension, observation value, and attributes.

## Codelist references

Coded components reference canonical ILOSTAT codelists, for example:

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

## Languages

Component names can be requested in English, French, or Spanish:

```python
structure = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    type="both",
    lang="fr",
)
```

## SDMX-ML 3.1

Serialize the structure as SDMX-ML 3.1:

```python
xml = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    format="sdmx-ml",
)
```

The generated structure includes the dataset concept scheme, dimensions, time dimension, measure, attributes, representations, codelist references, and attribute relationships.

## SDMX-JSON 2.1

Serialize the structure as SDMX-JSON 2.1:

```python
json_text = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="structure",
    format="sdmx-json",
)
```

SDMX-ML and SDMX-JSON structure outputs are validated during package testing against the official SDMX schemas.