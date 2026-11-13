#!/usr/bin/env python3
"""Read-only independent SDMX-JSON 2.1 reconstruction vs ILOSTAT tabular JSON.
Corrected key comparison: compare key sets, not Counter(dict) values.
Requires: requests. Run: py test_independent_sdmx_json.py
"""
import math
import os
import sys

import requests

BASE = os.environ.get('ILOSTAT_SDMX_TEST_BASE', 'https://rplumber.ilo.org/sdmx/v2').rstrip('/')
DATASETS = (
    'UNE_TUNE_SEX_AGE_NB_A',
    'EMP_TEMP_SEX_ECO_EDU_NB_Q',
    'SDG_0861_SEX_RT_A',
    'SDG_B922_NOC_RT_A',
)
EXPECTED_BREAKDOWNS = {
    'UNE_TUNE_SEX_AGE_NB_A': {'SEX', 'AGE'},
    'EMP_TEMP_SEX_ECO_EDU_NB_Q': {'SEX', 'ECO', 'EDU'},
    'SDG_0861_SEX_RT_A': {'SEX'},
    'SDG_B922_NOC_RT_A': set(),
}
CLASSIFICATIONS = {'SEX', 'AGE', 'ECO', 'EDU', 'OCU'}
SEP = '\x1f'


def get_json(session, endpoint, fmt):
    response = session.get(endpoint, params={
        'REF_AREA': 'FRA', 'firstNObservations': '2', 'format': fmt
    }, timeout=120)
    response.raise_for_status()
    return response.json()


def decode(entry):
    if 'id' in entry:
        return str(entry['id'])
    if 'value' in entry:
        return str(entry['value'])
    raise ValueError(f'Dimension/attribute value lacks id/value: {entry!r}')


def value_at(definition, index):
    values = definition.get('values', [])
    if not isinstance(index, int) or index < 0 or index >= len(values):
        raise ValueError(f'Index {index} outside {definition.get("id")} domain')
    return decode(values[index])


def normalized_value(value):
    if value is None or value == '':
        return None
    return str(value)


def check_one(session, dataset):
    endpoint = f'{BASE}/data/dataflow/ILO/{dataset}/1.0'
    plain = get_json(session, endpoint, 'json')
    obj = get_json(session, endpoint, 'sdmx-json')
    if not isinstance(plain, list) or not plain:
        raise AssertionError('Expected nonempty tabular JSON list')
    data = obj['data']
    structure = data['structures'][0]
    data_set = data['dataSets'][0]
    dims = structure['dimensions']['series']
    times = structure['dimensions']['observation']
    attrs = structure['attributes'].get('observation', [])
    if len(times) != 1 or times[0]['id'] != 'TIME_PERIOD':
        raise AssertionError('Unexpected observation time dimension')
    dim_names = [d['id'] for d in dims]
    attr_names = [a['id'] for a in attrs]
    if len(set(dim_names)) != len(dim_names):
        raise AssertionError('Duplicate series dimension identifiers')
    if set(dim_names) & CLASSIFICATIONS != EXPECTED_BREAKDOWNS[dataset]:
        raise AssertionError(f'Unexpected breakdowns: {set(dim_names) & CLASSIFICATIONS}')
    columns = dim_names + ['TIME_PERIOD']
    if any(any(col not in row for col in columns + ['OBS_VALUE']) for row in plain):
        raise AssertionError('Missing tabular key/value column')
    reconstructed = {}
    for skey, series in data_set['series'].items():
        indices = [int(i) for i in skey.split(':')]
        if len(indices) != len(dims):
            raise AssertionError(f'Wrong series key arity: {skey}')
        series_values = [value_at(d, i) for d, i in zip(dims, indices)]
        for tkey, observation in series['observations'].items():
            if len(observation) != len(attrs) + 1:
                raise AssertionError(f'Wrong observation attribute slot count: {skey}/{tkey}')
            time = value_at(times[0], int(tkey))
            key = SEP.join(series_values + [time])
            if key in reconstructed:
                raise AssertionError(f'Duplicate observation key: {key!r}')
            raw_value = observation[0]
            if raw_value is not None and (not isinstance(raw_value, (int, float)) or isinstance(raw_value, bool)):
                raise AssertionError(f'Non-numeric OBS_VALUE: {raw_value!r}')
            decoded_attrs = {}
            for attr, index in zip(attrs, observation[1:]):
                decoded_attrs[attr['id']] = None if index is None else value_at(attr, index)
            reconstructed[key] = (raw_value, decoded_attrs)
    if len(reconstructed) != len(plain):
        raise AssertionError(f'Observation count mismatch: {len(reconstructed)} vs {len(plain)}')
    expected_keys = [SEP.join(str(row[c]) for c in columns) for row in plain]
    if len(set(expected_keys)) != len(expected_keys):
        raise AssertionError('Duplicate observation keys in tabular JSON')
    if set(expected_keys) != set(reconstructed.keys()):
        missing = list(set(expected_keys) - set(reconstructed.keys()))[:3]
        extra = list(set(reconstructed.keys()) - set(expected_keys))[:3]
        raise AssertionError(f'Observation keys differ: tabular_only={missing!r}, sdmx_only={extra!r}')
    compared_attrs = 0
    for row, key in zip(plain, expected_keys):
        actual_value, actual_attrs = reconstructed[key]
        expected_value = row['OBS_VALUE']
        if expected_value is None or actual_value is None:
            if expected_value is not None or actual_value is not None:
                raise AssertionError(f'Missing value mismatch: {key}')
        elif not math.isclose(float(expected_value), float(actual_value), rel_tol=1e-10, abs_tol=1e-10):
            raise AssertionError(f'Value mismatch: {key}: {expected_value} != {actual_value}')
        for attr_name, actual in actual_attrs.items():
            if attr_name not in row:
                raise AssertionError(f'Tabular response missing attribute: {attr_name}')
            expected = normalized_value(row[attr_name])
            if normalized_value(actual) != expected:
                raise AssertionError(f'Attribute mismatch {attr_name} at {key}: {actual!r} != {expected!r}')
            compared_attrs += 1
    return len(reconstructed), len(dim_names), len(attrs), compared_attrs


def main():
    print('Independent SDMX-JSON 2.1 reconstruction')
    print('Endpoint:', BASE)
    failures = 0
    with requests.Session() as session:
        for dataset in DATASETS:
            try:
                n, dims, attrs, attr_checks = check_one(session, dataset)
                print(f'[PASS] {dataset}: observations={n}, series_dimensions={dims}, attributes={attrs}, attribute_checks={attr_checks}')
            except Exception as exc:
                failures += 1
                print(f'[FAIL] {dataset}: {type(exc).__name__}: {exc}')
    print(f'Summary: {len(DATASETS)-failures}/{len(DATASETS)} passed')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
