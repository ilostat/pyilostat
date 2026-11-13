"""Independent, read-only SDMX client smoke test for ILOSTAT.

Run: python test_interoperability.py
Optional: ILOSTAT_SDMX_TEST_BASE=http://127.0.0.1:8099 python test_interoperability.py
"""
import io
import os
import sys
from urllib.parse import urlencode

import requests

BASE = os.environ.get('ILOSTAT_SDMX_TEST_BASE', 'https://rplumber.ilo.org/sdmx/v2').rstrip('/')
TIMEOUT = 90
DATASETS = ('UNE_TUNE_SEX_AGE_NB_A', 'EMP_TEMP_SEX_ECO_EDU_NB_Q', 'SDG_0861_SEX_RT_A', 'SDG_B922_NOC_RT_A')


def fetch(path, params=None, accept=None):
    url = BASE + path
    response = requests.get(url, params=params, headers={'Accept': accept} if accept else {}, timeout=TIMEOUT)
    response.raise_for_status()
    if not response.content:
        raise AssertionError('Empty response: ' + response.url)
    return response


def parse_with_sdmx(response):
    import sdmx
    # A client parser independent of the ILOSTAT R/Python implementations.
    return sdmx.read_sdmx(io.BytesIO(response.content))


def main():
    print('Endpoint:', BASE)
    print('Python:', sys.version.split()[0])
    try:
        import sdmx
        print('sdmx1:', getattr(sdmx, '__version__', 'installed'))
    except ImportError:
        print('ERROR: install dependencies: python -m pip install -r requirements.txt')
        return 2

    failures = 0
    unsupported = 0
    cases = [
        ('dataflow', '/structure/dataflow/ILO/UNE_TUNE_SEX_AGE_NB_A/1.0', {'format': 'sdmx-ml'}),
        ('datastructure', '/structure/datastructure/ILO/UNE_TUNE_SEX_AGE_NB_A/1.0', {'references': 'none', 'format': 'sdmx-ml'}),
    ]
    for dataset in DATASETS:
        cases.append((dataset, '/data/dataflow/ILO/' + dataset + '/1.0', {'REF_AREA': 'FRA', 'firstNObservations': '2', 'format': 'sdmx-ml'}))

    for label, path, params in cases:
        try:
            response = fetch(path, params)
            print('[HTTP PASS]', label, response.status_code, len(response.content), 'bytes')
        except Exception as exc:
            failures += 1
            print('[HTTP FAIL]', label, type(exc).__name__, str(exc)[:240])
            continue
        try:
            msg = parse_with_sdmx(response)
            print('[CLIENT PASS]', label, type(msg).__name__)
        except Exception as exc:
            unsupported += 1
            print('[CLIENT UNVERIFIED]', label, type(exc).__name__, str(exc)[:300])

    print('Summary: HTTP failures:', failures, '| client parse failures/unverified:', unsupported)
    print('Note: client parse failures need investigation; they are not automatically API non-compliance.')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
