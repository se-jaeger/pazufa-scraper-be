from __future__ import annotations

import logging
import re
import uuid
from typing import Self

from pazufa_api_client.models import Station, Stationstyp, VgIdent, Vorgang, Vorgangstyp
from pazufa_api_client.models import Vorgang as PaZuFaVorgang
from pazufa_api_client.types import UNSET
from scrapy.exceptions import DropItem

from pazufa_scraper_be.pardok import APrDokument, DokTyp, DrsDokument, GesetzVorgang, GVBlDokument, PlPrDokument
from pazufa_scraper_be.pipelines._base import CacheDirPipeline
from pazufa_scraper_be.pipelines.documents.utils.build import (
    BackwardMergeRule,
    DokumentContainer,
    DropRule,
    ForwardMergeRule,
    get_station_gremium,
    get_station_typ,
    process_dokumente,
)

logger = logging.getLogger(__name__)


class BuildPaZuFaVorgang(CacheDirPipeline):
    async def process_item(self: Self, vorgang: GesetzVorgang) -> PaZuFaVorgang:
        if not isinstance(vorgang, GesetzVorgang):
            msg = f"Expected {GesetzVorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        pardok_pazufa_doks = [
            pardok_pazufa_dok
            for pardok_dok in vorgang.dokumente
            if (
                pardok_pazufa_dok := DokumentContainer.from_pardok_dokument(
                    pardok_dokument=pardok_dok, get_dokument_cache_dir_function=self.get_dokument_cache_dir
                )
            )
        ]

        rules = [
            DropRule(
                name="Drop if Vorgang only has Gesetz- und Verordnungsblatt",
                when=lambda current: isinstance(current.pardok, GVBlDokument) and len(current.pardok.vorgang.dokumente) == 1,
            ),
            DropRule(
                name="Drop postponed Lesung",
                when=lambda current: (
                    isinstance(current.pardok, PlPrDokument)
                    and current.pardok.typ == "Behandlung im Plenum"
                    and current.pardok.abstract is not None
                    and bool(re.search("vertagt", str(current.pardok.abstract), flags=re.IGNORECASE))
                ),
            ),
            ForwardMergeRule(
                name="Merge Änderungsantrag onto next Lesung",
                when=lambda current: isinstance(current.pardok, DrsDokument) and current.pardok.typ == DokTyp.AendAntr,
                merge_into=lambda _, target: (
                    isinstance(target.pardok, PlPrDokument) and target.pardok.typ in (DokTyp.Lesung_I, DokTyp.Lesung_II, DokTyp.Lesung_III)
                ),
            ),
            ForwardMergeRule(
                name="Merge Lesungen split into multiple onto last of its kind",
                when=lambda current: isinstance(current.pardok, PlPrDokument) and current.pardok.typ in (DokTyp.Lesung_I, DokTyp.Lesung_II, DokTyp.Lesung_III),
                merge_into=lambda current, target: isinstance(target.pardok, PlPrDokument) and current.pardok.typ == target.pardok.typ,
            ),
            BackwardMergeRule(
                name="Merge Beschlussempfehlung onto prev. Ausschussberatung of the same Ausschuss",
                when=lambda current: isinstance(current.pardok, DrsDokument) and current.pardok.typ == DokTyp.BeschlEmpf,
                merge_into=lambda current, target: isinstance(target.pardok, APrDokument) and current.pazufa[0].autoren == target.pazufa[0].autoren,
            ),
            BackwardMergeRule(
                name="Merge all Gesetz- und Verordnungsblatt onto first one",
                when=lambda current: isinstance(current.pardok, GVBlDokument),
                merge_into=lambda _, target: isinstance(target.pardok, GVBlDokument),
            ),
        ]
        pardok_pazufa_doks = process_dokumente(pardok_pazufa_doks=pardok_pazufa_doks, rules=rules)

        if not pardok_pazufa_doks:
            msg = f"[{vorgang.id}]: Could not create any Stations."
            raise DropItem(msg)

        stationen = []
        for item in pardok_pazufa_doks:
            pardok_dokument = item.pardok
            pazufa_dokumente = item.pazufa

            gremium, gremium_federf = get_station_gremium(dokument=pardok_dokument)
            station = Station(
                zp_start=pazufa_dokumente[0].zp_referenz,
                gremium=gremium,
                typ=get_station_typ(dokument=pardok_dokument),
                dokumente=pazufa_dokumente,
                titel=pardok_dokument.typ_l or UNSET,
                zp_modifiziert=pazufa_dokumente[-1].zp_modifiziert,
                gremium_federf=gremium_federf,
                # link: str | Unset = UNSET
                # trojanergefahr: int | Unset = UNSET
                # schlagworte: list[str] | Unset = UNSET
                # additional_links: list[str] | Unset = UNSET
                # stellungnahmen: list[Dokument | str] | Unset = UNSET
            )
            stationen.append(station)

            if station.typ == Stationstyp.PARL_VOLLVLSGN and pardok_dokument.abstract is not None:
                if bool(re.search("^angenommen|^zustimmung", pardok_dokument.abstract, flags=re.IGNORECASE)):
                    typ = Stationstyp.PARL_AKZEPTANZ

                elif bool(re.search("^abgelehnt", pardok_dokument.abstract, flags=re.IGNORECASE)):
                    typ = Stationstyp.PARL_ABLEHNUNG

                else:
                    typ = None

                if typ:
                    split_station = Station.from_dict(station.to_dict() | {"typ": typ, "titel": "TODO: split station titel"})
                    stationen.append(split_station)

        return Vorgang(
            api_id=uuid.uuid5(self.crawler.settings.get("SCRAPER_UUID"), vorgang.id),
            titel=stationen[0].dokumente[0].titel,
            wahlperiode=self.wahlperiode,
            verfassungsaendernd=False,  # TODO: not set at the moment?
            typ=Vorgangstyp.GG_LAND_PARL,
            initiatoren=stationen[0].dokumente[0].autoren,
            stationen=stationen,
            # kurztitel: str | Unset = UNSET
            ids=[VgIdent(id=vorgang.id, typ="vorgnr")],
            links=[f"https://pardok.parlament-berlin.de/portala/vorgang/{vorgang.id}"],
            # lobbyregister: list[Lobbyregeintrag] | Unset = UNSET
        )
