from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data import get_df
from .metadata import get_metadata

VALID_RESOURCES = {
    "data",
    "structure",
    "workflow",
}

VALID_TYPES = {
    "code",
    "label",
    "label_short",
    "both",
}

def get_sdmx(
    dataset_id: str,
    resource: str = "data",
    segment: str = "indicator",
    type: str = "code",
    lang: str = "en",
    filters: dict | None = None,
    best_source: str = "yes",
    fixed: bool = True,
    cache_dir: str | Path | None = None,
    refresh: bool = False,
) -> pd.DataFrame:
    """
    Retrieve an ILOSTAT dataset using SDMX conventions.

    Parameters
    ----------
    dataset_id : str
        ILOSTAT dataset identifier.

    resource : {"data", "structure", "workflow"}, default "data"
        SDMX resource to retrieve.

    segment : str, default "indicator"
        ILOSTAT bulk-data segment.

    type : {"code", "label", "label_short", "both"}, default "code"
    Output representation for coded SDMX components.

    "code" returns codes only.

    "label" returns localized labels. Classification dimensions
    use their full labels, including classification context.

    "label_short" returns localized labels using compact display
    values for classification dimensions when available.

    "both" returns codes together with localized full labels
    in adjacent columns.

    lang : {"en", "fr", "es"}, default "en"
        Language used for labels.

    filters : dict or None, default None
        Filters applied to the dataset.

    best_source : {"yes", "no", "all"}, default "yes"
        Select best-source observations.

    fixed : bool, default True
        If True, treat filter values as literal strings.

    cache_dir : str, pathlib.Path or None, default None
        Directory used to cache downloaded files.

    refresh : bool, default False
        If True, refresh metadata before checking cached data.

    Returns
    -------
    pandas.DataFrame
        Requested SDMX-oriented resource.
    """
    resource = resource.lower()
    type = type.lower()

    if resource not in VALID_RESOURCES:
        raise ValueError(
            "Invalid resource value. "
            "Choose from 'data', 'structure', or 'workflow'."
        )

    if type not in VALID_TYPES:
        raise ValueError(
            "Invalid type value. "
            "Choose from 'code', 'label', 'label_short', or 'both'."
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

    raise NotImplementedError(
        f"SDMX resource '{resource}' is not implemented yet."
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