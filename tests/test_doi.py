import pytest

import doiget_tdm.doi
import doiget_tdm.config


EXAMPLE_VALID_DOI = "10.3758/s13414-023-02718-0"
EXAMPLE_VALID_DOI_QUOTED = "10.3758%2Fs13414-023-02718-0"
EXAMPLE_VALID_DOI_2 = "10.1163/22134808-bja10082"
EXAMPLE_INVALID_DOI = "http://null"


def test_doi() -> None:
    doi = doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI)
    doi_from_quoted = doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI_QUOTED, unquote=True)

    assert doi == doi_from_quoted


def test_doi_group():

    n_groups = 5000

    doi = doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI)

    doi_group = doi.get_group(n_groups=n_groups)

    assert doi_group == "3652"

    doi_from_quoted = doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI_QUOTED, unquote=True)

    doi_from_quoted_group = doi_from_quoted.get_group(n_groups=n_groups)

    assert doi_from_quoted_group == "3652"

    n_groups = None

    doi = doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI)

    doi_group = doi.get_group(n_groups=n_groups)

    assert doi_group == ""


def test_doi_from_url() -> None:
    url = "https://doi.org/10.3758/s13414-023-02718-0"

    doiget_tdm.doi.DOI.from_url(url=url)

    with pytest.raises(ValueError):
        doiget_tdm.doi.DOI(doi=url)


def test_doi_from_url_error() -> None:

    with pytest.raises(ValueError):
        doiget_tdm.doi.DOI.from_url(url="https://doi.org/notadoi/111")


def test_doi_equality() -> None:

    doi = doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI)

    assert doi == doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI)

    another_doi = doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI_2)

    assert doi != another_doi


def test_invalid() -> None:

    with pytest.raises(ValueError):
        doiget_tdm.doi.DOI(doi="123.456/789abc")


def test_doi_sorting() -> None:

    doi_a = doiget_tdm.doi.DOI(doi="10.001/abc2")
    doi_b = doiget_tdm.doi.DOI(doi="10.001/abc4")
    doi_c = doiget_tdm.doi.DOI(doi="10.001/abc6")

    assert doi_a < doi_b < doi_c

    assert sorted((doi_b, doi_c, doi_a)) == [doi_a, doi_b, doi_c]


def test_doi_dunders() -> None:

    doi = doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI)

    str(doi)
    repr(doi)
    hash(doi)


def test_doi_parts() -> None:

    doi = doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI)

    (prefix, suffix) = doi.parts

    assert prefix == "10.3758"
    assert suffix == "s13414-023-02718-0"


def test_doi_parts_multiple_backslash() -> None:

    test_doi = "10.3758/s1234/45/66"

    doi = doiget_tdm.doi.DOI(doi=test_doi)

    (prefix, suffix) = doi.parts

    assert prefix == "10.3758"
    assert suffix == "s1234/45/66"


def test_quoted() -> None:

    doi = doiget_tdm.doi.DOI(doi=EXAMPLE_VALID_DOI)

    assert doi.quoted == EXAMPLE_VALID_DOI_QUOTED


def test_from_input(tmp_path) -> None:

    test_dois = [
        EXAMPLE_VALID_DOI,
        EXAMPLE_VALID_DOI_2,
    ]

    tmp_path_lined = tmp_path / "lined.txt"
    tmp_path_lined.write_text("\n".join(test_dois))

    tmp_path_csv_lower = tmp_path / "lower.txt"
    csv_lower_txt_parts = [
        ["a", "doi", "b"],
        ["afw", EXAMPLE_VALID_DOI, "ggeag"],
        ["sgts", EXAMPLE_VALID_DOI_2, "sgeg"],
    ]
    csv_lower_txt = "\n".join([",".join(row) for row in csv_lower_txt_parts])
    tmp_path_csv_lower.write_text(csv_lower_txt)

    tmp_path_csv_upper = tmp_path / "upper.txt"
    csv_upper_txt_parts = [
        ["a", "DOI", "b"],
        ["afw", EXAMPLE_VALID_DOI, "ggeag"],
        ["sgts", EXAMPLE_VALID_DOI_2, "sgeg"],
    ]
    csv_upper_txt = "\n".join([",".join(row) for row in csv_upper_txt_parts])
    tmp_path_csv_upper.write_text(csv_upper_txt)

    for unquote in [False, True]:

        assert doiget_tdm.doi.form_dois_from_input(
            raw_input=[EXAMPLE_VALID_DOI],
            unquote=unquote,
        ) == [EXAMPLE_VALID_DOI]

        assert (
            doiget_tdm.doi.form_dois_from_input(
                raw_input=test_dois,
                unquote=unquote,
            )
            == test_dois
        )

        assert (
            doiget_tdm.doi.form_dois_from_input(
                raw_input=test_dois + test_dois,
                unquote=unquote,
            )
            == test_dois
        )

        assert (
            doiget_tdm.doi.form_dois_from_input(
                raw_input=[tmp_path_lined],
                unquote=unquote,
            )
            == test_dois
        )

        assert (
            doiget_tdm.doi.form_dois_from_input(
                raw_input=[tmp_path_csv_lower],
                unquote=unquote,
            )
            == test_dois
        )

        assert (
            doiget_tdm.doi.form_dois_from_input(
                raw_input=[tmp_path_csv_upper],
                unquote=unquote,
            )
            == test_dois
        )

        assert doiget_tdm.doi.form_dois_from_input(
            raw_input=[EXAMPLE_VALID_DOI, EXAMPLE_INVALID_DOI],
            unquote=unquote,
        ) == [EXAMPLE_VALID_DOI]
