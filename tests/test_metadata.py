import sys
import importlib


import doiget.metadata


def test_lmdb(monkeypatch):

    monkeypatch.setitem(sys.modules, "lmdb", None)

    importlib.reload(doiget.metadata)

    assert not doiget.metadata.HAS_LMDB

