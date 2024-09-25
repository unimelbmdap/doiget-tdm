import pytest

import doiget.doi


EXAMPLE_VALID_DOI = "10.3758/s13414-023-02718-0"
EXAMPLE_VALID_DOI_QUOTED = "10.3758%2Fs13414-023-02718-0"
EXAMPLE_VALID_DOI_2 = "10.1163/22134808-bja10082"


def test_doi() -> None:
    doi = doiget.doi.DOI(doi=EXAMPLE_VALID_DOI)
    doi_from_quoted = doiget.doi.DOI(doi=EXAMPLE_VALID_DOI_QUOTED)

    assert doi == doi_from_quoted


def test_doi_from_url() -> None:
    doiget.doi.DOI.from_url(url="https://doi.org/10.3758/s13414-023-02718-0")


def test_doi_from_url_error() -> None:

    with pytest.raises(ValueError):
        doiget.doi.DOI.from_url(url="https://doi.org/notadoi/111")


def test_doi_equality() -> None:

    doi = doiget.doi.DOI(doi=EXAMPLE_VALID_DOI)

    assert doi == doiget.doi.DOI(doi=EXAMPLE_VALID_DOI)

    another_doi = doiget.doi.DOI(doi=EXAMPLE_VALID_DOI_2)

    assert doi != another_doi


def test_doi_sorting() -> None:

    doi_a = doiget.doi.DOI(doi="10.001/abc2")
    doi_b = doiget.doi.DOI(doi="10.001/abc4")
    doi_c = doiget.doi.DOI(doi="10.001/abc6")

    assert doi_a < doi_b < doi_c

    assert sorted((doi_b, doi_c, doi_a)) == [doi_a, doi_b, doi_c]


def test_doi_dunders() -> None:

    doi = doiget.doi.DOI(doi=EXAMPLE_VALID_DOI)

    str(doi)
    repr(doi)
    hash(doi)


def test_doi_parts() -> None:

    doi = doiget.doi.DOI(doi=EXAMPLE_VALID_DOI)

    (prefix, suffix) = doi.parts

    assert prefix == "10.3758"
    assert suffix == "s13414-023-02718-0"

    assert doi.prefix == prefix
    assert doi.suffix == suffix


def test_doi_parts_multiple_backslash() -> None:

    test_doi = "10.3758/s1234/45/66"

    doi = doiget.doi.DOI(doi=test_doi)

    (prefix, suffix) = doi.parts

    assert prefix == "10.3758"
    assert suffix == "s1234/45/66"


def test_quoted() -> None:

    doi = doiget.doi.DOI(doi=EXAMPLE_VALID_DOI)

    assert doi.quoted == EXAMPLE_VALID_DOI_QUOTED
