from __future__ import annotations

from typing import Any

import pandas as pd

VALID_LANGUAGES = {"en", "fr", "es"}

LABEL_DIMENSIONS = (
    "ref_area",
    "indicator",
    "source",
    "sex",
    "classif1",
    "classif2",
    "obs_status",
)

NOTE_DIMENSIONS = (
    "note_classif",
    "note_indicator",
    "note_source",
)


def _build_note_label(
    value: object,
    mapping: dict[str, str],
) -> object:
    """
    Convert underscore-separated note codes to labels.

    Multiple note labels are joined with " | ".
    """
    if pd.isna(value):
        return value

    value_str = str(value)

    if not value_str:
        return value_str

    codes = value_str.split("_")

    labels = [
        mapping.get(code, code)
        for code in codes
    ]

    return " | ".join(labels)


def add_labels(
    df: pd.DataFrame,
    dic: dict[str, Any],
    lang: str = "en",
) -> pd.DataFrame:
    """
    Add labels to coded ILOSTAT dimensions.

    Parameters
    ----------
    df : pandas.DataFrame
        ILOSTAT data.

    dic : dict
        Dataset-specific dictionary loaded from *_dic.json.

    lang : {"en", "fr", "es"}, default "en"
        Language used for labels.

    Returns
    -------
    pandas.DataFrame
        Data with label columns added immediately after
        their corresponding code columns.
    """
    lang = lang.lower()

    if lang not in VALID_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{lang}'. "
            f"Choose from {sorted(VALID_LANGUAGES)}."
        )

    result = df.copy()

    for dimension in LABEL_DIMENSIONS:
        if dimension not in result.columns:
            continue

        entries = dic.get(dimension)

        if not entries:
            continue

        label_column = f"{dimension}.label_{lang}"

        lookup = pd.DataFrame(entries)

        if (
            dimension not in lookup.columns
            or label_column not in lookup.columns
        ):
            continue

        mapping = (
            lookup
            .drop_duplicates(subset=[dimension])
            .set_index(dimension)[label_column]
        )

        position = result.columns.get_loc(dimension) + 1

        result.insert(
            position,
            f"{dimension}.label",
            result[dimension].map(mapping),
        )

    for dimension in NOTE_DIMENSIONS:
        if dimension not in result.columns:
            continue

        entries = dic.get(dimension)

        if not entries:
            continue

        label_column = f"{dimension}.label_{lang}"

        lookup = pd.DataFrame(entries)

        if (
            dimension not in lookup.columns
            or label_column not in lookup.columns
        ):
            continue

        mapping = (
            lookup
            .drop_duplicates(subset=[dimension])
            .set_index(dimension)[label_column]
            .to_dict()
        )

        position = result.columns.get_loc(dimension) + 1

        labels = result[dimension].apply(
            _build_note_label,
            mapping=mapping,
        )

        result.insert(
            position,
            f"{dimension}.label",
            labels,
        )

    return result


def labels_only(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove code columns that have corresponding label columns.

    The label columns retain their ``.label`` names.

    Examples
    --------
    ``ref_area`` + ``ref_area.label``
    becomes ``ref_area.label``.

    ``classif1`` + ``classif1.label``
    becomes ``classif1.label``.

    Columns without a corresponding label, such as ``time`` and
    ``obs_value``, are retained unchanged.
    """
    result = df.copy()

    code_columns = [
        column.removesuffix(".label")
        for column in result.columns
        if (
            column.endswith(".label")
            and column.removesuffix(".label") in result.columns
        )
    ]

    return result.drop(
        columns=code_columns,
    )