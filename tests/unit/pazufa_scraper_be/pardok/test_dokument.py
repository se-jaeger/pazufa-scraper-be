from typing import Any

import pytest

from pazufa_scraper_be.pardok.dokument import (
    AnyGesetzDokument,
    APrDokument,
    BaseGesetzDokument,
    DokTyp,
    DrsDokument,
    GVBlDokument,
    PlPrDokument,
    parse_dokument,
)


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


def test_all_urls_with_additional_variants(base_dok_data: dict[str, Any]) -> None:
    """Test different input types for additional_urls validator."""
    # Case 1: empty list should be converted to None
    data_empty = base_dok_data.copy()
    data_empty["additional_urls"] = []
    doc_empty = BaseGesetzDokument.model_validate(data_empty)
    assert doc_empty.additional_urls is None

    # Case 2: string should be converted to list of one string
    data_str = base_dok_data.copy()
    data_str["additional_urls"] = "https://extra.com"
    doc_str = BaseGesetzDokument.model_validate(data_str)
    assert isinstance(doc_str.additional_urls, list)
    assert [str(url).rstrip("/") for url in doc_str.additional_urls] == ["https://extra.com"]

    # Case 3: list should remain list
    data_list = base_dok_data.copy()
    data_list["additional_urls"] = ["https://extra1.com", "https://extra2.com"]
    doc_list = BaseGesetzDokument.model_validate(data_list)
    assert isinstance(doc_list.additional_urls, list)
    assert [str(url).rstrip("/") for url in doc_list.additional_urls] == ["https://extra1.com", "https://extra2.com"]


def test_vorgang_runtime_error(base_dok_data: dict[str, Any]) -> None:
    """Accessing vorgang on a standalone document raises RuntimeError."""
    doc = BaseGesetzDokument.model_validate(base_dok_data)
    with pytest.raises(RuntimeError, match="Dokument is standalone"):
        _ = doc.vorgang


def test_drs_dokument_post_init_urheber(drs_data: dict[str, Any]) -> None:
    """DrsDokument should set Urheber to Landesregierung for specific DokTyps."""
    # Case 1: VorlBeschl_GesEntw
    data_1 = drs_data.copy()
    data_1["DokTyp"] = DokTyp.VorlBeschl_GesEntw.value
    doc_1 = DrsDokument.model_validate(data_1)
    assert doc_1.urheber == ["Landesregierung"]

    # Case 2: VorlBeschl_GesEntwErg
    data_2 = drs_data.copy()
    data_2["DokTyp"] = DokTyp.VorlBeschl_GesEntwErg.value
    doc_2 = DrsDokument.model_validate(data_2)
    assert doc_2.urheber == ["Landesregierung"]

    # Case 3: Other type should keep original urheber
    data_3 = drs_data.copy()
    data_3["DokTyp"] = "Antr"
    data_3["Urheber"] = ["Some Other"]
    doc_3 = DrsDokument.model_validate(data_3)
    assert doc_3.urheber == ["Some Other"]
