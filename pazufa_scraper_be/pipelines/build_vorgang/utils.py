from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pazufa_corelib.api_client.models import Doktyp, Gremium, Parlament, Stationstyp
from pazufa_corelib.api_client.models import Dokument as PaZuFaDokument
from pazufa_corelib.api_client.types import UNSET, Unset

from pazufa_scraper_be.pardok import APrDokument, BaseGesetzDokument, DrsDokument, GVBlDokument, PlPrDokument

if TYPE_CHECKING:
    from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DokumentContainer:
    """Container pairing a pardok document with its derived PaZuFa documents."""

    pardok: BaseGesetzDokument
    pazufa: list[PaZuFaDokument]


def get_station_typ_and_gremium(dok_container: DokumentContainer) -> tuple[Stationstyp, tuple[Gremium, bool | Unset]]:
    """Extract Stationstyp, Gremium and whether it was 'federführend'."""
    typ = Stationstyp.SONSTIG
    gremium_name = ""
    gremium_federf = UNSET

    if isinstance(dok_container.pardok, DrsDokument) and dok_container.pazufa[0].typ == Doktyp.ENTWURF:
        typ = Stationstyp.PARL_INITIATIV
        gremium_name = "Plenum"

    if isinstance(dok_container.pardok, PlPrDokument):
        typ = Stationstyp.PARL_VOLLVLSGN
        gremium_name = "Plenum"

    if isinstance(dok_container.pardok, APrDokument):
        typ = Stationstyp.PARL_AUSSCHBER

        # NOTE: It should always be a single value with Ausschuss name, so we take the first that fit
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

    if isinstance(dok_container.pardok, GVBlDokument):
        typ = Stationstyp.POSTPARL_GSBLT
        gremium_name = "Gesetzesblatt"
        gremium_federf = UNSET

    gremium = Gremium(
        parlament=Parlament.BE,
        wahlperiode=dok_container.pardok.wp,
        name=gremium_name,
        # NOTE: Following should be revisited
        link=UNSET,
    )

    if typ == Stationstyp.SONSTIG:
        msg = f"[{dok_container.pardok.vorgang.id} - {dok_container.pardok.id}]: Using fallback for Stationstyp."
        logger.info(msg)

    return typ, (gremium, gremium_federf)


def get_station_zeitpunkte(dok_container: DokumentContainer) -> tuple[datetime, datetime]:
    """Extract timestamps relevant for station."""
    zp_start = dok_container.pazufa[0].zp_referenz
    zp_modifiziert = dok_container.pazufa[-1].zp_modifiziert

    if isinstance(dok_container.pardok, GVBlDokument):
        zp_start = dok_container.pardok.vk_dat

    return zp_start, zp_modifiziert
