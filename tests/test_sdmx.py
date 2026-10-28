import pandas as pd
import pytest

import ilostat
from ilostat.sdmx import (
    _add_value_labels,
    _apply_sdmx_operator_filters,
    _build_sdmx_structure_model,
    _extract_constant_filters,
    _format_sdmx_time_period,
    _get_component_map,
    _split_sdmx_filters,
    _translate_sdmx_filters,
)


def test_get_component_map():
    meta = {
        "dimensions": {
            "ref_area": {
                "api_name": "ref_area",
            },
            "sex": {
                "api_name": "sex",
                "type": "SEX",
            },
            "age": {
                "api_name": "classif1",
                "type": "AGE",
            },
        }
    }

    result = _get_component_map(meta)

    assert result == {
        "REF_AREA": "ref_area",
        "SEX": "sex",
        "AGE": "classif1",
    }


def test_classification_label():
    df = pd.DataFrame({
        "AGE": [
            "AGE_YTHADULT_Y15-24",
        ]
    })

    dimension = {
        "api_name": "classif1",
        "values": [
            {
                "code": "AGE_YTHADULT_Y15-24",
                "label": {
                    "en": "Age (Youth, adults): 15-24 years",
                },
                "display": {
                    "en": "15-24",
                },
            }
        ],
    }

    _add_value_labels(
        out=df,
        column="AGE",
        dimension=dimension,
        lang="en",
        type="label",
    )

    assert (
        df.loc[0, "AGE"]
        == "Age (Youth, adults): 15-24 years"
    )


def test_classification_label_short():
    df = pd.DataFrame({
        "AGE": [
            "AGE_YTHADULT_Y15-24",
        ]
    })

    dimension = {
        "api_name": "classif1",
        "values": [
            {
                "code": "AGE_YTHADULT_Y15-24",
                "label": {
                    "en": "Age (Youth, adults): 15-24 years",
                },
                "display": {
                    "en": "15-24",
                },
            }
        ],
    }

    _add_value_labels(
        out=df,
        column="AGE",
        dimension=dimension,
        lang="en",
        type="label_short",
    )

    assert df.loc[0, "AGE"] == "15-24"


def test_classification_both():
    df = pd.DataFrame({
        "AGE": [
            "AGE_YTHADULT_Y15-24",
        ]
    })

    dimension = {
        "api_name": "classif1",
        "values": [
            {
                "code": "AGE_YTHADULT_Y15-24",
                "label": {
                    "en": "Age (Youth, adults): 15-24 years",
                },
                "display": {
                    "en": "15-24",
                },
            }
        ],
    }

    _add_value_labels(
        out=df,
        column="AGE",
        dimension=dimension,
        lang="en",
        type="both",
    )

    assert (
        df.loc[0, "AGE"]
        == "AGE_YTHADULT_Y15-24"
    )

    assert (
        df.loc[0, "AGE_LABEL"]
        == "Age (Youth, adults): 15-24 years"
    )

def test_non_classification_uses_display():
    df = pd.DataFrame({
        "SEX": ["SEX_F"]
    })

    dimension = {
        "api_name": "sex",
        "values": [
            {
                "code": "SEX_F",
                "label": {
                    "en": "Sex: Female",
                },
                "display": {
                    "en": "Female",
                },
            }
        ],
    }

    _add_value_labels(
        out=df,
        column="SEX",
        dimension=dimension,
        lang="en",
        type="label",
    )

    assert df.loc[0, "SEX"] == "Female"

def test_translate_sdmx_filters():
    meta = {
        "dimensions": {
            "ref_area": {
                "api_name": "ref_area",
            },
            "sex": {
                "api_name": "sex",
                "type": "SEX",
            },
            "age": {
                "api_name": "classif1",
                "type": "AGE",
            },
        }
    }

    filters = {
        "REF_AREA": "FRA",
        "SEX": "SEX_F",
        "AGE": "AGE_YTHADULT_Y15-24",
        "TIME_PERIOD": "2024",
    }

    result = _translate_sdmx_filters(
        filters,
        meta,
    )

    assert result == {
        "ref_area": "FRA",
        "sex": "SEX_F",
        "classif1": "AGE_YTHADULT_Y15-24",
        "time": "2024",
    }

def test_constant_filters_match():
    meta = {
        "dataset": {
            "frequency": {
                "code": "A",
            }
        },
        "sdmx": {
            "measure": {
                "code": "UNE_TUNE_NB",
            },
        },
    }

    filters, matches = _extract_constant_filters(
        {
            "REF_AREA": "FRA",
            "FREQ": "A",
            "MEASURE": "UNE_TUNE_NB",
        },
        meta,
    )

    assert matches is True
    assert filters == {
        "REF_AREA": "FRA",
    }


def test_constant_frequency_does_not_match():
    meta = {
        "dataset": {
            "frequency": {
                "code": "A",
            }
        },
        "sdmx": {
            "measure": {
                "code": "UNE_TUNE_NB",
            },
        },
    }

    filters, matches = _extract_constant_filters(
        {
            "REF_AREA": "FRA",
            "FREQ": "Q",
        },
        meta,
    )

    assert matches is False
    assert filters == {
        "REF_AREA": "FRA",
    }


def test_constant_measure_does_not_match():
    meta = {
        "dataset": {
            "frequency": {
                "code": "A",
            }
        },
        "sdmx": {
            "measure": {
                "code": "UNE_TUNE_NB",
            },
        },
    }

    filters, matches = _extract_constant_filters(
        {
            "MEASURE": "XXX",
        },
        meta,
    )

    assert matches is False
    assert filters == {}

def test_split_sdmx_filters():
    filters = {
        "REF_AREA": "FRA",
        "SEX": "SEX_F",
        "TIME_PERIOD": {
            "ge": "2020",
            "le": "2024",
        },
    }

    simple, operators = _split_sdmx_filters(
        filters
    )

    assert simple == {
        "REF_AREA": "FRA",
        "SEX": "SEX_F",
    }

    assert operators == {
        "TIME_PERIOD": {
            "ge": "2020",
            "le": "2024",
        }
    }


def test_apply_sdmx_operator_filters():
    df = pd.DataFrame({
        "TIME_PERIOD": [
            "2020",
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
        ],
        "OBS_VALUE": [
            10,
            11,
            12,
            13,
            14,
            15,
        ],
    })

    result, remaining = (
        _apply_sdmx_operator_filters(
            df=df,
            filters={
                "TIME_PERIOD": {
                    "gt": "2022",
                    "lt": "2024",
                }
            },
        )
    )

    assert result[
        "TIME_PERIOD"
    ].tolist() == [
        "2023",
    ]

    assert result[
        "OBS_VALUE"
    ].tolist() == [
        13,
    ]

    assert remaining is None

def test_time_period_operators_use_year():
    df = pd.DataFrame({
        "TIME_PERIOD": [
            "2023M12",
            "2024M01",
            "2024M06",
            "2024M12",
            "2025M01",
        ],
        "OBS_VALUE": [
            1,
            2,
            3,
            4,
            5,
        ],
    })

    result, _ = (
        _apply_sdmx_operator_filters(
            df=df,
            filters={
                "TIME_PERIOD": {
                    "ge": "2024",
                    "le": "2024",
                }
            },
        )
    )

    assert result[
        "TIME_PERIOD"
    ].tolist() == [
        "2024M01",
        "2024M06",
        "2024M12",
    ]

def test_time_period_operator_returns_whole_year():
    df = pd.DataFrame({
        "TIME_PERIOD": [
            "2023Q4",
            "2024Q1",
            "2024Q2",
            "2024Q3",
            "2024Q4",
            "2025Q1",
        ],
    })

    result, _ = (
        _apply_sdmx_operator_filters(
            df=df,
            filters={
                "TIME_PERIOD": {
                    "eq": "2024",
                }
            },
        )
    )

    assert result[
        "TIME_PERIOD"
    ].tolist() == [
        "2024Q1",
        "2024Q2",
        "2024Q3",
        "2024Q4",
    ]

def test_sdmx_time_period_annual():
    values = pd.Series([
        "2023",
        "2024",
    ])

    result = _format_sdmx_time_period(
        values
    )

    assert result.tolist() == [
        "2023",
        "2024",
    ]


def test_sdmx_time_period_quarterly():
    values = pd.Series([
        "2024Q1",
        "2024Q4",
    ])

    result = _format_sdmx_time_period(
        values
    )

    assert result.tolist() == [
        "2024-Q1",
        "2024-Q4",
    ]


def test_sdmx_time_period_monthly():
    values = pd.Series([
        "2024M01",
        "2024M12",
    ])

    result = _format_sdmx_time_period(
        values
    )

    assert result.tolist() == [
        "2024-M01",
        "2024-M12",
    ]

def test_sdmx_both_adds_dataset_level_labels():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        type="both",
    )

    assert "FREQ_LABEL" in df.columns
    assert "MEASURE_LABEL" in df.columns
    assert "UNIT_MEASURE_LABEL" in df.columns
    assert "UNIT_MULT_LABEL" in df.columns

    assert df["FREQ"].eq("A").all()
    assert df["FREQ_LABEL"].eq("Annual").all()

    assert df["MEASURE"].eq(
        "UNE_DEAP_RT"
    ).all()

    assert df["UNIT_MEASURE"].eq(
        "PT"
    ).all()

    assert df["UNIT_MEASURE_LABEL"].eq(
        "%"
    ).all()

    assert df["UNIT_MULT"].astype(str).eq(
        "0"
    ).all()

    assert df["UNIT_MULT_LABEL"].eq(
        "units"
    ).all()


def test_sdmx_source_label():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        type="both",
        filters={
            "SOURCE": "BA:148",
        },
    )

    assert "SOURCE_LABEL" in df.columns

    assert df["SOURCE"].eq(
        "BA:148"
    ).all()

    assert df["SOURCE_LABEL"].eq(
        "LFS - Employment Survey"
    ).all()


def test_sdmx_observation_status_label():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        type="both",
        best_source="all",
    )

    status = df.loc[
        df["OBS_STATUS"].notna(),
        [
            "OBS_STATUS",
            "OBS_STATUS_LABEL",
        ],
    ]

    assert not status.empty

    known = status[
        status["OBS_STATUS"].eq("B")
    ]

    if not known.empty:
        assert known[
            "OBS_STATUS_LABEL"
        ].eq(
            "Break in series"
        ).all()


def test_sdmx_note_labels():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        type="both",
        best_source="all",
    )

    assert "NOTE_SOURCE_LABEL" in df.columns
    assert "NOTE_INDICATOR_LABEL" in df.columns
    assert "NOTE_CLASSIF_LABEL" in df.columns

    notes = df.loc[
        df["NOTE_SOURCE"].eq(
            "R1:3513"
        )
    ]

    if not notes.empty:
        assert notes[
            "NOTE_SOURCE_LABEL"
        ].eq(
            "Repository: ILO-STATISTICS - "
            "Micro data processing"
        ).all()


def test_sdmx_drops_physical_indicator():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
    )

    assert "indicator" not in df.columns


def test_sdmx_column_order():
    df = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        type="both",
    )

    columns = list(
        df.columns
    )

    expected_order = [
        "STRUCTURE",
        "STRUCTURE_ID",
        "STRUCTURE_NAME",
        "ACTION",
        "REF_AREA",
        "REF_AREA_LABEL",
        "SOURCE",
        "SOURCE_LABEL",
        "FREQ",
        "FREQ_LABEL",
        "MEASURE",
        "MEASURE_LABEL",
        "SEX",
        "SEX_LABEL",
        "AGE",
        "AGE_LABEL",
        "TIME_PERIOD",
        "OBS_VALUE",
        "OBS_STATUS",
        "OBS_STATUS_LABEL",
        "UNIT_MEASURE",
        "UNIT_MEASURE_LABEL",
        "UNIT_MULT",
        "UNIT_MULT_LABEL",
        "NOTE_SOURCE",
        "NOTE_SOURCE_LABEL",
        "NOTE_INDICATOR",
        "NOTE_INDICATOR_LABEL",
        "NOTE_CLASSIF",
        "NOTE_CLASSIF_LABEL",
    ]

    positions = [
        columns.index(column)
        for column in expected_order
        if column in columns
    ]

    assert positions == sorted(
        positions
    )


def test_sdmx_best_source_column():
    default = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
    )

    all_sources = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        best_source="all",
    )

    non_best = ilostat.get_sdmx(
        "UNE_DEAP_SEX_AGE_RT_A",
        best_source="no",
    )

    assert "BEST_SOURCE" not in default.columns

    assert "BEST_SOURCE" in all_sources.columns
    assert "BEST_SOURCE" in non_best.columns

    assert all_sources.columns[-1] == (
        "BEST_SOURCE"
    )

    assert non_best.columns[-1] == (
        "BEST_SOURCE"
    )

def test_sdmx_structure():
    df = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        type="both",
    )

    assert isinstance(
        df,
        pd.DataFrame,
    )

    assert not df.empty

    assert list(df["COMPONENT_ID"]) == [
        "REF_AREA",
        "SOURCE",
        "FREQ",
        "MEASURE",
        "SEX",
        "AGE",
        "TIME_PERIOD",
        "OBS_VALUE",
        "OBS_STATUS",
        "UNIT_MEASURE",
        "UNIT_MULT",
        "NOTE_SOURCE",
        "NOTE_INDICATOR",
        "NOTE_CLASSIF",
        "BEST_SOURCE",
    ]


def test_sdmx_structure_roles():
    df = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        type="both",
    )

    roles = dict(
        zip(
            df["COMPONENT_ID"],
            df["ROLE"],
            strict=True,
        )
    )

    assert roles["REF_AREA"] == "dimension"
    assert roles["SOURCE"] == "dimension"
    assert roles["TIME_PERIOD"] == "dimension"
    assert roles["OBS_VALUE"] == "measure"
    assert roles["OBS_STATUS"] == "attribute"
    assert roles["BEST_SOURCE"] == "attribute"


def test_sdmx_structure_code():
    df = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        type="code",
    )

    assert "COMPONENT_ID" in df.columns
    assert "COMPONENT_NAME" not in df.columns


def test_sdmx_structure_label():
    df = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        type="label",
    )

    assert "COMPONENT_ID" not in df.columns
    assert "COMPONENT_NAME" in df.columns


def test_sdmx_structure_label_short():
    df = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        type="label_short",
    )

    assert "COMPONENT_ID" not in df.columns
    assert "COMPONENT_NAME" in df.columns


def test_sdmx_structure_french():
    df = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        type="both",
        lang="fr",
        refresh=True,
    )

    names = dict(
        zip(
            df["COMPONENT_ID"],
            df["COMPONENT_NAME"],
            strict=True,
        )
    )

    assert names["REF_AREA"] == "Zone de référence"
    assert names["FREQ"] == "Fréquence"
    assert names["MEASURE"] == "Mesure"
    assert names["SEX"] == "Sexe"
    assert names["AGE"] == "Âge"

def test_sdmx_structure_dataframe_format():
    df = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        format="dataframe",
        type="both",
    )

    assert isinstance(
        df,
        pd.DataFrame,
    )

    assert not df.empty

def test_sdmx_invalid_format():
    import pytest

    with pytest.raises(
        ValueError,
        match="Invalid format value",
    ):
        ilostat.get_sdmx(
            "UNE_TUNE_SEX_AGE_NB_A",
            resource="structure",
            format="invalid",
        )

def test_sdmx_structure_codelists():
    df = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        type="both",
    )

    codelists = dict(
        zip(
            df["COMPONENT_ID"],
            df["CODELIST"],
            strict=True,
        )
    )

    assert codelists["REF_AREA"] == "cl_ref_area"
    assert codelists["SOURCE"] == "cl_source"
    assert codelists["FREQ"] == "cl_freq"
    assert codelists["MEASURE"] == "cl_measure"
    assert codelists["SEX"] == "cl_sex"
    assert codelists["AGE"] == "cl_age"
    assert pd.isna(
        codelists["TIME_PERIOD"]
    )
    assert pd.isna(
        codelists["OBS_VALUE"]
    )
    assert codelists["OBS_STATUS"] == "cl_obs_status"
    assert codelists["UNIT_MEASURE"] == "cl_unit_measure"
    assert codelists["UNIT_MULT"] == "cl_unit_mult"
    assert codelists["NOTE_SOURCE"] == "cl_note_source"
    assert codelists["NOTE_INDICATOR"] == "cl_note_indicator"
    assert codelists["NOTE_CLASSIF"] == "cl_note_classif"
    assert codelists["BEST_SOURCE"] == "cl_best_source"

def test_build_sdmx_structure_model():
    meta = ilostat.get_metadata(
        "UNE_TUNE_SEX_AGE_NB_A",
    )

    model = _build_sdmx_structure_model(
        dataset_id="UNE_TUNE_SEX_AGE_NB_A",
        meta=meta,
    )

    assert model["id"] == "UNE_TUNE_SEX_AGE_NB_A"
    assert model["agency"] == "ILO"
    assert model["version"] == "1.0"

    components = {
        component["id"]: component
        for component in model["components"]
    }

    assert components["REF_AREA"]["position"] == 1
    assert components["REF_AREA"]["codelist"] == "cl_ref_area"

    assert components["AGE"]["codelist"] == "cl_age"

    assert components["TIME_PERIOD"]["codelist"] is None
    assert components["TIME_PERIOD"]["representation"] == "time"

    assert components["OBS_VALUE"]["role"] == "measure"
    assert components["OBS_VALUE"]["codelist"] is None

    assert components["BEST_SOURCE"]["codelist"] == "cl_best_source"    

def test_sdmx_ml_time_dimension():
    xml = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        format="sdmx-ml",
    )

    assert (
        '<str:TimeDimension id="TIME_PERIOD">'
        in xml
    )

    assert (
        'textType="ObservationalTimePeriod"'
        in xml
    )

def test_sdmx_ml_attribute_relationships():
    xml = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        format="sdmx-ml",
    )

    assert xml.count(
        "<str:AttributeRelationship>"
    ) == 7

    assert xml.count(
        "<str:Observation"
    ) == 7

def test_sdmx_ml_concept_scheme():
    xml = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        format="sdmx-ml",
    )

    assert (
        'id="CS_UNE_TUNE_SEX_AGE_NB_A"'
        in xml
    )

    assert (
        '<str:Concept id="REF_AREA">'
        in xml
    )

    assert (
        '<com:Name xml:lang="en">'
        'Reference area'
        '</com:Name>'
        in xml
    )

    assert (
        '<str:Concept id="OBS_VALUE">'
        in xml
    )

    assert (
        '<str:Concept id="BEST_SOURCE">'
        in xml
    )

def test_sdmx_ml_structure_xml():
    import xml.etree.ElementTree as ET

    xml = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        format="sdmx-ml",
    )

    root = ET.fromstring(
        xml
    )

    assert root.tag == (
        "{http://www.sdmx.org/resources/"
        "sdmxml/schemas/v3_1/message}"
        "Structure"
    )

def test_sdmx_ml_concept_scheme_xml():
    import xml.etree.ElementTree as ET

    xml = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        format="sdmx-ml",
    )

    root = ET.fromstring(
        xml
    )

    namespaces = {
        "str": (
            "http://www.sdmx.org/resources/"
            "sdmxml/schemas/v3_1/structure"
        ),
    }

    concept_scheme = root.find(
        ".//str:ConceptScheme",
        namespaces,
    )

    assert concept_scheme is not None

    assert (
        concept_scheme.get("id")
        == "CS_UNE_TUNE_SEX_AGE_NB_A"
    )
def test_sdmx_json_validates_against_sdmx_21_schema():
    import json
    from pathlib import Path

    from jsonschema import Draft7Validator

    text = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        format="sdmx-json",
    )

    document = json.loads(
        text
    )

    schema_path = (
        Path(__file__).parent
        / "schemas"
        / "sdmx-json-structure-schema.json"
    )

    schema = json.loads(
        schema_path.read_text(
            encoding="utf-8"
        )
    )

    validator = Draft7Validator(
        schema
    )

    errors = list(
        validator.iter_errors(
            document
        )
    )

    assert not errors

def test_sdmx_json_structure():
    import json

    text = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="structure",
        format="sdmx-json",
    )

    message = json.loads(
        text
    )

    dsd = message["data"][
        "dataStructures"
    ][0]

    assert (
        dsd["id"]
        == "UNE_TUNE_SEX_AGE_NB_A"
    )

    components = dsd[
        "dataStructureComponents"
    ]

    dimensions = components[
        "dimensionList"
    ]["dimensions"]

    assert [
        dimension["id"]
        for dimension in dimensions
    ] == [
        "REF_AREA",
        "SOURCE",
        "FREQ",
        "MEASURE",
        "SEX",
        "AGE",
    ]

    assert (
        components["dimensionList"]
        ["timeDimension"]["id"]
        == "TIME_PERIOD"
    )

    assert (
        components["measureList"]
        ["measures"][0]["id"]
        == "OBS_VALUE"
    )

def test_sdmx_codelist_age():
    out = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="codelist",
        component="AGE",
    )

    assert list(out.columns) == [
        "age",
        "age.label",
    ]

    assert len(out) == 41


def test_sdmx_codelist_ref_area():
    out = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="codelist",
        component="REF_AREA",
    )

    assert list(out.columns) == [
        "ref_area",
        "ref_area.label",
    ]


def test_sdmx_codelist_language():
    out = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="codelist",
        component="AGE",
        lang="fr",
    )

    assert list(out.columns) == [
        "age",
        "age.label",
    ]


def test_sdmx_codelist_requires_component():
    with pytest.raises(
        ValueError,
        match="component is required",
    ):
        ilostat.get_sdmx(
            "UNE_TUNE_SEX_AGE_NB_A",
            resource="codelist",
        )


def test_sdmx_codelist_non_coded_component():
    with pytest.raises(
        ValueError,
        match="does not use a codelist",
    ):
        ilostat.get_sdmx(
            "UNE_TUNE_SEX_AGE_NB_A",
            resource="codelist",
            component="TIME_PERIOD",
        )

def test_sdmx_codelist_sdmx_ml_validates_against_sdmx_31_schema():
    from pathlib import Path

    from lxml import etree

    xml = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="codelist",
        component="AGE",
        format="sdmx-ml",
    )

    schema_path = (
        Path(__file__).parent
        / "schemas"
        / "sdmx31"
        / "schemas"
        / "SDMXMessage.xsd"
    )

    schema = etree.XMLSchema(
        etree.parse(str(schema_path))
    )

    document = etree.fromstring(
        xml.encode("utf-8")
    )

    schema.assertValid(document)

def test_sdmx_codelist_sdmx_json_validates_against_sdmx_21_schema():
    import json
    from pathlib import Path

    from jsonschema import Draft7Validator

    text = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="codelist",
        component="AGE",
        format="sdmx-json",
    )

    document = json.loads(text)

    schema_path = (
        Path(__file__).parent
        / "schemas"
        / "sdmx-json-structure-schema.json"
    )

    schema = json.loads(
        schema_path.read_text(
            encoding="utf-8"
        )
    )

    validator = Draft7Validator(schema)

    errors = list(
        validator.iter_errors(document)
    )

    assert not errors

def test_sdmx_dataflow():
    out = ilostat.get_sdmx(
        resource="dataflow",
    )

    assert list(out.columns) == [
        "DATAFLOW_ID",
        "DATAFLOW_NAME",
        "LAST_UPDATE",
    ]

    assert not out.empty


def test_sdmx_dataflow_dataset():
    out = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="dataflow",
    )

    assert len(out) == 1

    assert (
        out.iloc[0]["DATAFLOW_ID"]
        == "UNE_TUNE_SEX_AGE_NB_A"
    )

    assert (
        "Annual"
        in out.iloc[0]["DATAFLOW_NAME"]
    )


def test_sdmx_dataflow_french():
    out = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="dataflow",
        lang="fr",
    )

    assert len(out) == 1
    assert out.iloc[0]["DATAFLOW_NAME"]

def test_sdmx_dataset_id_required():
    with pytest.raises(
        ValueError,
        match="dataset_id is required",
    ):
        ilostat.get_sdmx(
            resource="structure",
        )

def test_sdmx_dataflow_sdmx_ml_validates_against_sdmx_31_schema():
    from pathlib import Path

    from lxml import etree

    xml = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="dataflow",
        format="sdmx-ml",
    )

    schema_path = (
        Path(__file__).parent
        / "schemas"
        / "sdmx31"
        / "schemas"
        / "SDMXMessage.xsd"
    )

    schema = etree.XMLSchema(
        etree.parse(str(schema_path))
    )

    document = etree.fromstring(
        xml.encode("utf-8")
    )

    schema.assertValid(document)

def test_sdmx_dataflow_sdmx_json_validates_against_sdmx_21_schema():
    import json
    from pathlib import Path

    from jsonschema import Draft7Validator

    text = ilostat.get_sdmx(
        "UNE_TUNE_SEX_AGE_NB_A",
        resource="dataflow",
        format="sdmx-json",
    )

    document = json.loads(text)

    schema_path = (
        Path(__file__).parent
        / "schemas"
        / "sdmx-json-structure-schema.json"
    )

    schema = json.loads(
        schema_path.read_text(
            encoding="utf-8"
        )
    )

    validator = Draft7Validator(schema)

    errors = list(
        validator.iter_errors(document)
    )

    assert not errors