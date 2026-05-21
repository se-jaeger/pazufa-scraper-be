from typing import Any

import pytest

from pazufa_scraper_be.pardok.dokument import AnyGesetzDokument, APrDokument, DrsDokument, GVBlDokument, PlPrDokument, parse_dokument


@pytest.fixture
def base_dok_data() -> dict[str, Any]:
    """Return base fixture data shared by all document type fixtures."""
    return {
        "DokArt": "PlPr",
        "DokArtL": "Plenumsprotokoll",
        "DHerk": "Pardok",
        "DHerkL": "Pardok-System",
        "DokTyp": "Behandlung im Plenum",
        "DokTypL": "Behandlung im Plenum Typ",
        "DBID": "doc123",
        "Wp": 19,
        "ReihNr": 1,
        "DokNr": "123/2024",
        "DokDat": "10.05.2024",
        "Abstract": "This is a test abstract",
        "LokURL": "https://example.com/doc123",
    }


@pytest.fixture
def plpr_data(base_dok_data: dict[str, Any]) -> dict[str, Any]:
    """Return fixture data for a PlPrDokument."""
    return {
        **base_dok_data,
        "DokArt": "PlPr",
        "Sb": "Seite 1",
        "Redner": ["Speaker A", "Speaker B"],
    }


@pytest.fixture
def apr_data(base_dok_data: dict[str, Any]) -> dict[str, Any]:
    """Return fixture data for an APrDokument."""
    return {
        **base_dok_data,
        "DokArt": "APr",
        "Urheber": ["Author A"],
    }


@pytest.fixture
def gvbl_data(base_dok_data: dict[str, Any]) -> dict[str, Any]:
    """Return fixture data for a GVBlDokument."""
    return {
        **base_dok_data,
        "DokArt": "GVBl",
        "VkDat": "11.05.2024",
        "Jg": "2024",
        "HNr": "12345",
        "DokNr": "678",
        "Desk": "Desk GVBl",
        "Titel": "Title GVBl",
        "Sb": "S. 123",
    }


@pytest.fixture
def drs_data(base_dok_data: dict[str, Any]) -> dict[str, Any]:
    """Return fixture data for a DrsDokument."""
    return {
        **base_dok_data,
        "DokArt": "Drs",
        "Urheber": ["Author B"],
        "Desk": "Desk Drs",
        "Titel": "Title Drs",
        "Sb": "S. 456",
    }


@pytest.mark.parametrize(
    ("fixture_name", "expected_class"),
    [
        ("plpr_data", PlPrDokument),
        ("apr_data", APrDokument),
        ("gvbl_data", GVBlDokument),
        ("drs_data", DrsDokument),
    ],
)
def test_parse_dokument_success(request: pytest.FixtureRequest, fixture_name: str, expected_class: type[AnyGesetzDokument]) -> None:
    """parse_dokument returns the correct subtype for each document art."""
    data = request.getfixturevalue(fixture_name)
    result = parse_dokument(data)
    assert isinstance(result, expected_class)
    assert result is not None
    assert result.id == data["DBID"]


def test_parse_dokument_invalid_art(base_dok_data: dict[str, Any]) -> None:
    """parse_dokument raises ValueError for an unrecognised DokArt."""
    invalid_data = base_dok_data.copy()
    invalid_data["DokArt"] = "UnknownArt"
    with pytest.raises(ValueError, match="Unknown DokArt: UnknownArt"):
        parse_dokument(invalid_data)


def test_parse_dokument_validation_error(plpr_data: dict[str, Any]) -> None:
    """parse_dokument returns None when Pydantic validation fails."""
    # Missing required field ReihNr (gt 0) - we can set it to 0
    invalid_data = plpr_data.copy()
    invalid_data["ReihNr"] = 0
    # parse_dokument catches ValidationError and logs it, returning None
    result = parse_dokument(invalid_data)
    assert result is None


def test_parse_dokument_already_model(plpr_data: dict[str, Any]) -> None:
    """parse_dokument returns the same object when passed an existing model."""
    doc = PlPrDokument.model_validate(plpr_data)
    result = parse_dokument(doc)
    assert result is doc


def test_parse_dokument_wrong_type() -> None:
    """parse_dokument raises TypeError for non-dict, non-model input."""
    with pytest.raises(TypeError, match="Expected dict, got"):
        parse_dokument(123)  # type: ignore[ty:invalid-argument-type]


def test_all_urls(plpr_data: dict[str, Any]) -> None:
    """all_urls includes the primary URL and all additional URLs."""
    data = plpr_data.copy()
    data["additional_urls"] = ["https://extra1.com", "https://extra2.com"]
    doc = PlPrDokument(**data)

    expected = [
        "https://example.com/doc123",  # LokURL
        "https://extra1.com/",
        "https://extra2.com/",
    ]
    # all_urls returns a list of HttpUrl, which we can compare as strings or objects
    assert [str(url) for url in doc.all_urls] == expected


def test_all_urls_no_additional(plpr_data: dict[str, Any]) -> None:
    """all_urls returns only the primary URL when no additional URLs are set."""
    doc = PlPrDokument.model_validate(plpr_data)
    assert [str(url) for url in doc.all_urls] == ["https://example.com/doc123"]


def test_vorgang_runtime_error(plpr_data: dict[str, Any]) -> None:
    """Accessing vorgang on a standalone document raises RuntimeError."""
    doc = PlPrDokument.model_validate(plpr_data)
    with pytest.raises(RuntimeError, match="Dokument is standalone"):
        _ = doc.vorgang
