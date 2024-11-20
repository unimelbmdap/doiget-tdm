import sys
import importlib
import pathlib
import json

import pytest

import requests

import doiget_tdm.doi
import doiget_tdm.metadata


def test_lmdb(monkeypatch):

    monkeypatch.setitem(sys.modules, "lmdb", None)

    importlib.reload(doiget_tdm.metadata)

    assert not doiget_tdm.metadata.HAS_LMDB


def test_api_get(monkeypatch):

    test_data_path = (
        pathlib.Path(__file__).parent.parent
        / "test_data"
        / "example_crossref_metadata.json"
    )

    test_data = test_data_path.read_bytes()

    test_data_json = json.loads(test_data)

    def mock_call(*args, **kwargs):
        response = requests.Response()

        response._content = test_data

        return response

    client = doiget_tdm.metadata.CrossRefWebAPIClient()

    monkeypatch.setattr(client._api, "call", mock_call)

    metadata = client.get_doi_metadata(
        doi=doiget_tdm.doi.DOI(doi="10.7717/peerj.1038")
    )

    assert metadata == json.dumps(test_data_json["message"]).encode()

    # bad status
    test_data_json["status"] = "not_ok"
    test_data = json.dumps(test_data_json).encode()

    with pytest.raises(ValueError):
        metadata = client.get_doi_metadata(
            doi=doiget_tdm.doi.DOI(doi="10.7717/peerj.1038")
        )

    # no status
    del test_data_json["status"]

    test_data = json.dumps(test_data_json).encode()

    with pytest.raises(ValueError):
        metadata = client.get_doi_metadata(
            doi=doiget_tdm.doi.DOI(doi="10.7717/peerj.1038")
        )

    # no message
    test_data_json["status"] = "ok"
    del test_data_json["message"]

    test_data = json.dumps(test_data_json).encode()

    with pytest.raises(ValueError):
        metadata = client.get_doi_metadata(
            doi=doiget_tdm.doi.DOI(doi="10.7717/peerj.1038")
        )

    # empty message
    test_data_json["message"] = ""

    test_data = json.dumps(test_data_json).encode()

    with pytest.raises(ValueError):
        metadata = client.get_doi_metadata(
            doi=doiget_tdm.doi.DOI(doi="10.7717/peerj.1038")
        )
