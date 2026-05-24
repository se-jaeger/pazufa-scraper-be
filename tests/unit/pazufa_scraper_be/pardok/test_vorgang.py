from typing import Any

import pytest
from pydantic import ValidationError

from pazufa_scraper_be.pardok.dokument import PlPrDokument
from pazufa_scraper_be.pardok.vorgang import GesetzVorgang, Nebeneintrag


@pytest.fixture
def base_vorgang_data() -> dict[str, Any]:
    """Return base fixture data for a GesetzVorgang."""
    return {
        "VTyp": "Gesetz",
        "VTypL": "Gesetz-Typ",
        "VID": "vorg123",
        "ReihNr": 0,
        "VNr": "V123/2024",
        "VIR": "IR123",
        "VSys": ["Sys1"],
        "VSysL": ["System 1"],
    }


@pytest.fixture
def base_dok_data() -> dict[str, Any]:
    """Return base fixture data for a document."""
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
        "LokURL": "https://example.com/doc123",
    }


def test_nebeneintrag_success() -> None:
    """Nebeneintrag should validate correctly."""
    data = {"ReihNr": 1, "Desk": "Desk A"}
    entry = Nebeneintrag.model_validate(data)
    assert entry.reih_nr == 1
    assert entry.desk == "Desk A"


def test_nebeneintrag_failure() -> None:
    """Nebeneintrag should fail expectedly."""
    data = {"ReihNr": 0, "Desk": "Desk A"}
    with pytest.raises(ValidationError):
        _ = Nebeneintrag.model_validate(data)


def test_gesetzvorgang_success(base_vorgang_data: dict[str, Any], base_dok_data: dict[str, Any]) -> None:
    """GesetzVorgang should instantiate correctly and link documents in model_post_init."""
    invalid_dok = base_dok_data.copy()
    invalid_dok["DBID"] = "bad-doc"
    invalid_dok["ReihNr"] = 0  # Invalid: must be > 0

    data = {
        **base_vorgang_data,
        "Dokument": [base_dok_data, invalid_dok],
        "Nebeneintrag": [
            {"ReihNr": 1, "Desk": "Desk 1"},
            {"ReihNr": 2, "Desk": "Desk 2"},
            {"ReihNr": -1, "Desk": "Desk oops"},  # bad: to be filtered out
        ],
    }
    n_nebeneintraege = len(data["Nebeneintrag"]) - 1

    vorgang = GesetzVorgang.model_validate(data)

    assert vorgang.id == "vorg123"
    assert len(vorgang.dokumente) == 1
    assert isinstance(vorgang.nebeneintraege, list)
    assert vorgang.nebeneintraege[0].desk == "Desk 1"
    assert vorgang.nebeneintraege[1].desk == "Desk 2"
    assert len(vorgang.nebeneintraege) == n_nebeneintraege

    # Test model_post_init: valid documents should be linked back to the vorgang
    assert len(vorgang.dokumente) == 1

    doc = vorgang.dokumente[0]
    assert doc.vorgang is vorgang
    assert doc.id == "doc123"

    # Verify that we can access the vorgang property
    assert doc.vorgang.id == "vorg123"

    # Sanity check mapping
    assert isinstance(doc, PlPrDokument)


def test_gesetzvorgang_invalid_reih_nr(base_vorgang_data: dict[str, Any]) -> None:
    """GesetzVorgang should raise ValidationError if ReihNr is not 0."""
    data = base_vorgang_data.copy()
    data["ReihNr"] = 1
    with pytest.raises(ValidationError):
        GesetzVorgang.model_validate(data)
