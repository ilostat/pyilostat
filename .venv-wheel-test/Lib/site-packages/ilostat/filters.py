from __future__ import annotations

import re
from collections.abc import Iterable

import pandas as pd


def _as_list(value: str | Iterable[str]) -> list[str]:
    """Normalize a filter value to a list of strings."""
    if isinstance(value, str):
        return [value]

    return [str(item) for item in value]


def apply_filters(
    df: pd.DataFrame,
    filters: dict[str, str | Iterable[str]] | None = None,
    fixed: bool = True,
) -> pd.DataFrame:
    """
    Apply ILOSTAT filters to a DataFrame.

    Special filters
    ---------------
    timefrom
        Keep observations from this year onward.

    timeto
        Keep observations up to this year.

    Other filters are matched against the corresponding
    ILOSTAT dimension using substring detection.
    """
    if not filters:
        return df

    result = df

    # Work on a copy so the user's dictionary is not modified.
    filters = dict(filters)

    timefrom = filters.pop("timefrom", None)
    timeto = filters.pop("timeto", None)

    # ---------------------------------------------------------
    # Time filtering
    # Uses the first four characters of the ILOSTAT time code.
    #
    # 2020    -> 2020
    # 2020Q1  -> 2020
    # 2020M01 -> 2020
    # ---------------------------------------------------------

    if timefrom is not None or timeto is not None:
        if "time" not in result.columns:
            raise ValueError(
                "Time filtering was requested, but the dataset "
                "does not contain a 'time' column."
            )

        year = pd.to_numeric(
            result["time"]
            .astype("string")
            .str[:4],
            errors="coerce",
        )

        if timefrom is not None:
            result = result.loc[
                year >= int(timefrom)
            ]
            year = year.loc[result.index]

        if timeto is not None:
            result = result.loc[
                year <= int(timeto)
            ]

    # ---------------------------------------------------------
    # Dimension filters
    # ---------------------------------------------------------

    for column, values in filters.items():
        if column not in result.columns:
            raise ValueError(
                f"Filter column '{column}' does not exist "
                f"in the dataset."
            )

        patterns = _as_list(values)

        if fixed:
            patterns = [
                re.escape(pattern)
                for pattern in patterns
            ]

        pattern = "|".join(patterns)

        mask = (
            result[column]
            .astype("string")
            .str.contains(
                pattern,
                regex=True,
                na=False,
            )
        )

        result = result.loc[mask]

    return result