# SDMX codelists

Use `resource="codelist"` to retrieve the codelist associated with a coded dataset component.

## DataFrame

```python
import ilostat

age = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="codelist",
    component="AGE",
)

print(age.head())
```

Codelist DataFrames use normalized component names:

```text
age                  age.label
AGE_YTHADULT_YGE15   Age (Youth, adults): 15+
AGE_YTHADULT_Y15-64  Age (Youth, adults): 15-64
```

The applicable codelist is determined automatically from the dataset structure.

## Other components

The same interface can be used for other coded components:

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
)
```

Components without a coded representation, such as `TIME_PERIOD`, do not have a codelist.

## Languages

Codelist labels are available in English, French, and Spanish:

```python
age_fr = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="codelist",
    component="AGE",
    lang="fr",
)
```

## SDMX-ML 3.1

```python
xml = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="codelist",
    component="AGE",
    format="sdmx-ml",
)
```

## SDMX-JSON 2.1

```python
json_text = ilostat.get_sdmx(
    "UNE_TUNE_SEX_AGE_NB_A",
    resource="codelist",
    component="AGE",
    format="sdmx-json",
)
```

SDMX-ML and SDMX-JSON codelist outputs are validated during package testing against the official SDMX schemas.