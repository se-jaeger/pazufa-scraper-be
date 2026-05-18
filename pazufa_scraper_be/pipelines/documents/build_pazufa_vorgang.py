from __future__ import annotations

import logging
import re
import uuid
from datetime import timedelta
from typing import Self, cast

from pazufa_corelib.api_client.models import Dokument, Station, Stationstyp, VgIdent, Vorgang, Vorgangstyp
from pazufa_corelib.api_client.models import Vorgang as PaZuFaVorgang
from pazufa_corelib.api_client.types import UNSET
from scrapy.exceptions import DropItem

from pazufa_scraper_be.pardok import APrDokument, DokTyp, DrsDokument, GesetzVorgang, GVBlDokument, PlPrDokument
from pazufa_scraper_be.pipelines._base import CacheDirPipeline
from pazufa_scraper_be.pipelines.documents.utils.build import (
    BackwardMergeRule,
    DokumentContainer,
    DropRule,
    ForwardMergeRule,
    apply_rules,
    build_pazufa_dokument,
    get_station_gremium,
    get_station_typ,
)

logger = logging.getLogger(__name__)


class BuildPaZuFaVorgang(CacheDirPipeline):
    async def process_item(self: Self, vorgang: GesetzVorgang) -> PaZuFaVorgang:
        if not isinstance(vorgang, GesetzVorgang):
            msg = f"Expected {GesetzVorgang.__name__} object but got {vorgang.__class__.__name__}."
            raise DropItem(msg)

        dok_containers = []
        for pardok in vorgang.dokumente:
            pazufa = []
            for url in pardok.all_urls:
                if pazufa_dokument := build_pazufa_dokument(dokument=pardok, dokument_cache_dir=self.get_dokument_cache_dir(dokument=pardok, url=url), url=url):
                    pazufa.append(pazufa_dokument)

            if len(pazufa) > 0:
                dok_containers.append(DokumentContainer(pardok, pazufa))

        if len(dok_containers) == 0:
            msg = f"[{vorgang.id}]: Could not create any Dokument from Vorgang."
            raise DropItem(msg)

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
            BackwardMergeRule(
                name="Merge Lesungen split into multiple onto first of its kind",
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
            BackwardMergeRule(
                name="Merge Gesetzentwurf Ergänzung onto initial Gesetzentwurf",
                when=lambda current: isinstance(current.pardok, DrsDokument) and current.pardok.typ == DokTyp.VorlBeschl_GesEntwErg,
                merge_into=lambda _, target: isinstance(target.pardok, DrsDokument) and target.pardok.typ == DokTyp.VorlBeschl_GesEntw,
            ),
        ]

        dok_containers = apply_rules(pardok_pazufa_doks=dok_containers, rules=rules)

        if len(dok_containers) == 0:
            msg = f"[{vorgang.id}]: Could not create any Stations."
            raise DropItem(msg)

        stationen = []
        for dok_container in dok_containers:
            gremium, gremium_federf = get_station_gremium(dok_container)
            station = Station(
                zp_start=dok_container.pazufa[0].zp_referenz,
                gremium=gremium,
                typ=get_station_typ(dok_container),
                dokumente=cast("list[Dokument | str]", dok_container.pazufa),
                titel=dok_container.pardok.typ_l or UNSET,
                zp_modifiziert=dok_container.pazufa[-1].zp_modifiziert,
                gremium_federf=gremium_federf,
                # link: str | Unset = UNSET
                # trojanergefahr: int | Unset = UNSET
                # schlagworte: list[str] | Unset = UNSET
                # additional_links: list[str] | Unset = UNSET
                # stellungnahmen: list[Dokument | str] | Unset = UNSET
            )
            stationen.append(station)

            if station.typ == Stationstyp.PARL_VOLLVLSGN and dok_container.pardok.abstract is not None:
                if bool(re.search("^angenommen|^zustimmung", dok_container.pardok.abstract, flags=re.IGNORECASE)):
                    typ = Stationstyp.PARL_AKZEPTANZ

                elif bool(re.search("^abgelehnt", dok_container.pardok.abstract, flags=re.IGNORECASE)):
                    typ = Stationstyp.PARL_ABLEHNUNG

                else:
                    typ = None

                if typ:
                    new_station = Station.from_dict(station.to_dict() | {"typ": typ, "titel": "TODO: split station titel"})
                    new_station.zp_start = station.zp_start + timedelta(hours=1)
                    stationen.append(new_station)

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
