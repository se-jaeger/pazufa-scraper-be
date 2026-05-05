from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pazufa_api_client.models import Autor, Doktyp, Gremium, Parlament, Stationstyp
from pazufa_api_client.models import Dokument as PaZuFaDokument
from pazufa_api_client.types import UNSET, Unset

from pazufa_scraper_be.constants import (
    FILE_BYTE_HASH_FILE_NAME,
    LAST_MODIFIED_FILE_NAME,
    SUMMARY_FILE_NAME,
    TEXT_FILE_NAME,
)
from pazufa_scraper_be.pardok import APrDokument, BaseGesetzDokument, DokTyp, DrsDokument, GVBlDokument, PlPrDokument
from pazufa_scraper_be.pardok.dokument import AusschussprotokollTyp

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from pydantic import HttpUrl

logger = logging.getLogger(__name__)


def get_dokument_drucksnr(dokument: BaseGesetzDokument, dokument_cache_dir: Path | None) -> str:
    if isinstance(dokument, (DrsDokument, PlPrDokument)):
        return dokument.nr

    # Ausschussprotokolle append their type abbreviation to avoid Backend treating them as the same document due to the same Nr.
    if isinstance(dokument, APrDokument):
        return f"{dokument.nr}{f'-{dokument_cache_dir.name[-2:]}' if dokument_cache_dir else ''}"

    if isinstance(dokument, GVBlDokument):
        return f"{dokument.h_nr}/{dokument.jg}"

    return ""


def get_dokument_titel(dokument: BaseGesetzDokument, dokument_cache_dir: Path) -> str:
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

    # TODO: log
    return dokument.art_l


def get_dokument_autoren(dokument: BaseGesetzDokument) -> list[Autor]:
    autoren = []

    for urheber in getattr(dokument, "urheber", []):
        urheber = re.sub(r" \(federführend\)", "", urheber, flags=re.IGNORECASE).strip()
        if isinstance(dokument, APrDokument) and not bool(re.search("ausschuss", urheber, flags=re.IGNORECASE)):
            continue

        autoren.append(
            Autor(
                organisation=urheber,
            )
        )

    return autoren


def get_station_gremium(dokument: BaseGesetzDokument) -> tuple[Gremium, bool | Unset]:
    if isinstance(dokument, DrsDokument):
        gremium_name = f"{', '.join(dokument.urheber[:-1])}{f' und {dokument.urheber[-1]}' if len(dokument.urheber) > 1 else ''}"
        gremium_federf = UNSET

    # NOTE: It should always be a single value with Ausschuss name, so we take the first that fit
    if isinstance(dokument, APrDokument):
        gremium_name = ""
        for x in dokument.urheber:
            if bool(re.search("ausschuss", x, flags=re.IGNORECASE)):
                gremium_name = x
                break

        if bool(re.search("federführend", gremium_name, flags=re.IGNORECASE)):
            gremium_name = re.sub(r" \(federführend\)", "", gremium_name, flags=re.IGNORECASE).strip()
            gremium_federf = True

        else:
            gremium_name = gremium_name.strip()
            gremium_federf = False

    elif isinstance(dokument, PlPrDokument):
        gremium_name = "Plenum"
        gremium_federf = UNSET

    elif isinstance(dokument, GVBlDokument):
        gremium_name = "Gesetzesblatt"
        gremium_federf = UNSET

    gremium = Gremium(
        parlament=Parlament.BE,
        wahlperiode=dokument.wp,
        name=gremium_name,
        link=UNSET,
    )

    return gremium, gremium_federf


def get_station_typ(dokument: BaseGesetzDokument) -> Stationstyp:
    if isinstance(dokument, DrsDokument):
        # NOTE: This is usually the Senate/Govermant
        if dokument.typ == DokTyp.VorlBeschl_GesEntw:
            return Stationstyp.PARL_INITIATIV

        # NOTE: This is from any member of the Plenum
        if dokument.typ == DokTyp.Antr_GesEntw:
            return Stationstyp.PARL_INITIATIV

    elif isinstance(dokument, PlPrDokument):
        return Stationstyp.PARL_VOLLVLSGN

    elif isinstance(dokument, APrDokument):
        return Stationstyp.PARL_AUSSCHBER

    if isinstance(dokument, GVBlDokument):
        return Stationstyp.POSTPARL_GSBLT

    msg = f"[{dokument.vorgang.id} - {dokument.id}]: Using fallback for Stationstyp!"
    logger.warning(msg)
    return Stationstyp.SONSTIG


def build_pazufa_dokument(dokument: BaseGesetzDokument, dokument_cache_dir: Path | None, url: HttpUrl) -> PaZuFaDokument | None:
    if dokument_cache_dir is None:
        return None

    text_file = dokument_cache_dir / TEXT_FILE_NAME
    summary_file = dokument_cache_dir / SUMMARY_FILE_NAME
    last_modified_file = dokument_cache_dir / LAST_MODIFIED_FILE_NAME
    file_byte_hash_file = dokument_cache_dir / FILE_BYTE_HASH_FILE_NAME

    # TODO
    doktyp_mapping = {
        DokTyp.Antr_GesEntw: Doktyp.ANTRAG,
        DokTyp.Antr: Doktyp.ANTRAG,
        DokTyp.Behandlung_im_Plenum: Doktyp.REDEPROTOKOLL,
        DokTyp.Bekannt_GVBl: Doktyp.SONSTIG,
        DokTyp.BeschlEmpf: Doktyp.BESCHLUSSEMPF,
        DokTyp.GVBl: Doktyp.SONSTIG,
        DokTyp.Lesung_I: Doktyp.REDEPROTOKOLL,
        DokTyp.Lesung_II: Doktyp.REDEPROTOKOLL,
        DokTyp.Lesung_III: Doktyp.REDEPROTOKOLL,
        DokTyp.VorlBeschl: Doktyp.BESCHLUSSEMPF,
        DokTyp.VorlBeschl_GesEntw: Doktyp.BESCHLUSSEMPF,
        DokTyp.VorlBeschl_GesEntwErg: Doktyp.BESCHLUSSEMPF,
        DokTyp.Antr: Doktyp.ANTRAG,
    }

    if text_file.exists():
        volltext = text_file.read_text()

    else:
        msg = f"[{dokument.vorgang.id} - {dokument.id}]: Text file does not exist, ignoring Dokument!"
        logger.warning(msg)
        return None

    if summary_file.exists():
        zusammenfassung = summary_file.read_text()

    else:
        msg = f"[{dokument.vorgang.id} - {dokument.id}]: Summary file does not exist!"
        logger.info(msg)
        zusammenfassung = UNSET

    if file_byte_hash_file.exists():
        hash_ = file_byte_hash_file.read_text()

    else:
        msg = f"[{dokument.vorgang.id} - {dokument.id}]: Hash file does not exist, ignoring Dokument!"
        logger.warning(msg)
        return None

    # TODO: check if this can be handgled by pardok model
    date = datetime(dokument.dat.year, dokument.dat.month, dokument.dat.day, tzinfo=UTC) if dokument.dat is not None else datetime.now(tz=UTC)

    if last_modified_file.exists():
        dt = datetime.fromisoformat(last_modified_file.read_text())
        modified_date = datetime(dt.year, dt.month, dt.day, tzinfo=UTC)

    else:
        modified_date = date

    return PaZuFaDokument(
        typ=doktyp_mapping.get(dokument.typ, Doktyp.SONSTIG),
        titel=get_dokument_titel(dokument, dokument_cache_dir),
        volltext=volltext,
        zp_referenz=date,
        zp_modifiziert=modified_date,
        link=str(url),
        hash_=hash_,
        autoren=get_dokument_autoren(dokument),
        drucksnr=get_dokument_drucksnr(dokument, dokument_cache_dir),
        kurztitel=UNSET,  # TODO
        vorwort=UNSET,  # TODO
        zusammenfassung=zusammenfassung,
        zp_erstellt=UNSET,
        meinung=UNSET,  # TODO: 1-5 or None
        schlagworte=UNSET,  # TODO:
    )


@dataclass
class DokumentContainer:
    pardok: BaseGesetzDokument
    pazufa: list[PaZuFaDokument]


@dataclass
class Rule:
    name: str
    when: Callable[[DokumentContainer], bool]

    def __call__(self, item: DokumentContainer) -> bool:
        return self.when(item)


@dataclass
class DropRule(Rule):
    pass


@dataclass
class ChangeRule(Rule):
    change_function: Callable[[DokumentContainer], DokumentContainer]


def merge_function(current: DokumentContainer, target: DokumentContainer) -> DokumentContainer:
    abstract = ((target.pardok.abstract or "") + "\n\n" + (current.pardok.abstract or "")).strip()
    target.pardok.abstract = abstract or None
    return DokumentContainer(pardok=target.pardok, pazufa=target.pazufa + current.pazufa)


@dataclass
class _MergeRule(Rule):
    merge_into: Callable[[DokumentContainer, DokumentContainer], bool]
    merge_function: Callable[[DokumentContainer, DokumentContainer], DokumentContainer] = merge_function


@dataclass
class ForwardMergeRule(_MergeRule):
    pass


@dataclass
class BackwardMergeRule(_MergeRule):
    pass


def flush_pending_forward_rules(pending: list[tuple[DokumentContainer, ForwardMergeRule]], current: DokumentContainer) -> tuple[list, DokumentContainer]:
    remaining = []
    for pending_item, pending_rule in pending:
        if pending_rule.merge_into(pending_item, current):
            current = pending_rule.merge_function(pending_item, current)

        else:
            remaining.append((pending_item, pending_rule))

    return remaining, current


def apply_rules(pardok_pazufa_doks: list[DokumentContainer], rules: Sequence[Rule]) -> list[DokumentContainer]:

    result: list[DokumentContainer] = []
    pending: list[tuple[DokumentContainer, ForwardMergeRule]] = []

    for index, current in enumerate(pardok_pazufa_doks):
        pending, current = flush_pending_forward_rules(pending=pending, current=current)

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

                    case ChangeRule():
                        rule_applied = True
                        # TODO

                    case DropRule():
                        rule_applied = True
                        break

        if not rule_applied:
            result.append(current)

    if len(pending) > 0:
        msg = f"[{pardok_pazufa_doks[0].pardok.vorgang.id}]: Did not consume all pending items."
        logger.warning(msg)

    return result
