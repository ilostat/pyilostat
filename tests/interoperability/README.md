# ILOSTAT independent SDMX interoperability probe

Read-only HTTP and third-party `sdmx1` parser checks. Python 3.10+ recommended.

```powershell
cd H:\_Sys\packages\Python\sdmx-interoperability
py -m pip install -r requirements.txt
py test_interoperability.py
```

A parser failure is reported separately from an HTTP failure: `sdmx1` support for SDMX-ML 3.1 must be verified, and parser incompatibility alone does not prove an ILOSTAT API defect. No production writes.
