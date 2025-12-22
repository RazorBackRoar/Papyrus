import importlib


def test_import_package():
    pkg = importlib.import_module("papyrus")
    assert pkg is not None
