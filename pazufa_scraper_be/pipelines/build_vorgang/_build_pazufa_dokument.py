from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pazufa_corelib.api_client.models import Autor, Doktyp
from pazufa_corelib.api_client.models import Dokument as PaZuFaDokument
from pazufa_corelib.api_client.types import UNSET, Unset

from pazufa_scraper_be.constants import (
    FILE_BYTE_HASH_FILE_NAME,
    LAST_MODIFIED_FILE_NAME,
    SUMMARY_FILE_NAME,
    TEXT_FILE_NAME,
)
from pazufa_scraper_be.pardok import APrDokument, BaseGesetzDokument, DokTyp, DrsDokument, GVBlDokument, PlPrDokument
from pazufa_scraper_be.pardok.dokument import AusschussprotokollTyp, DokArt

if TYPE_CHECKING:
    from pathlib import Path

    from pydantic import HttpUrl

logger = logging.getLogger(__name__)


def _get_typ(dokument: BaseGesetzDokument) -> Doktyp:
    """Map a document's art/typ combination to the corresponding PaZuFa DokTyp."""
    doktyp_mapping = {
        # Gesetzentwuerfe
        (DokArt.Drs, DokTyp.Antr_GesEntw): Doktyp.ENTWURF,
        (DokArt.Drs, DokTyp.VorlBeschl_GesEntw): Doktyp.ENTWURF,
        (DokArt.Drs, DokTyp.VorlBeschl_GesEntwErg): Doktyp.ENTWURF,
        # Lesungen
        (DokArt.PlPr, DokTyp.Behandlung_im_Plenum): Doktyp.REDEPROTOKOLL,
        (DokArt.PlPr, DokTyp.Lesung_I): Doktyp.REDEPROTOKOLL,
        (DokArt.PlPr, DokTyp.Lesung_II): Doktyp.REDEPROTOKOLL,
        # Ausschussberatung und Beschlussempfehlung
        (DokArt.APr, DokTyp.Ausschussberatung): Doktyp.REDEPROTOKOLL,
        (DokArt.APr, DokTyp.ABespr_Par_21_Abs_3_GO): Doktyp.REDEPROTOKOLL,
        (DokArt.APr, DokTyp.APr): Doktyp.REDEPROTOKOLL,
        (DokArt.APr, DokTyp.BeschlEmpf): Doktyp.BESCHLUSSEMPF,
        (DokArt.Drs, DokTyp.BeschlEmpf): Doktyp.BESCHLUSSEMPF,
        # Gesetzesblatt
        (DokArt.GVBl, DokTyp.GVBl): Doktyp.SONSTIG,
        (DokArt.GVBl, DokTyp.Bekannt_GVBl): Doktyp.SONSTIG,
        (DokArt.GVBl, DokTyp.Neufassung): Doktyp.SONSTIG,
        # Verschiedenes
        (DokArt.Drs, DokTyp.AendAntr): Doktyp.ANTRAG,
        (DokArt.Drs, DokTyp.Antr): Doktyp.ANTRAG,
    }
    if ret_val := doktyp_mapping.get((dokument.art, dokument.typ)):
        return ret_val

    msg = f"[{dokument.vorgang.id} - {dokument.id}]: Using fallback for DokTyp. Got the following (DokArt, DokTyp): ({dokument.art}, {dokument.typ})"
    logger.info(msg)
    return Doktyp.SONSTIG


def _get_drucksnr(dokument: BaseGesetzDokument, dokument_cache_dir: Path | None) -> str:
    """Return the Drucksachennummer string for a document."""
    if isinstance(dokument, (DrsDokument, PlPrDokument)):
        return dokument.nr

    # Ausschussprotokolle append their type abbreviation to avoid Backend treating them as the same document due to the same Nr.
    if isinstance(dokument, APrDokument):
        return f"{dokument.nr}{f'-{dokument_cache_dir.name[-2:]}' if dokument_cache_dir else ''}"

    if isinstance(dokument, GVBlDokument):
        return f"{dokument.h_nr}/{dokument.jg}"

    return ""


# TODO(se-jaeger): refactor to reduce complexity
def _get_titel(dokument: BaseGesetzDokument, dokument_cache_dir: Path) -> str:  # noqa: PLR0911
    """Derive a human-readable title for a document, falling back to its art label."""
    if hasattr(dokument, "titel") and type(dokument.titel) is str:
        return dokument.titel

    drucksnr = _get_drucksnr(dokument, dokument_cache_dir)
    if isinstance(dokument, APrDokument) and dokument_cache_dir.name.endswith(f"-{AusschussprotokollTyp.Beschluss}"):
        return f"Ausschuss Beschlussprotokoll{f' - {drucksnr}' if drucksnr else ''}"

    if isinstance(dokument, APrDokument) and dokument_cache_dir.name.endswith(f"-{AusschussprotokollTyp.Inhalt}"):
        return f"Ausschuss Inhaltsprotokoll{f' - {drucksnr}' if drucksnr else ''}"

    if isinstance(dokument, APrDokument) and dokument_cache_dir.name.endswith(f"-{AusschussprotokollTyp.Wort}"):
        return f"Ausschuss Wortprotokoll{f' - {drucksnr}' if drucksnr else ''}"

    if isinstance(dokument, DrsDokument) and dokument.typ == DokTyp.BeschlEmpf:
        return f"Ausschuss Beschlussempfehlung{f' - {drucksnr}' if drucksnr else ''}"

    if isinstance(dokument, DrsDokument) and dokument.typ == DokTyp.AendAntr:
        return f"Änderungsantrag{f' - {drucksnr}' if drucksnr else ''}"

    if isinstance(dokument, GVBlDokument):
        return f"Gesetz- und Verordnungsblatt Nr. {drucksnr}"

    if dokument.nr is not None:
        return f"{dokument.art_l} - {dokument.nr}"

    # TODO(se-jaeger): log
    return dokument.art_l


def _get_autoren(dokument: BaseGesetzDokument) -> list[Autor]:
    """Extract and clean the list of Autoren from a document."""
    autoren = []

    for urheber in getattr(dokument, "urheber", []):
        cleaned = re.sub(r" \(federführend\)", "", urheber, flags=re.IGNORECASE).strip()
        if isinstance(dokument, APrDokument) and not bool(re.search("ausschuss", cleaned, flags=re.IGNORECASE)):
            continue

        autoren.append(
            Autor(
                organisation=cleaned,
            )
        )

    return autoren


def _get_zeitpunkte(dokument: BaseGesetzDokument, dokument_cache_dir: Path) -> tuple[Unset | datetime, datetime, datetime]:
    """Extract timestamps relevant for document."""
    last_modified_file = dokument_cache_dir / LAST_MODIFIED_FILE_NAME

    # TODO(anyone): revisit this
    zp_erstellt = UNSET

    if dokument.dat is not None:
        zp_referenz = dokument.dat
    else:
        msg = f"[{dokument.vorgang.id} - {dokument.id}]: Using fallback for document timestamp."
        logger.warning(msg)
        zp_referenz = datetime.now(tz=UTC)

    if last_modified_file.exists():
        dt = datetime.fromisoformat(last_modified_file.read_text())
        zp_modifiziert = datetime(dt.year, dt.month, dt.day, tzinfo=UTC)
    else:
        zp_modifiziert = dokument.dat

    return zp_erstellt, zp_referenz, zp_modifiziert


def build_pazufa_dokument(dokument: BaseGesetzDokument, dokument_cache_dir: Path | None, url: HttpUrl) -> PaZuFaDokument | None:
    """Build a PaZuFaDokument from a cached document, returning None if required files are missing."""
    if dokument_cache_dir is None:
        return None

    text_file = dokument_cache_dir / TEXT_FILE_NAME
    summary_file = dokument_cache_dir / SUMMARY_FILE_NAME
    file_byte_hash_file = dokument_cache_dir / FILE_BYTE_HASH_FILE_NAME

    if text_file.exists():
        volltext = text_file.read_text()

    else:
        msg = f"[{dokument.vorgang.id} - {dokument.id}]: Text file does not exist, ignoring Dokument."
        logger.warning(msg)
        return None

    if summary_file.exists():
        zusammenfassung = summary_file.read_text()

    else:
        msg = f"[{dokument.vorgang.id} - {dokument.id}]: Summary file does not exist."
        logger.info(msg)
        zusammenfassung = UNSET

    if file_byte_hash_file.exists():
        hash_ = file_byte_hash_file.read_text()

    else:
        msg = f"[{dokument.vorgang.id} - {dokument.id}]: Hash file does not exist, ignoring Dokument."
        logger.warning(msg)
        return None

    zp_erstellt, zp_referenz, zp_modifiziert = _get_zeitpunkte(dokument, dokument_cache_dir)

    return PaZuFaDokument(
        typ=_get_typ(dokument),
        titel=_get_titel(dokument, dokument_cache_dir),
        volltext=volltext,
        zp_erstellt=zp_erstellt,
        zp_referenz=zp_referenz,
        zp_modifiziert=zp_modifiziert,
        link=str(url),
        hash_=hash_,
        autoren=_get_autoren(dokument),
        drucksnr=_get_drucksnr(dokument, dokument_cache_dir),
        zusammenfassung=zusammenfassung,
        # NOTE: Following should be revisited
        kurztitel=UNSET,
        vorwort=UNSET,
        meinung=UNSET,
        schlagworte=UNSET,
    )
