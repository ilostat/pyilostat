# SDMX dataflows

ILOSTAT datasets are exposed as SDMX Dataflows.

The Dataflow catalogue is derived from the multilingual ILOSTAT table of contents.

## Dataflow catalogue

Retrieve all available Dataflows:

```python
import ilostat

dataflows = ilostat.get_sdmx(
    resource="dataflow",
)

print(dataflows.head())
```

The DataFrame contains:

```text
DATAFLOW_ID
DATAFLOW_NAME
LAST_UPDATE
```

`DATAFLOW_NAME` combines the localized indicator label and frequency label.

For example:

```text
DATAFLOW_ID                 DATAFLOW_NAME
UNE_TUNE_SEX_AGE_NB_A      Unemployment by sex and age (thousands) - Annual
```

## Retrieve one Dataflow

Provide a dataset identifier to retrieve a specific Dataflow:

```python
dataflow = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="dataflow",
)
```

## Languages

Dataflow names are available in English, French, and Spanish:

```python
dataflow = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="dataflow",
    lang="fr",
)
```

## Last update

`LAST_UPDATE` comes from the ILOSTAT table of contents.

It can be used by Python clients to identify datasets that have changed since a previous retrieval.

Downloaded resources are also managed through the `ilostat` cache.

## Data Structure Definition

Each formal SDMX Dataflow references the corresponding ILOSTAT Data Structure Definition.

For example:

```text
Dataflow:
ILO:UNE_TUNE_SEX_AGE_NB_A(1.0)

Data Structure:
ILO:UNE_TUNE_SEX_AGE_NB_A(1.0)
```

The artefact type distinguishes the Dataflow from its Data Structure Definition.

## SDMX-ML 3.1

```python
xml = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="dataflow",
    format="sdmx-ml",
)
```

## SDMX-JSON 2.1

```python
json_text = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="dataflow",
    format="sdmx-json",
)
```

SDMX-ML and SDMX-JSON Dataflow outputs are validated during package testing against the official SDMX schemas.