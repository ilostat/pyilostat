#!/usr/bin/env python3
"""Read-only diagnosis of ILOSTAT SDMX-JSON versus tabular observation keys."""
import os
import sys
from collections import Counter
import requests

BASE = os.environ.get('ILOSTAT_SDMX_TEST_BASE', 'https://rplumber.ilo.org/sdmx/v2').rstrip('/')
DATASETS = ('UNE_TUNE_SEX_AGE_NB_A','EMP_TEMP_SEX_ECO_EDU_NB_Q','SDG_0861_SEX_RT_A','SDG_B922_NOC_RT_A')
SEP = '\x1f'

def decode(v):
    return str(v['id'] if 'id' in v else v['value'])

def run(session, dataset):
    endpoint = f'{BASE}/data/dataflow/ILO/{dataset}/1.0'
    params = {'REF_AREA':'FRA','firstNObservations':'2'}
    def fetch(fmt):
        r=session.get(endpoint,params={**params,'format':fmt},timeout=120)
        r.raise_for_status()
        return r.json()
    plain=fetch('json')
    obj=fetch('sdmx-json')
    structure=obj['data']['structures'][0]
    dims=structure['dimensions']['series']
    times=structure['dimensions']['observation']
    names=[d['id'] for d in dims]+[times[0]['id']]
    observed=[]
    for skey,series in obj['data']['dataSets'][0]['series'].items():
        indices=[int(i) for i in skey.split(':')]
        series_vals=[decode(d['values'][idx]) for d,idx in zip(dims,indices)]
        for tkey in series['observations']:
            time=decode(times[0]['values'][int(tkey)])
            observed.append(tuple(series_vals+[time]))
    expected=[tuple(str(row.get(n)) for n in names) for row in plain]
    only_plain=list((Counter(expected)-Counter(observed)).elements())
    only_sdmx=list((Counter(observed)-Counter(expected)).elements())
    print(f'\n{dataset}: tabular={len(plain)}, reconstructed={len(observed)}')
    print('Dimensions:',', '.join(names))
    print('Unmatched tabular keys:',len(only_plain),'unmatched SDMX keys:',len(only_sdmx))
    for title,rows in [('Tabular only',only_plain),('SDMX only',only_sdmx)]:
        for key in rows[:3]:
            print(' ',title,dict(zip(names,key)))
    if only_plain and only_sdmx:
        print('First mismatching pair by dimension:')
        for name,a,b in zip(names,only_plain[0],only_sdmx[0]):
            if a != b: print(f'  {name}: tabular={a!r} SDMX={b!r}')
    return not only_plain and not only_sdmx

def main():
    print('ILOSTAT independent key diagnostic (read-only)')
    print('Endpoint:',BASE)
    with requests.Session() as session:
        for dataset in DATASETS:
            try:
                ok=run(session,dataset)
                print('Result:', 'MATCH' if ok else 'MISMATCH')
            except Exception as e:
                print(f'{dataset}: ERROR {type(e).__name__}: {e}')
    return 0

if __name__=='__main__':
    sys.exit(main())
