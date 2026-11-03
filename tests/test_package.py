from importlib.metadata import version

import ilostat


def test_version():
    assert ilostat.__version__ == version("ilostat")