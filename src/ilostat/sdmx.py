from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .data import get_df
from .dictionary import get_dic
from .metadata import get_metadata, get_toc

VALID_RESOURCES = {
    "data",
    "structure",
    "codelist",
    "dataflow",
}

VALID_TYPES = {
    "code",
    "label",
    "label_short",
    "both",
}

SDMX_COMPONENT_NAMES = {
    "SOURCE": {
        "en": "Source",
        "fr": "Source",
        "es": "Fuente",
    },
    "FREQ": {
        "en": "Frequency",
        "fr": "Fréquence",
        "es": "Frecuencia",
    },
    "MEASURE": {
        "en": "Measure",
        "fr": "Mesure",
        "es": "Medida",
    },
    "TIME_PERIOD": {
        "en": "Time period",
        "fr": "Période",
        "es": "Período",
    },
    "OBS_VALUE": {
        "en": "Observation value",
        "fr": "Valeur observée",
        "es": "Valor observado",
    },
    "OBS_STATUS": {
        "en": "Observation status",
        "fr": "Statut de l'observation",
        "es": "Estado de la observación",
    },
    "UNIT_MEASURE": {
        "en": "Unit of measure",
        "fr": "Unité de mesure",
        "es": "Unidad de medida",
    },
    "UNIT_MULT": {
        "en": "Multiplier",
        "fr": "Multiplicateur",
        "es": "Multiplicador",
    },
    "NOTE_SOURCE": {
        "en": "Source note",
        "fr": "Note sur la source",
        "es": "Nota sobre la fuente",
    },
    "NOTE_INDICATOR": {
        "en": "Indicator note",
        "fr": "Note sur l'indicateur",
        "es": "Nota sobre el indicador",
    },
    "NOTE_CLASSIF": {
        "en": "Classification note",
        "fr": "Note sur la classification",
        "es": "Nota sobre la clasificación",
    },
    "BEST_SOURCE": {
        "en": "Best source",
        "fr": "Meilleure source",
        "es": "Mejor fuente",
    },
}

def get_sdmx(
    dataset_id: str | None = None,
    resource: str = "data",
    component: str | None = None,
    segment: str = "indicator",
    type: str = "code",
    format: str = "dataframe",
    lang: str = "en",
    filters: dict | None = None,
    best_source: str = "yes",
    fixed: bool = True,
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> pd.DataFrame | str:
    """
    Retrieve ILOSTAT resources using SDMX conventions.

    Parameters
    ----------
    dataset_id : str or None, default None
        ILOSTAT dataset identifier.

        Required for data, structure, and codelist resources.
        For resource="dataflow", None returns the complete
        dataflow catalogue and a dataset identifier returns
        the corresponding dataflow.

    resource : {"data", "structure", "codelist", "dataflow"}, default "data"
        SDMX resource to retrieve.

    component : str or None, default None
        SDMX component identifier used when resource="codelist",
        for example "REF_AREA", "SEX", or "AGE".

    segment : str, default "indicator"
        ILOSTAT bulk-data segment.

    type : {"code", "label", "label_short", "both"}, default "code"
        Output representation used for DataFrame resources.

        "code" returns codes only.

        "label" returns localized full labels.

        "label_short" returns localized compact labels for
        classification dimensions when available.

        "both" returns codes together with localized full labels.

        This option does not modify SDMX-ML or SDMX-JSON
        serializations.

    format : {"dataframe", "sdmx-ml", "sdmx-json"}, default "dataframe"
        Output format.

        "dataframe" returns a pandas DataFrame.

        "sdmx-ml" returns SDMX-ML output where supported.

        "sdmx-json" returns SDMX-JSON output where supported.

    lang : {"en", "fr", "es"}, default "en"
        Language used for labels and dataflow names.

    filters : dict or None, default None
        Filters applied when resource="data".

    best_source : {"yes", "no", "all"}, default "yes"
        Select best-source observations when resource="data".

    fixed : bool, default True
        If True, treat filter values as literal strings when
        resource="data".

    cache_dir : str, pathlib.Path or None, default None
        Directory used to cache downloaded files.

    refresh : bool, default False
        If True, refresh the relevant resources before checking
        cached data.

    Returns
    -------
    pandas.DataFrame or str
        Requested SDMX-oriented resource. SDMX-ML and
        SDMX-JSON serializations are returned as strings.
    """

    resource = resource.lower()
    type = type.lower()

    format = format.lower()

    if format not in {
        "dataframe",
        "sdmx-ml",
        "sdmx-json",
    }:
        raise ValueError(
            "Invalid format value. "
            "Choose from 'dataframe', 'sdmx-ml', "
            "or 'sdmx-json'."
        )

    if resource not in VALID_RESOURCES:
        raise ValueError(
            "Invalid resource value. "
            "Choose from 'data', 'structure', 'codelist', or 'dataflow'."
        )

    if type not in VALID_TYPES:
        raise ValueError(
            "Invalid type value. "
            "Choose from 'code', 'label', 'label_short', or 'both'."
        )

    if resource == "codelist":
        return _get_sdmx_codelist(
            dataset_id=dataset_id,
            segment=segment,
            component=component,
            format=format,
            lang=lang,
            cache_dir=cache_dir,
            refresh=refresh,
        )

    if (
        resource != "dataflow"
        and dataset_id is None
    ):
        raise ValueError(
            "dataset_id is required when "
            f"resource='{resource}'."
        )

    if resource == "dataflow":
        return _get_sdmx_dataflow(
            dataset_id=dataset_id,
            segment=segment,
            format=format,
            lang=lang,
            cache_dir=cache_dir,
            refresh=refresh,
        )

    if resource == "data":
        return _get_sdmx_data(
            dataset_id=dataset_id,
            segment=segment,
            type=type,
            lang=lang,
            filters=filters,
            best_source=best_source,
            fixed=fixed,
            cache_dir=cache_dir,
            refresh=refresh,
        )

    if resource == "structure":
        return _get_sdmx_structure(
            dataset_id=dataset_id,
            segment=segment,
            type=type,
            format=format,
            lang=lang,
            cache_dir=cache_dir,
            refresh=refresh,
        )

    raise NotImplementedError(
        f"SDMX resource '{resource}' is not implemented yet."
    )

def _get_sdmx_dataflow(
    dataset_id: str | None,
    segment: str,
    format: str,
    lang: str,
    cache_dir: str | Path | None,
    refresh: bool,
) -> pd.DataFrame:
    """
    Retrieve ILOSTAT dataflows using SDMX conventions.
    """

    toc = get_toc(
        segment=segment,
        lang=lang,
        cache_dir=cache_dir,
        refresh=refresh,
    )

    if dataset_id is not None:
        toc = toc.loc[
            toc["id"] == dataset_id
        ].copy()

        if toc.empty:
            raise ValueError(
                f"Dataset '{dataset_id}' was not found "
                f"in the '{segment}' table of contents."
            )

    out = pd.DataFrame(
        {
            "DATAFLOW_ID": toc["id"],
            "DATAFLOW_NAME": (
                toc["indicator.label"]
                + " - "
                + toc["freq.label"]
            ),
            "LAST_UPDATE": toc["last.update"],
        }
    )

    if format == "dataframe":
        return out.reset_index(
            drop=True
        )

    if format == "sdmx-ml":
        return _to_sdmx_ml_dataflow(
            data=out,
            lang=lang,
        )

    if format == "sdmx-json":
        return _to_sdmx_json_dataflow(
            data=out,
            lang=lang,
        )

    raise ValueError(
        f"Unsupported SDMX dataflow format '{format}'."
    )

def _to_sdmx_json_dataflow(
    data: pd.DataFrame,
    lang: str,
) -> str:
    """
    Serialize ILOSTAT dataflows as SDMX-JSON 2.1.
    """

    dataflows = []

    for _, row in data.iterrows():
        dataflow_id = str(
            row["DATAFLOW_ID"]
        )

        dataflow_name = str(
            row["DATAFLOW_NAME"]
        )

        dataflows.append(
            {
                "id": dataflow_id,
                "version": "1.0",
                "agencyID": "ILO",
                "name": dataflow_name,
                "names": {
                    lang: dataflow_name,
                },
                "structure": (
                    "urn:sdmx:org.sdmx.infomodel."
                    "datastructure.DataStructure="
                    f"ILO:{dataflow_id}(1.0)"
                ),
            }
        )

    message = {
        "$schema": (
            "https://json.sdmx.org/2.1/"
            "sdmx-json-structure-schema.json"
        ),
        "meta": {
            "id": "ILOSTAT_DATAFLOWS",
            "test": False,
            "contentLanguages": [
                lang,
            ],
            "sender": {
                "id": "ILO",
            },
        },
        "data": {
            "dataflows": dataflows,
        },
    }

    return json.dumps(
        message,
        ensure_ascii=False,
        indent=2,
    )

def _to_sdmx_ml_dataflow(
    data: pd.DataFrame,
    lang: str,
) -> str:
    """
    Serialize ILOSTAT dataflows as SDMX-ML 3.1.
    """

    namespaces = {
        "mes": (
            "http://www.sdmx.org/resources/"
            "sdmxml/schemas/v3_1/message"
        ),
        "str": (
            "http://www.sdmx.org/resources/"
            "sdmxml/schemas/v3_1/structure"
        ),
        "com": (
            "http://www.sdmx.org/resources/"
            "sdmxml/schemas/v3_1/common"
        ),
    }

    for prefix, uri in namespaces.items():
        ET.register_namespace(
            prefix,
            uri,
        )

    root = ET.Element(
        ET.QName(
            namespaces["mes"],
            "Structure",
        )
    )

    # ----------------------------------------------------------
    # Header
    # ----------------------------------------------------------

    header = ET.SubElement(
        root,
        ET.QName(
            namespaces["mes"],
            "Header",
        ),
    )

    ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "ID",
        ),
    ).text = "ILOSTAT_DATAFLOWS"

    ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "Test",
        ),
    ).text = "false"

    ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "Prepared",
        ),
    ).text = (
        datetime.now(timezone.utc)
        .isoformat(
            timespec="seconds"
        )
        .replace(
            "+00:00",
            "Z",
        )
    )

    sender = ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "Sender",
        ),
        {
            "id": "ILO",
        },
    )

    ET.SubElement(
        sender,
        ET.QName(
            namespaces["com"],
            "Name",
        ),
        {
            "{http://www.w3.org/XML/1998/namespace}lang": "en",
        },
    ).text = (
        "International Labour Organization"
    )

    # ----------------------------------------------------------
    # Structures / Dataflows
    # ----------------------------------------------------------

    structures = ET.SubElement(
        root,
        ET.QName(
            namespaces["mes"],
            "Structures",
        ),
    )

    dataflows = ET.SubElement(
        structures,
        ET.QName(
            namespaces["str"],
            "Dataflows",
        ),
    )

    for _, row in data.iterrows():

        dataflow_id = str(
            row["DATAFLOW_ID"]
        )

        dataflow_name = str(
            row["DATAFLOW_NAME"]
        )

        dataflow = ET.SubElement(
            dataflows,
            ET.QName(
                namespaces["str"],
                "Dataflow",
            ),
            {
                "id": dataflow_id,
                "agencyID": "ILO",
                "version": "1.0",
            },
        )

        ET.SubElement(
            dataflow,
            ET.QName(
                namespaces["com"],
                "Name",
            ),
            {
                "{http://www.w3.org/XML/1998/namespace}lang": lang,
            },
        ).text = dataflow_name

        structure = ET.SubElement(
            dataflow,
            ET.QName(
                namespaces["str"],
                "Structure",
            ),
        )

        structure.text = (
            "urn:sdmx:org.sdmx.infomodel."
            "datastructure.DataStructure="
            f"ILO:{dataflow_id}(1.0)"
        )

    ET.indent(
        root,
        space="  ",
    )

    return ET.tostring(
        root,
        encoding="unicode",
        xml_declaration=False,
    )

def _get_sdmx_codelist(
    dataset_id: str,
    segment: str,
    component: str | None,
    format: str,
    lang: str,
    cache_dir: str | Path | None,
    refresh: bool,
):
    """
    Retrieve the codelist associated with an SDMX
    component of an ILOSTAT dataset.
    """
        
    if component is None:
        raise ValueError(
            "component is required when "
            "resource='codelist'."
        )

    meta = get_metadata(
        dataset_id=dataset_id,
        segment=segment,
        cache_dir=cache_dir,
        refresh=refresh,
    )

    model = _build_sdmx_structure_model(
        dataset_id=dataset_id,
        meta=meta,
        lang=lang,
    )

    component_id = component.upper()

    match = next(
        (
            item
            for item in model["components"]
            if item["id"] == component_id
        ),
        None,
    )

    if match is None:
        raise ValueError(
            f"Unknown SDMX component "
            f"'{component_id}' for dataset "
            f"'{dataset_id}'."
        )

    codelist = match["codelist"]

    if codelist is None:
        raise ValueError(
            f"SDMX component '{component_id}' "
            "does not use a codelist."
        )

    out = get_dic(
        codelist,
        lang=lang,
        cache_dir=cache_dir,
        refresh=refresh,
    )

    target = component_id.lower()

    if len(out.columns) >= 2:
        out = out.rename(
            columns={
                out.columns[0]: target,
                out.columns[1]: f"{target}.label",
            }
        )

    if format == "dataframe":
        return out

    if format == "sdmx-ml":
        return _to_sdmx_ml_codelist(
            data=out,
            component_id=component_id,
            codelist=codelist,
            lang=lang,
        )

    if format == "sdmx-json":
        return _to_sdmx_json_codelist(
            data=out,
            component_id=component_id,
            codelist=codelist,
            lang=lang,
        )

    raise ValueError(
        f"Unsupported SDMX codelist format '{format}'."
    )

def _to_sdmx_json_codelist(
    data: pd.DataFrame,
    component_id: str,
    codelist: str,
    lang: str,
) -> str:
    """
    Serialize an ILOSTAT codelist as SDMX-JSON 2.1.
    """

    code_column = component_id.lower()
    label_column = f"{code_column}.label"

    codes = []

    for _, row in data.iterrows():
        code = str(
            row[code_column]
        )

        label = str(
            row[label_column]
        )

        codes.append(
            {
                "id": code,
                "name": label,
                "names": {
                    lang: label,
                },
            }
        )

    codelist_name = (
        f"{component_id} codelist"
    )

    message = {
        "$schema": (
            "https://json.sdmx.org/2.1/"
            "sdmx-json-structure-schema.json"
        ),
        "meta": {
            "id": (
                f"CODELIST_{component_id}"
            ),
            "test": False,
            "contentLanguages": [
                lang,
            ],
            "sender": {
                "id": "ILO",
            },
        },
        "data": {
            "codelists": [
                {
                    "id": codelist.upper(),
                    "version": "1.0",
                    "agencyID": "ILO",
                    "name": codelist_name,
                    "names": {
                        lang: codelist_name,
                    },
                    "codes": codes,
                }
            ],
        },
    }

    return json.dumps(
        message,
        ensure_ascii=False,
        indent=2,
    )

def _to_sdmx_ml_codelist(
    data: pd.DataFrame,
    component_id: str,
    codelist: str,
    lang: str,
) -> str:
    """
    Serialize an ILOSTAT codelist as SDMX-ML 3.1.
    """

    namespaces = {
        "mes": (
            "http://www.sdmx.org/resources/"
            "sdmxml/schemas/v3_1/message"
        ),
        "str": (
            "http://www.sdmx.org/resources/"
            "sdmxml/schemas/v3_1/structure"
        ),
        "com": (
            "http://www.sdmx.org/resources/"
            "sdmxml/schemas/v3_1/common"
        ),
    }

    for prefix, uri in namespaces.items():
        ET.register_namespace(
            prefix,
            uri,
        )

    root = ET.Element(
        ET.QName(
            namespaces["mes"],
            "Structure",
        )
    )

    # ----------------------------------------------------------
    # Header
    # ----------------------------------------------------------

    header = ET.SubElement(
        root,
        ET.QName(
            namespaces["mes"],
            "Header",
        ),
    )

    ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "ID",
        ),
    ).text = (
        f"CODELIST_{component_id}"
    )

    ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "Test",
        ),
    ).text = "false"

    ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "Prepared",
        ),
    ).text = (
        datetime.now(timezone.utc)
        .isoformat(
            timespec="seconds"
        )
        .replace(
            "+00:00",
            "Z",
        )
    )

    sender = ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "Sender",
        ),
        {
            "id": "ILO",
        },
    )

    ET.SubElement(
        sender,
        ET.QName(
            namespaces["com"],
            "Name",
        ),
        {
            "{http://www.w3.org/XML/1998/namespace}lang": "en",
        },
    ).text = (
        "International Labour Organization"
    )

    # ----------------------------------------------------------
    # Structures / Codelists
    # ----------------------------------------------------------

    structures = ET.SubElement(
        root,
        ET.QName(
            namespaces["mes"],
            "Structures",
        ),
    )

    codelists = ET.SubElement(
        structures,
        ET.QName(
            namespaces["str"],
            "Codelists",
        ),
    )

    codelist_element = ET.SubElement(
        codelists,
        ET.QName(
            namespaces["str"],
            "Codelist",
        ),
        {
            "id": codelist.upper(),
            "agencyID": "ILO",
            "version": "1.0",
        },
    )

    ET.SubElement(
        codelist_element,
        ET.QName(
            namespaces["com"],
            "Name",
        ),
        {
            "{http://www.w3.org/XML/1998/namespace}lang": lang,
        },
    ).text = f"{component_id} codelist"

    # ----------------------------------------------------------
    # Codes
    # ----------------------------------------------------------

    code_column = component_id.lower()
    label_column = f"{code_column}.label"

    for _, row in data.iterrows():
        code = ET.SubElement(
            codelist_element,
            ET.QName(
                namespaces["str"],
                "Code",
            ),
            {
                "id": str(
                    row[code_column]
                ),
            },
        )

        ET.SubElement(
            code,
            ET.QName(
                namespaces["com"],
                "Name",
            ),
            {
                "{http://www.w3.org/XML/1998/namespace}lang": lang,
            },
        ).text = str(
            row[label_column]
        )

    ET.indent(
        root,
        space="  ",
    )

    return ET.tostring(
        root,
        encoding="unicode",
        xml_declaration=False,
    )

def _get_sdmx_data(
    dataset_id: str,
    segment: str,
    type: str,
    lang: str,
    filters: dict | None,
    best_source: str,
    fixed: bool,
    cache_dir: str | Path | None,
    refresh: bool,
) -> pd.DataFrame:
    """
    Retrieve ILOSTAT observations and transform them
    to SDMX conventions.
    """

    meta = get_metadata(
        dataset_id=dataset_id,
        segment=segment,
        cache_dir=cache_dir,
        refresh=refresh,
    )

    # Separate ordinary filters from SDMX operator filters.
    #
    # Example:
    #
    # REF_AREA = FRA
    #
    # is a simple filter, while:
    #
    # TIME_PERIOD = {"ge": "2020", "le": "2024"}
    #
    # is an operator filter.
    simple_filters, operator_filters = (
        _split_sdmx_filters(
            filters
        )
    )

    # FREQ and MEASURE are constant SDMX dimensions
    # stored in metadata rather than physical columns.
    data_filters, constants_match = (
        _extract_constant_filters(
            filters=simple_filters,
            meta=meta,
        )
    )

    # Translate SDMX component names to the physical
    # ILOSTAT column names expected by get_df().
    #
    # Examples:
    #
    # REF_AREA -> ref_area
    # SEX      -> sex
    # AGE      -> classif1
    data_filters = _translate_sdmx_filters(
        filters=data_filters,
        meta=meta,
    )

    # Always retrieve codes from get_df().
    #
    # SDMX labels are added after the semantic dimensions
    # (AGE, ECO, OCU, etc.) have been resolved from metadata.
    df = get_df(
        dataset_id=dataset_id,
        segment=segment,
        type="code",
        lang=lang,
        filters=data_filters,
        best_source=best_source,
        fixed=fixed,
        cache_dir=cache_dir,
        refresh=refresh,
    )

    # A non-matching constant filter represents a valid
    # SDMX query with no matching observations.
    if not constants_match:
        df = df.iloc[0:0].copy()

    # Convert the physical ILOSTAT representation to
    # the SDMX-oriented representation.
    out = _to_sdmx_data(
        df=df,
        meta=meta,
        type=type,
        lang=lang,
    )

    # Operator filters are applied after transformation,
    # so they operate on SDMX component names such as
    # TIME_PERIOD.
    out, _ = _apply_sdmx_operator_filters(
        df=out,
        filters=operator_filters,
    )

    return out.reset_index(
        drop=True
    )

def _get_sdmx_structure(
    dataset_id: str,
    segment: str,
    type: str,
    format: str,
    lang: str,
    cache_dir: str | Path | None,
    refresh: bool,
):
    """
    Retrieve the SDMX structure associated with an
    ILOSTAT dataset.
    """

    meta = get_metadata(
        dataset_id=dataset_id,
        segment=segment,
        cache_dir=cache_dir,
        refresh=refresh,
    )

    if format == "dataframe":
        return _to_sdmx_structure(
            meta=meta,
            type=type,
            lang=lang,
        )

    if format == "sdmx-ml":
        model = _build_sdmx_structure_model(
            dataset_id=dataset_id,
            meta=meta,
            lang=lang,
        )

        return _to_sdmx_ml_structure(
            model=model,
            meta=meta,
            lang=lang,
        )
        
    if format == "sdmx-json":
        model = _build_sdmx_structure_model(
            dataset_id=dataset_id,
            meta=meta,
            lang=lang,
        )

        return _to_sdmx_json_structure(
            model=model,
            meta=meta,
            lang=lang,
        )


    raise ValueError(
        f"Unsupported SDMX structure format '{format}'."
    )

def _to_sdmx_json_structure(
    model: dict,
    meta: dict,
    lang: str,
) -> str:
    """
    Serialize an internal ILOSTAT SDMX structure model
    as SDMX-JSON Structure 2.1.
    """
    dimensions = []
    attributes = []
    measures = []
    time_dimension = None

    for component in model["components"]:

        concept_urn = (
            "urn:sdmx:org.sdmx.infomodel."
            "conceptscheme.Concept="
            f"{model['agency']}:"
            f"{model['concept_scheme']}"
            f"({model['version']})."
            f"{component['id']}"
        )

        item = {
            "id": component["id"],
            "conceptIdentity": concept_urn,
        }

        # ------------------------------------------------------
        # Coded representation
        # ------------------------------------------------------

        if component["codelist"] is not None:
            item["localRepresentation"] = {
                "enumeration": (
                    "urn:sdmx:org.sdmx.infomodel."
                    "codelist.Codelist="
                    f"{model['agency']}:"
                    f"{component['codelist'].upper()}"
                    f"({model['version']})"
                )
            }

        # ------------------------------------------------------
        # Dimensions
        # ------------------------------------------------------

        if component["role"] == "dimension":

            if component["id"] == "TIME_PERIOD":
                item["localRepresentation"] = {
                    "format": {
                        "dataType": (
                            "ObservationalTimePeriod"
                        )
                    }
                }

                time_dimension = item

            else:
                item["position"] = component[
                    "position"
                ]

                dimensions.append(
                    item
                )

        # ------------------------------------------------------
        # Measure
        # ------------------------------------------------------

        elif component["role"] == "measure":
            measures.append(
                item
            )

        # ------------------------------------------------------
        # Attributes
        # ------------------------------------------------------

        elif component["role"] == "attribute":
            item["usage"] = "optional"

            item["attributeRelationship"] = {
                "observation": {}
            }

            attributes.append(
                item
            )

    # ----------------------------------------------------------
    # Concepts
    # ----------------------------------------------------------

    concepts = [
        {
            "id": component["id"],
            "name": component["name"],
            "names": {
                lang: component["name"],
            },
        }
        for component in model["components"]
    ]

    # ----------------------------------------------------------
    # Message
    # ----------------------------------------------------------

    message = {
        "$schema": (
            "https://json.sdmx.org/2.1/"
            "sdmx-json-structure-schema.json"
        ),
        "meta": {
            "id": (
                f"STRUCTURE_{model['id']}"
            ),
            "test": False,
            "contentLanguages": [
                lang,
            ],
            "sender": {
                "id": model["agency"],
            },
        },
        "data": {
            "dataStructures": [
                {
                    "id": model["id"],
                    "version": model["version"],
                    "agencyID": model["agency"],
                    "name": (
                        f"Data structure for "
                        f"{model['id']}"
                    ),
                    "names": {
                        lang: (
                            f"Data structure for "
                            f"{model['id']}"
                        ),
                    },
                    "dataStructureComponents": {
                        "attributeList": {
                            "id": (
                                "AttributeDescriptor"
                            ),
                            "attributes": attributes,
                        },
                        "dimensionList": {
                            "id": (
                                "DimensionDescriptor"
                            ),
                            "dimensions": dimensions,
                            "timeDimension": (
                                time_dimension
                            ),
                        },
                        "measureList": {
                            "id": (
                                "MeasureDescriptor"
                            ),
                            "measures": measures,
                        },
                    },
                }
            ],
            "conceptSchemes": [
                {
                    "id": model[
                        "concept_scheme"
                    ],
                    "version": model[
                        "version"
                    ],
                    "agencyID": model[
                        "agency"
                    ],
                    "name": (
                        f"Concept scheme for "
                        f"{model['id']}"
                    ),
                    "names": {
                        lang: (
                            f"Concept scheme for "
                            f"{model['id']}"
                        ),
                    },
                    "concepts": concepts,
                }
            ],
        },
    }

    return json.dumps(
        message,
        ensure_ascii=False,
        indent=2,
    )

def _to_sdmx_ml_structure(
    model: dict,
    meta: dict,
    lang: str,
) -> str:
    """
    Serialize an internal ILOSTAT SDMX structure model
    as SDMX-ML.
    """
    namespaces = {
        "mes": (
            "http://www.sdmx.org/resources/"
            "sdmxml/schemas/v3_1/message"
        ),
        "str": (
            "http://www.sdmx.org/resources/"
            "sdmxml/schemas/v3_1/structure"
        ),
        "com": (
            "http://www.sdmx.org/resources/"
            "sdmxml/schemas/v3_1/common"
        ),
    }

    for prefix, uri in namespaces.items():
        ET.register_namespace(
            prefix,
            uri,
        )

    # ----------------------------------------------------------
    # Structure message
    # ----------------------------------------------------------

    root = ET.Element(
        ET.QName(
            namespaces["mes"],
            "Structure",
        )
    )

      # ----------------------------------------------------------
    # Header
    # ----------------------------------------------------------

    header = ET.SubElement(
        root,
        ET.QName(
            namespaces["mes"],
            "Header",
        ),
    )

    ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "ID",
        ),
    ).text = (
        f"STRUCTURE_{model['id']}"
    )

    ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "Test",
        ),
    ).text = "false"

    ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "Prepared",
        ),
    ).text = (
        datetime.now(timezone.utc)
        .isoformat(
            timespec="seconds"
        )
        .replace(
            "+00:00",
            "Z",
        )
    )

    sender = ET.SubElement(
        header,
        ET.QName(
            namespaces["mes"],
            "Sender",
        ),
        {
            "id": model["agency"],
        },
    )

    ET.SubElement(
        sender,
        ET.QName(
            namespaces["com"],
            "Name",
        ),
        {
            "{http://www.w3.org/XML/1998/namespace}lang": "en",
        },
    ).text = (
        "International Labour Organization"
    )

    ET.SubElement(
        sender,
        ET.QName(
            namespaces["com"],
            "Name",
        ),
        {
            "{http://www.w3.org/XML/1998/namespace}lang": "en",
        },
    ).text = "International Labour Organization"

    structures = ET.SubElement(
        root,
        ET.QName(
            namespaces["mes"],
            "Structures",
        ),
    )

    # ----------------------------------------------------------
    # Concept schemes
    # ----------------------------------------------------------

    concept_schemes = ET.SubElement(
        structures,
        ET.QName(
            namespaces["str"],
            "ConceptSchemes",
        ),
    )

    concept_scheme = ET.SubElement(
        concept_schemes,
        ET.QName(
            namespaces["str"],
            "ConceptScheme",
        ),
        {
            "id": model["concept_scheme"],
            "agencyID": model["agency"],
            "version": model["version"],
        },
    )

    concept_scheme_name = ET.SubElement(
        concept_scheme,
        ET.QName(
            namespaces["com"],
            "Name",
        ),
        {
            "{http://www.w3.org/XML/1998/namespace}lang": (
                lang
            ),
        },
    )

    concept_scheme_name.text = (
        f"Concept scheme for {model['id']}"
    )

    for component in model["components"]:

        concept = ET.SubElement(
            concept_scheme,
            ET.QName(
                namespaces["str"],
                "Concept",
            ),
            {
                "id": component["id"],
            },
        )

        name = ET.SubElement(
            concept,
            ET.QName(
                namespaces["com"],
                "Name",
            ),
            {
                "{http://www.w3.org/XML/1998/namespace}lang": (
                    lang
                ),
            },
        )

        name.text = component["name"]

    # ----------------------------------------------------------
    # Data structures
    # ----------------------------------------------------------

    data_structures = ET.SubElement(
        structures,
        ET.QName(
            namespaces["str"],
            "DataStructures",
        ),
    )

    data_structure = ET.SubElement(
        data_structures,
        ET.QName(
            namespaces["str"],
            "DataStructure",
        ),
        {
            "id": model["id"],
            "agencyID": model["agency"],
            "version": model["version"],
        },
    )

    data_structure_name = ET.SubElement(
        data_structure,
        ET.QName(
            namespaces["com"],
            "Name",
        ),
        {
            "{http://www.w3.org/XML/1998/namespace}lang": (
                lang
            ),
        },
    )

    data_structure_name.text = (
        f"Data structure for {model['id']}"
    )

    # ----------------------------------------------------------
    # Components
    # ----------------------------------------------------------

    components_element = ET.SubElement(
        data_structure,
        ET.QName(
            namespaces["str"],
            "DataStructureComponents",
        ),
    )

    dimensions = ET.SubElement(
        components_element,
        ET.QName(
            namespaces["str"],
            "DimensionList",
        ),
    )

    attributes = ET.SubElement(
        components_element,
        ET.QName(
            namespaces["str"],
            "AttributeList",
        ),
    )

    measures = ET.SubElement(
        components_element,
        ET.QName(
            namespaces["str"],
            "MeasureList",
        ),
    )
    # ----------------------------------------------------------
    # Individual components
    # ----------------------------------------------------------

    for component in model["components"]:

        role = component["role"]

        if role == "dimension":
            parent = dimensions

            if component["id"] == "TIME_PERIOD":
                element_name = "TimeDimension"
            else:
                element_name = "Dimension"

        elif role == "measure":
            parent = measures
            element_name = "Measure"

        elif role == "attribute":
            parent = attributes
            element_name = "Attribute"

        else:
            continue

        properties = {
            "id": component["id"],
        }

        if (
            component["position"] is not None
            and component["id"] != "TIME_PERIOD"
        ):
            properties["position"] = str(
                component["position"]
            )

        component_element = ET.SubElement(
            parent,
            ET.QName(
                namespaces["str"],
                element_name,
            ),
            properties,
        )

        # ------------------------------------------------------
        # Concept identity
        # ------------------------------------------------------

        concept_identity = ET.SubElement(
            component_element,
            ET.QName(
                namespaces["str"],
                "ConceptIdentity",
            ),
        )

        concept_identity.text = (
            "urn:sdmx:org.sdmx.infomodel."
            "conceptscheme.Concept="
            f"{model['agency']}:"
            f"{model['concept_scheme']}"
            f"({model['version']})."
            f"{component['id']}"
        )

        # ------------------------------------------------------
        # Time representation
        # ------------------------------------------------------

        if component["id"] == "TIME_PERIOD":

            local_representation = ET.SubElement(
                component_element,
                ET.QName(
                    namespaces["str"],
                    "LocalRepresentation",
                ),
            )

            text_format = ET.SubElement(
                local_representation,
                ET.QName(
                    namespaces["str"],
                    "TextFormat",
                ),
            )

            text_format.set(
                "textType",
                "ObservationalTimePeriod",
            )

        # ------------------------------------------------------
        # Coded representation
        # ------------------------------------------------------

        if component["codelist"] is not None:

            local_representation = ET.SubElement(
                component_element,
                ET.QName(
                    namespaces["str"],
                    "LocalRepresentation",
                ),
            )

            enumeration = ET.SubElement(
                local_representation,
                ET.QName(
                    namespaces["str"],
                    "Enumeration",
                ),
            )

            enumeration.text = (
                "urn:sdmx:org.sdmx.infomodel."
                "codelist.Codelist="
                f"{model['agency']}:"
                f"{component['codelist'].upper()}"
                f"({model['version']})"
            )

        # ------------------------------------------------------
        # Attribute relationship
        # ------------------------------------------------------

        if (
            role == "attribute"
            and component["attachment"] == "observation"
        ):

            relationship = ET.SubElement(
                component_element,
                ET.QName(
                    namespaces["str"],
                    "AttributeRelationship",
                ),
            )

            ET.SubElement(
                relationship,
                ET.QName(
                    namespaces["str"],
                    "Observation",
                ),
            )

    # ----------------------------------------------------------
    # Pretty formatting
    # ----------------------------------------------------------

    ET.indent(
        root,
        space="  ",
    )

    return ET.tostring(
        root,
        encoding="unicode",
        xml_declaration=False,
    )

def _to_sdmx_structure(
    meta: dict,
    type: str,
    lang: str,
) -> pd.DataFrame:
    """
    Transform ILOSTAT metadata into an SDMX-oriented
    structure description.
    """

    rows = []

    def add_dimension(
        component_id: str,
        component_name: str | None,
        representation: str = "coded",
    ) -> None:
        position = len(rows) + 1

        row = {
            "COMPONENT_ID": component_id,
            "ROLE": "dimension",
            "POSITION": position,
            "REPRESENTATION": representation,
        }

        if type in {
            "label",
            "label_short",
            "both",
        }:
            row["COMPONENT_NAME"] = (
                component_name
                or component_id
            )

        rows.append(
            row
        )

    # ----------------------------------------------------------
    # REF_AREA
    # ----------------------------------------------------------

    ref_area = (
        meta.get("dimensions", {})
        .get("ref_area", {})
    )

    add_dimension(
        component_id="REF_AREA",
        component_name=(
            ref_area.get("label", {})
            .get(lang)
        ),
    )

    # ----------------------------------------------------------
    # SOURCE
    # ----------------------------------------------------------

    add_dimension(
        component_id="SOURCE",
        component_name="Source",
    )

    # ----------------------------------------------------------
    # FREQ
    # ----------------------------------------------------------

    add_dimension(
        component_id="FREQ",
        component_name=(
        SDMX_COMPONENT_NAMES["FREQ"]
        .get(lang)
        )
    )

    # ----------------------------------------------------------
    # MEASURE
    # ----------------------------------------------------------

    add_dimension(
        component_id="MEASURE",
        component_name=(
            SDMX_COMPONENT_NAMES["MEASURE"]
            .get(lang)
        ),
    )

    # ----------------------------------------------------------
    # Semantic dimensions
    #
    # SEX, AGE, ECO, EDU, OCU, etc.
    # ----------------------------------------------------------

    for dimension in meta.get(
        "dimensions",
        {}
    ).values():

        api_name = dimension.get(
            "api_name"
        )

        dimension_type = dimension.get(
            "type"
        )

        if (
            not api_name
            or not dimension_type
        ):
            continue

        component_id = (
            dimension_type.upper()
        )

        # REF_AREA was already handled above.
        if component_id == "REF_AREA":
            continue

        add_dimension(
            component_id=component_id,
            component_name=(
                dimension.get("label", {})
                .get(lang)
            ),
        )

    # ----------------------------------------------------------
    # TIME_PERIOD
    # ----------------------------------------------------------

    add_dimension(
        component_id="TIME_PERIOD",
        component_name="Time period",
        representation="time",
    )

    # ----------------------------------------------------------
    # Primary measure
    # ----------------------------------------------------------

    row = {
        "COMPONENT_ID": "OBS_VALUE",
        "ROLE": "measure",
        "POSITION": None,
        "REPRESENTATION": "number",
    }

    if type in {
        "label",
        "label_short",
        "both",
    }:
        row["COMPONENT_NAME"] = (
            "Observation value"
        )

    rows.append(
        row
    )

    # ----------------------------------------------------------
    # Attributes
    # ----------------------------------------------------------

    attributes = [
        (
            "OBS_STATUS",
            "Observation status",
            "coded",
        ),
        (
            "UNIT_MEASURE",
            "Unit of measure",
            "coded",
        ),
        (
            "UNIT_MULT",
            "Multiplier",
            "coded",
        ),
        (
            "NOTE_SOURCE",
            "Source note",
            "coded",
        ),
        (
            "NOTE_INDICATOR",
            "Indicator note",
            "coded",
        ),
        (
            "NOTE_CLASSIF",
            "Classification note",
            "coded",
        ),
        (
            "BEST_SOURCE",
            "Best source",
            "coded",
        ),
    ]

    for (
        component_id,
        component_name,
        representation,
    ) in attributes:

        row = {
            "COMPONENT_ID": component_id,
            "ROLE": "attribute",
            "POSITION": None,
            "REPRESENTATION": representation,
        }

        if type in {
            "label",
            "label_short",
            "both",
        }:
            row["COMPONENT_NAME"] = (
                SDMX_COMPONENT_NAMES
                .get(
                    component_id,
                    {},
                )
                .get(
                    lang,
                    component_name,
                )
            )

        rows.append(
            row
        )

    out = pd.DataFrame(
        rows
    )

    out["POSITION"] = out["POSITION"].astype(
        "Int64"
    )

    out["CODELIST"] = [
        _get_codelist_name(
            component_id=component_id,
            representation=representation,
        )
        for component_id, representation
        in zip(
            out["COMPONENT_ID"],
            out["REPRESENTATION"],
            strict=True,
        )
    ]

    if type in {
        "label",
        "label_short",
    }:
        out = out.drop(
            columns=["COMPONENT_ID"],
        )

    return out

def _format_sdmx_time_period(
    series: pd.Series,
) -> pd.Series:
    """
    Convert ILOSTAT time values to SDMX reporting-period format.

    Examples
    --------
    2024    -> 2024
    2024Q1  -> 2024-Q1
    2024M01 -> 2024-M01
    """
    values = series.astype("string")

    values = values.str.replace(
        r"^(\d{4})Q([1-4])$",
        r"\1-Q\2",
        regex=True,
    )

    values = values.str.replace(
        r"^(\d{4})M(0[1-9]|1[0-2])$",
        r"\1-M\2",
        regex=True,
    )

    return values

def _to_sdmx_data(
    df: pd.DataFrame,
    meta: dict,
    type: str,
    lang: str,
) -> pd.DataFrame:
    """
    Transform an ILOSTAT DataFrame to an SDMX-oriented
    DataFrame.
    """

    out = df.copy()

    out = out.drop(
    columns=["indicator"],
    errors="ignore",
    )

    # ----------------------------------------------------------
    # Standard ILOSTAT -> SDMX component names
    # ----------------------------------------------------------

    rename = {
        "source": "SOURCE",
        "time": "TIME_PERIOD",
        "obs_value": "OBS_VALUE",
        "obs_status": "OBS_STATUS",
        "note_classif": "NOTE_CLASSIF",
        "note_indicator": "NOTE_INDICATOR",
        "note_source": "NOTE_SOURCE",
        "best_source": "BEST_SOURCE",
    }

    component_map = _get_component_map(
        meta
    )

    rename.update({
        api_name: component
        for component, api_name
        in component_map.items()
    })

    out = out.rename(
        columns=rename
    )

    if "TIME_PERIOD" in out.columns:
        out["TIME_PERIOD"] = (
            _format_sdmx_time_period(
                out["TIME_PERIOD"]
            )
        )

    # ----------------------------------------------------------
    # Constant SDMX dimensions from metadata
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # Dataset-level SDMX components
    # ----------------------------------------------------------

    frequency = (
        meta.get("dataset", {})
        .get("frequency", {})
        .get("code")
    )

    measure = (
        meta.get("sdmx", {})
        .get("measure", {})
        .get("code")
    )

    unit_measure = (
        meta.get("sdmx", {})
        .get("unit_measure", {})
        .get("code")
    )

    unit_mult = (
        meta.get("sdmx", {})
        .get("unit_mult", {})
        .get("code")
    )

    if frequency is not None:
        out["FREQ"] = frequency

    if measure is not None:
        out["MEASURE"] = measure

    if unit_measure is not None:
        out["UNIT_MEASURE"] = unit_measure

    if unit_mult is not None:
        out["UNIT_MULT"] = unit_mult
    # ----------------------------------------------------------
    # SDMX dataflow envelope
    # ----------------------------------------------------------

    dataflow = (
        meta.get("sdmx", {})
        .get("dataflow", {})
    )

    dataflow_id = dataflow.get(
        "id"
    )

    dataflow_name = (
        dataflow.get("name", {})
        .get(lang)
    )

    if dataflow_id:

        out.insert(
            0,
            "STRUCTURE",
            "dataflow",
        )

        out.insert(
            1,
            "STRUCTURE_ID",
            f"ILO:{dataflow_id}(1.0)",
        )

        position = 2

        if (
            type in {"label", "label_short", "both"}
            and dataflow_name
        ):
            out.insert(
                position,
                "STRUCTURE_NAME",
                dataflow_name,
            )

            position += 1

        out.insert(
            position,
            "ACTION",
            "I",
        )

    # ----------------------------------------------------------
    # Localized labels
    # ----------------------------------------------------------

    if type in {"label", "label_short", "both"}:

        out = _add_sdmx_labels(
            out=out,
            meta=meta,
            lang=lang,
            type=type,
        )

    # ----------------------------------------------------------
    # SDMX column order
    # ----------------------------------------------------------

    return _order_sdmx_columns(
        out=out,
        meta=meta,
    )


def _add_sdmx_labels(
    out: pd.DataFrame,
    meta: dict,
    lang: str,
    type: str,
) -> pd.DataFrame:
    """
    Add localized labels to coded SDMX components.

    type="label":
        Replace codes with localized labels.

    type="label_short":
        Replace codes with localized labels, using compact
        display values for classif1 and classif2.

    type="both":
        Keep codes and add localized labels in adjacent
        *_LABEL columns.
    """

    # ----------------------------------------------------------
    # FREQ
    # ----------------------------------------------------------

    frequency = (
        meta.get("dataset", {})
        .get("frequency", {})
    )

    frequency_label = (
        frequency.get("label", {})
        .get(lang)
    )

    if (
        "FREQ" in out.columns
        and frequency_label is not None
    ):

        if type in {
            "label",
            "label_short",
        }:
            out["FREQ"] = (
                frequency_label
            )

        elif type == "both":
            position = (
                out.columns.get_loc(
                    "FREQ"
                )
                + 1
            )

            out.insert(
                position,
                "FREQ_LABEL",
                frequency_label,
            )

    # ----------------------------------------------------------
    # MEASURE
    # ----------------------------------------------------------

    measure = (
        meta.get("sdmx", {})
        .get("measure", {})
    )

    measure_label = (
        measure.get("label", {})
        .get(lang)
    )

    if (
        "MEASURE" in out.columns
        and measure_label is not None
    ):

        if type in {
            "label",
            "label_short",
        }:
            out["MEASURE"] = (
                measure_label
            )

        elif type == "both":
            position = (
                out.columns.get_loc(
                    "MEASURE"
                )
                + 1
            )

            out.insert(
                position,
                "MEASURE_LABEL",
                measure_label,
            )

    # ----------------------------------------------------------
    # UNIT_MEASURE
    # ----------------------------------------------------------

    unit_measure = (
        meta.get("sdmx", {})
        .get("unit_measure", {})
    )

    unit_measure_label = (
        unit_measure.get("label", {})
        .get(lang)
    )

    if (
        "UNIT_MEASURE" in out.columns
        and unit_measure_label is not None
    ):

        if type in {
            "label",
            "label_short",
        }:
            out["UNIT_MEASURE"] = (
                unit_measure_label
            )

        elif type == "both":
            position = (
                out.columns.get_loc(
                    "UNIT_MEASURE"
                )
                + 1
            )

            out.insert(
                position,
                "UNIT_MEASURE_LABEL",
                unit_measure_label,
            )

    # ----------------------------------------------------------
    # UNIT_MULT
    # ----------------------------------------------------------

    unit_mult = (
        meta.get("sdmx", {})
        .get("unit_mult", {})
    )

    unit_mult_label = (
        unit_mult.get("label", {})
        .get(lang)
    )

    if (
        "UNIT_MULT" in out.columns
        and unit_mult_label is not None
    ):

        if type in {
            "label",
            "label_short",
        }:
            out["UNIT_MULT"] = (
                unit_mult_label
            )

        elif type == "both":
            position = (
                out.columns.get_loc(
                    "UNIT_MULT"
                )
                + 1
            )

            out.insert(
                position,
                "UNIT_MULT_LABEL",
                unit_mult_label,
            )

    # ----------------------------------------------------------
    # REF_AREA
    # ----------------------------------------------------------

    ref_area = (
        meta.get("dimensions", {})
        .get("ref_area", {})
    )

    _add_value_labels(
        out=out,
        column="REF_AREA",
        dimension=ref_area,
        lang=lang,
        type=type,
    )

    # ----------------------------------------------------------
    # SOURCE
    # ----------------------------------------------------------

    source = meta.get(
        "source",
        {}
    )

    _add_value_labels(
        out=out,
        column="SOURCE",
        dimension=source,
        lang=lang,
        type=type,
    )

    # ----------------------------------------------------------
    # Semantic dimensions
    #
    # Includes SEX and classifications such as AGE,
    # ECO, OCU, EDU, etc.
    # ----------------------------------------------------------

    for dimension in meta.get(
        "dimensions",
        {}
    ).values():

        api_name = dimension.get(
            "api_name"
        )

        dimension_type = dimension.get(
            "type"
        )

        if (
            not api_name
            or not dimension_type
        ):
            continue

        column = (
            dimension_type.upper()
        )

        if column not in out.columns:
            continue

        _add_value_labels(
            out=out,
            column=column,
            dimension=dimension,
            lang=lang,
            type=type,
        )

    # ----------------------------------------------------------
    # OBS_STATUS
    # ----------------------------------------------------------

    observation_status = {
        "values": meta.get(
            "observation_status",
            []
        )
    }

    _add_value_labels(
        out=out,
        column="OBS_STATUS",
        dimension=observation_status,
        lang=lang,
        type=type,
    )

    # ----------------------------------------------------------
    # NOTES
    # ----------------------------------------------------------

    notes = meta.get(
        "notes",
        {}
    )

    _add_note_labels(
        out=out,
        column="NOTE_SOURCE",
        notes=notes.get(
            "source",
            []
        ),
        lang=lang,
        type=type,
    )

    _add_note_labels(
        out=out,
        column="NOTE_INDICATOR",
        notes=notes.get(
            "indicator",
            []
        ),
        lang=lang,
        type=type,
    )

    _add_note_labels(
        out=out,
        column="NOTE_CLASSIF",
        notes=notes.get(
            "classification",
            []
        ),
        lang=lang,
        type=type,
    )

    return out

def _add_value_labels(
    out: pd.DataFrame,
    column: str,
    dimension: dict,
    lang: str,
    type: str,
) -> None:
    """
    Add labels for one coded SDMX component.

    For classification dimensions (classif1/classif2):

    - type="label" uses the full classification label.
    - type="label_short" uses the compact display label.
    - type="both" keeps the code and adds the full label.

    Other dimensions use the display label when available,
    falling back to the full label.
    """

    if column not in out.columns:
        return

    values = dimension.get(
        "values",
        []
    )

    if not values:
        return

    labels = {}

    api_name = dimension.get(
        "api_name"
    )

    is_classification = (
        api_name in {
            "classif1",
            "classif2",
        }
    )

    for item in values:

        code = item.get(
            "code"
        )

        if code is None:
            continue

        if (
            is_classification
            and type != "label_short"
        ):
            # Full classification label preserves
            # classification/version context.
            label = (
                item.get("label", {})
                .get(lang)
            )

        else:
            # Compact representation.
            label = (
                item.get("display", {})
                .get(lang)
                or item.get("label", {})
                .get(lang)
            )

        if label is not None:
            labels[code] = label

    if not labels:
        return

    mapped = out[
        column
    ].map(labels)

    if type in {
        "label",
        "label_short",
    }:

        # Replace codes with localized labels.
        out[column] = mapped.fillna(
            out[column]
        )

    elif type == "both":

        # Keep code and add the full localized label
        # in an adjacent column.
        label_column = (
            f"{column}_LABEL"
        )

        position = (
            out.columns.get_loc(column)
            + 1
        )

        out.insert(
            position,
            label_column,
            mapped,
        )

def _order_sdmx_columns(
    out: pd.DataFrame,
    meta: dict,
) -> pd.DataFrame:
    """
    Apply a stable SDMX column order.

    Localized *_LABEL columns, when present, are kept
    immediately after their coded component.
    """

    ordered = []

    def add_column(
        column: str,
    ) -> None:
        """
        Add an SDMX component and its adjacent label,
        when present.
        """
        if (
            column not in out.columns
            or column in ordered
        ):
            return

        ordered.append(
            column
        )

        label_column = (
            f"{column}_LABEL"
        )

        if label_column in out.columns:
            ordered.append(
                label_column
            )

    # ----------------------------------------------------------
    # SDMX envelope
    # ----------------------------------------------------------

    for column in [
        "STRUCTURE",
        "STRUCTURE_ID",
        "STRUCTURE_NAME",
        "ACTION",
    ]:
        add_column(
            column
        )

    # ----------------------------------------------------------
    # Reference area
    # ----------------------------------------------------------

    add_column(
        "REF_AREA"
    )

    add_column(
        "SOURCE"
    )

    # ----------------------------------------------------------
    # Frequency and measure
    # ----------------------------------------------------------

    add_column(
        "FREQ"
    )

    add_column(
        "MEASURE"
    )

    # ----------------------------------------------------------
    # Semantic dimensions
    #
    # SEX, AGE, ECO, EDU, OCU, etc. are generated from
    # metadata and retain metadata order.
    # ----------------------------------------------------------

    for dimension in meta.get(
        "dimensions",
        {}
    ).values():

        dimension_type = dimension.get(
            "type"
        )

        if not dimension_type:
            continue

        column = (
            dimension_type.upper()
        )

        # REF_AREA was already handled above.
        if column == "REF_AREA":
            continue

        add_column(
            column
        )

    # ----------------------------------------------------------
    # Observation
    # ----------------------------------------------------------

    add_column(
        "TIME_PERIOD"
    )

    add_column(
        "OBS_VALUE"
    )

    add_column(
        "OBS_STATUS"
    )

    # ----------------------------------------------------------
    # Unit attributes
    # ----------------------------------------------------------

    add_column(
        "UNIT_MEASURE"
    )

    add_column(
        "UNIT_MULT"
    )

    # ----------------------------------------------------------
    # Source and notes
    # ----------------------------------------------------------
    
    add_column(
        "NOTE_SOURCE"
    )

    add_column(
        "NOTE_INDICATOR"
    )

    add_column(
        "NOTE_CLASSIF"
    )

    # ----------------------------------------------------------
    # ILOSTAT source-selection flag
    #
    # Present only when returned by get_df().
    # ----------------------------------------------------------

    add_column(
        "BEST_SOURCE"
    )

    # ----------------------------------------------------------
    # Preserve anything not explicitly handled.
    # ----------------------------------------------------------

    remaining = [
        column
        for column in out.columns
        if column not in ordered
    ]

    return out[
        ordered + remaining
    ].reset_index(
        drop=True
    )

def _get_component_map(
    meta: dict,
) -> dict[str, str]:
    """
    Return SDMX component -> ILOSTAT physical column mapping.
    """

    mapping = {}

    for name, dimension in meta.get(
        "dimensions",
        {}
    ).items():

        api_name = dimension.get(
            "api_name"
        )

        if not api_name:
            continue

        component = (
            dimension.get("type")
            or name
        ).upper()

        mapping[component] = api_name

    return mapping


def _translate_sdmx_filters(
    filters: dict | None,
    meta: dict,
) -> dict | None:
    """
    Translate SDMX component names to ILOSTAT physical
    column names expected by get_df().

    Existing ILOSTAT column names remain supported.
    """
    if filters is None:
        return None

    component_map = _get_component_map(
        meta
    )

    component_map.update({
        "SOURCE": "source",
        "TIME_PERIOD": "time",
        "OBS_STATUS": "obs_status",
        "NOTE_CLASSIF": "note_classif",
        "NOTE_INDICATOR": "note_indicator",
        "NOTE_SOURCE": "note_source",
        "BEST_SOURCE": "best_source",
    })

    translated = {}

    for name, value in filters.items():

        physical_name = component_map.get(
            name.upper(),
            name,
        )

        translated[physical_name] = value

    return translated

def _extract_constant_filters(
    filters: dict | None,
    meta: dict,
) -> tuple[dict | None, bool]:
    """
    Remove constant SDMX component filters and determine
    whether they match the dataset.

    FREQ and MEASURE are dataset-level constants stored in
    metadata rather than physical columns in the data file.

    Returns
    -------
    tuple
        Remaining filters and whether the constant filters match.
    """
    if filters is None:
        return None, True

    remaining = dict(filters)

    frequency = (
        meta.get("dataset", {})
        .get("frequency", {})
        .get("code")
    )

    measure = (
        meta.get("sdmx", {})
        .get("measure", {})
        .get("code")
    )

    constants = {
        "FREQ": frequency,
        "MEASURE": measure,
    }

    matches = True

    for component, expected in constants.items():

        matching_key = next(
            (
                key
                for key in remaining
                if key.upper() == component
            ),
            None,
        )

        if matching_key is None:
            continue

        requested = remaining.pop(
            matching_key
        )

        if isinstance(
            requested,
            (list, tuple, set),
        ):
            if expected not in requested:
                matches = False
        elif requested != expected:
            matches = False

    return remaining, matches

def _split_sdmx_filters(
    filters: dict | None,
) -> tuple[dict | None, dict | None]:
    """
    Split simple filters from SDMX operator filters.

    Examples
    --------
    REF_AREA="FRA" is a simple filter.

    TIME_PERIOD={"ge": "2020", "le": "2024"}
    is an operator filter.
    """
    if filters is None:
        return None, None

    simple = {}
    operators = {}

    for name, value in filters.items():

        if isinstance(value, dict):
            operators[name] = value
        else:
            simple[name] = value

    return (
        simple or None,
        operators or None,
    )


def _apply_sdmx_operator_filters(
    df: pd.DataFrame,
    filters: dict | None,
) -> tuple[pd.DataFrame, dict | None]:
    """
    Apply SDMX-style comparison filters.

    Supported operators are:
    eq, ne, lt, le, gt, ge.
    """
    if filters is None:
        return df, None

    operators = {
        "eq": lambda series, value: series == value,
        "ne": lambda series, value: series != value,
        "lt": lambda series, value: series < value,
        "le": lambda series, value: series <= value,
        "gt": lambda series, value: series > value,
        "ge": lambda series, value: series >= value,
    }

    for column, condition in filters.items():

        if column not in df.columns:
            raise ValueError(
                f"Filter column '{column}' "
                "does not exist in the SDMX dataset."
            )

        series = df[
            column
        ].astype("string")

        if column == "TIME_PERIOD":
            series = series.str[:4]

        mask = pd.Series(
            True,
            index=df.index,
        )

        for operator, value in condition.items():

            if operator not in operators:
                raise ValueError(
                    f"Unsupported SDMX filter operator "
                    f"'{operator}'. Choose from "
                    "'eq', 'ne', 'lt', 'le', 'gt', or 'ge'."
                )

            comparison_value = str(value)

            if column == "TIME_PERIOD":
                comparison_value = comparison_value[:4]

            mask &= operators[
                operator
            ](
                series,
                comparison_value,
            )

        df = df.loc[
            mask
        ]

    return df, None

def _add_note_labels(
    out: pd.DataFrame,
    column: str,
    notes: list,
    lang: str,
    type: str,
) -> None:
    """
    Add localized labels for ILOSTAT note codes.

    Multiple note codes are separated by "_".

    Examples
    --------
    R1:3513
    R1:3260_T30:2334
    """

    if column not in out.columns:
        return

    if not notes:
        return

    labels = {}

    for item in notes:

        code = item.get("code")

        if code is None:
            continue

        label = (
            item.get("label", {})
            .get(lang)
        )

        if label is not None:
            labels[code] = label

    if not labels:
        return

    def resolve(value):

        if pd.isna(value):
            return pd.NA

        codes = str(value).split("_")

        resolved = [
            labels.get(code, code)
            for code in codes
        ]

        return " | ".join(
            resolved
        )

    # Resolve each distinct combination only once.
    unique_values = (
        out[column]
        .dropna()
        .unique()
    )

    resolved = {
        value: resolve(value)
        for value in unique_values
    }

    mapped = out[column].map(
        resolved
    )

    if type in {
        "label",
        "label_short",
    }:
        out[column] = mapped.fillna(
            out[column]
        )

    elif type == "both":

        position = (
            out.columns.get_loc(column)
            + 1
        )

        out.insert(
            position,
            f"{column}_LABEL",
            mapped,
        )

def _build_sdmx_structure_model(
    dataset_id: str,
    meta: dict,
    lang: str = "en",
) -> dict:
    """
    Build the internal SDMX structure model for an
    ILOSTAT dataset.
    """
    structure = _to_sdmx_structure(
        meta=meta,
        type="both",
        lang=lang,
    )

    components = []

    for row in structure.to_dict(
        orient="records"
    ):
        position = row["POSITION"]

        if pd.isna(position):
            position = None
        else:
            position = int(position)

        codelist = row["CODELIST"]

        if pd.isna(codelist):
            codelist = None

        components.append(
            {
                "id": row["COMPONENT_ID"],
                "name": row["COMPONENT_NAME"],
                "role": row["ROLE"],
                "position": position,
                "representation": row["REPRESENTATION"],
                "codelist": codelist,
                "attachment": (
                    "observation"
                    if row["ROLE"] == "attribute"
                    else None
            ),
            }
        )

    return {
        "id": dataset_id,
        "agency": "ILO",
        "version": "1.0",
        "concept_scheme": f"CS_{dataset_id}",
        "components": components,
    }

def _get_codelist_name(
    component_id: str,
    representation: str,
) -> str | None:
    """
    Return the canonical ILOSTAT codelist name for an
    SDMX component.

    Non-coded components do not have a codelist.
    """
    if representation != "coded":
        return None

    return (
        f"cl_{component_id.lower()}"
    )

def _add_sdmx_ref(
    parent: ET.Element,
    namespace: str,
    element_name: str,
    *,
    agency: str,
    object_id: str,
    version: str,
    class_name: str,
) -> ET.Element:
    """
    Add an SDMX maintainable reference.
    """
    element = ET.SubElement(
        parent,
        ET.QName(
            namespace,
            element_name,
        ),
    )

    ET.SubElement(
        element,
        ET.QName(
            namespace,
            "Ref",
        ),
        {
            "agencyID": agency,
            "id": object_id,
            "version": version,
            "class": class_name,
        },
    )

    return element