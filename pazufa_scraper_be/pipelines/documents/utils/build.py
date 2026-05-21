from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pazufa_corelib.api_client.models import Autor, Doktyp, Gremium, Parlament, Stationstyp
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
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from pydantic import HttpUrl

logger = logging.getLogger(__name__)


def get_dokument_typ(dokument: BaseGesetzDokument) -> Doktyp:
    """Map a document's art/typ combination to the corresponding PaZuFa Doktyp."""
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

    msg = f"[{dokument.vorgang.id} - {dokument.id}]: Using fallback for Doktyp."
    logger.info(msg)
    return Doktyp.SONSTIG


def get_dokument_drucksnr(dokument: BaseGesetzDokument, dokument_cache_dir: Path | None) -> str:
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
def get_dokument_titel(dokument: BaseGesetzDokument, dokument_cache_dir: Path) -> str:  # noqa: PLR0911
    """Derive a human-readable title for a document, falling back to its art label."""
    if hasattr(dokument, "titel") and type(dokument.titel) is str:
        return dokument.titel

    drucksnr = get_dokument_drucksnr(dokument, dokument_cache_dir)
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


def get_dokument_autoren(dokument: BaseGesetzDokument) -> list[Autor]:
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


def get_station_gremium(dok_container: DokumentContainer) -> tuple[Gremium, bool | Unset]:
    """Determine the Gremium and whether it is federführend for a DokumentContainer."""
    if isinstance(dok_container.pardok, DrsDokument):
        gremium_name = (
            f"{', '.join(dok_container.pardok.urheber[:-1])}{f' und {dok_container.pardok.urheber[-1]}' if len(dok_container.pardok.urheber) > 1 else ''}"
        )
        gremium_federf = UNSET

    # NOTE: It should always be a single value with Ausschuss name, so we take the first that fit
    if isinstance(dok_container.pardok, APrDokument):
        gremium_name = ""
        for x in dok_container.pardok.urheber:
            if bool(re.search("ausschuss", x, flags=re.IGNORECASE)):
                gremium_name = x
                break

        if bool(re.search("federführend", gremium_name, flags=re.IGNORECASE)):
            gremium_name = re.sub(r" \(federführend\)", "", gremium_name, flags=re.IGNORECASE).strip()
            gremium_federf = True

        else:
            gremium_name = gremium_name.strip()
            gremium_federf = False

    elif isinstance(dok_container.pardok, PlPrDokument):
        gremium_name = "Plenum"
        gremium_federf = UNSET

    elif isinstance(dok_container.pardok, GVBlDokument):
        gremium_name = "Gesetzesblatt"
        gremium_federf = UNSET

    gremium = Gremium(
        parlament=Parlament.BE,
        wahlperiode=dok_container.pardok.wp,
        name=gremium_name,
        # NOTE: Following should be revisited
        link=UNSET,
    )

    return gremium, gremium_federf


def get_station_zeitpunkte(dok_container: DokumentContainer) -> tuple[datetime, datetime]:
    """Extract timestamps relevant for station."""
    zp_start = dok_container.pazufa[0].zp_referenz
    zp_modifiziert = dok_container.pazufa[-1].zp_modifiziert

    if isinstance(dok_container.pardok, GVBlDokument):
        zp_start = dok_container.pardok.vk_dat

    return zp_start, zp_modifiziert


def get_station_typ(dok_container: DokumentContainer) -> Stationstyp:
    """Map a DokumentContainer to the corresponding PaZuFa Stationstyp."""
    if isinstance(dok_container.pardok, DrsDokument) and dok_container.pazufa[0].typ == Doktyp.ENTWURF:
        return Stationstyp.PARL_INITIATIV

    if isinstance(dok_container.pardok, PlPrDokument):
        return Stationstyp.PARL_VOLLVLSGN

    if isinstance(dok_container.pardok, APrDokument):
        return Stationstyp.PARL_AUSSCHBER

    if isinstance(dok_container.pardok, GVBlDokument):
        return Stationstyp.POSTPARL_GSBLT

    msg = f"[{dok_container.pardok.vorgang.id} - {dok_container.pardok.id}]: Using fallback for Stationstyp."
    logger.info(msg)
    return Stationstyp.SONSTIG


def get_dokument_zeitpunkte(dokument: BaseGesetzDokument, dokument_cache_dir: Path) -> tuple[Unset | datetime, datetime, datetime]:
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

    zp_erstellt, zp_referenz, zp_modifiziert = get_dokument_zeitpunkte(dokument, dokument_cache_dir)

    return PaZuFaDokument(
        typ=get_dokument_typ(dokument),
        titel=get_dokument_titel(dokument, dokument_cache_dir),
        volltext=volltext,
        zp_erstellt=zp_erstellt,
        zp_referenz=zp_referenz,
        zp_modifiziert=zp_modifiziert,
        link=str(url),
        hash_=hash_,
        autoren=get_dokument_autoren(dokument),
        drucksnr=get_dokument_drucksnr(dokument, dokument_cache_dir),
        zusammenfassung=zusammenfassung,
        # NOTE: Following should be revisited
        kurztitel=UNSET,
        vorwort=UNSET,
        meinung=UNSET,
        schlagworte=UNSET,
    )


@dataclass
class DokumentContainer:
    """Container pairing a pardok document with its derived PaZuFa documents."""

    pardok: BaseGesetzDokument
    pazufa: list[PaZuFaDokument]


@dataclass
class Rule:
    """Base rule that evaluates whether a DokumentContainer matches a condition."""

    name: str
    when: Callable[[DokumentContainer], bool]

    def __call__(self, dok_container: DokumentContainer) -> bool:
        """Evaluate the rule's condition against dok_container."""
        return self.when(dok_container)


@dataclass
class DropRule(Rule):
    """Rule that drops matching DokumentContainers from the pipeline."""


@dataclass
class TransformRule(Rule):
    """Rule that transforms a matching DokumentContainer."""

    transform_function: Callable[[DokumentContainer], DokumentContainer]


def merge_function(current: DokumentContainer, target: DokumentContainer) -> DokumentContainer:
    """Merge current into target by concatenating abstracts and combining pazufa document lists."""
    abstract = ((target.pardok.abstract or "") + "\n\n" + (current.pardok.abstract or "")).strip()
    target.pardok.abstract = abstract or None
    return DokumentContainer(pardok=target.pardok, pazufa=target.pazufa + current.pazufa)


@dataclass
class _MergeRule(Rule):
    merge_into: Callable[[DokumentContainer, DokumentContainer], bool]
    merge_function: Callable[[DokumentContainer, DokumentContainer], DokumentContainer] = merge_function


@dataclass
class ForwardMergeRule(_MergeRule):
    """Rule that merges the current container into a subsequent matching container."""


@dataclass
class BackwardMergeRule(_MergeRule):
    """Rule that merges the current container into a preceding matching container."""


def flush_pending_forward_rules(pending: list[tuple[DokumentContainer, ForwardMergeRule]], current: DokumentContainer) -> tuple[list, DokumentContainer]:
    """Apply any pending forward-merge rules that match the current container."""
    remaining = []
    for pending_item, pending_rule in pending:
        if pending_rule.merge_into(pending_item, current):
            current = pending_rule.merge_function(pending_item, current)

        else:
            remaining.append((pending_item, pending_rule))

    return remaining, current


# TODO(se-jaeger): refactor to reduce complexity
def apply_rules(pardok_pazufa_doks: list[DokumentContainer], rules: Sequence[Rule]) -> list[DokumentContainer]:  # noqa: C901, PLR0912
    """Apply the given rules to a list of DokumentContainers, returning the reduced list."""
    result: list[DokumentContainer] = []
    pending: list[tuple[DokumentContainer, ForwardMergeRule]] = []

    for index, item in enumerate(pardok_pazufa_doks):
        pending, current = flush_pending_forward_rules(pending=pending, current=item)

        rule_applied = False
        for rule in rules:
            if rule(current):
                match rule:
                    case ForwardMergeRule():
                        for target in pardok_pazufa_doks[index + 1 :]:
                            if rule.merge_into(current, target):
                                rule_applied = True
                                pending.append((current, rule))
                                break

                    case BackwardMergeRule():
                        for i in reversed(range(len(result))):
                            if rule.merge_into(current, result[i]):
                                rule_applied = True
                                result[i] = rule.merge_function(current, result[i])
                                break

                    case TransformRule():
                        rule_applied = True
                        # TODO(se-jaeger): implement ChangeRule action

                    case DropRule():
                        rule_applied = True
                        break

        if not rule_applied:
            result.append(current)

    if len(pending) > 0:
        msg = f"[{pardok_pazufa_doks[0].pardok.vorgang.id}]: Did not consume all pending items."
        logger.warning(msg)

    return result
