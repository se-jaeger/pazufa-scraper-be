from __future__ import annotations

import logging
from enum import StrEnum
from typing import TYPE_CHECKING, Annotated, Literal, Self, get_args

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, HttpUrl, PrivateAttr, model_validator

from pazufa_scraper_be.pardok.utils import CoercedStrList, GermanDate  # noqa: TC001

if TYPE_CHECKING:
    from pazufa_scraper_be.pardok.vorgang import GesetzVorgang

logger = logging.getLogger(__name__)


class DokArt(StrEnum):
    PlPr = "PlPr"
    APr = "APr"
    GVBl = "GVBl"
    Drs = "Drs"


class DokTyp(StrEnum):
    ABespr_Par_21_Abs_3_GO = "ABespr § 21 Abs. 3 GO"
    ABespr = "ABespr"
    Antr_GesEntw = "Antr (GesEntw)"
    Antr = "Antr"
    Ausschussberatung = "Ausschussberatung"
    ABericht_Zwischenbericht = "ABericht (Zwischenbericht)"
    Behandlung_im_Plenum = "Behandlung im Plenum"
    Bekannt_GVBl = "Bekannt (GVBl)"
    BeschlEmpf = "BeschlEmpf"
    GVBl = "GVBl"
    Lesung_I = "I. Lesung"
    Lesung_II = "II. Lesung"
    Lesung_III = "III. Lesung"
    Neufassung = "Neufassung"
    VorlBeschl = "VorlBeschl"
    VorlBeschl_GesEntw = "VorlBeschl (GesEntw)"
    VorlBeschl_GesEntwErg = "VorlBeschl (GesEntwErg)"
    AendAntr = "ÄndAntr"


class BaseGesetzDokument(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always", populate_by_name=True)
    _vorgang: GesetzVorgang | None = PrivateAttr(default=None)

    art: DokArt = Field(alias="DokArt")
    art_l: str = Field(alias="DokArtL")

    herk: str = Field(alias="DHerk")
    herk_l: str = Field(alias="DHerkL")

    typ: DokTyp = Field(alias="DokTyp")
    typ_l: Annotated[str, BeforeValidator(lambda x: "" if type(x) is dict else x)] = Field(alias="DokTypL")

    id: str = Field(alias="DBID")
    wp: int = Field(alias="Wp")
    reih_nr: int = Field(alias="ReihNr", gt=0)
    nr: str = Field(alias="DokNr")
    dat: GermanDate = Field(alias="DokDat")
    abstract: str | None = Field(default=None, alias="Abstract")

    lok_url: HttpUrl = Field(alias="LokURL")
    additional_urls: Annotated[list[HttpUrl] | None, BeforeValidator(lambda v: None if v == [] else [v] if isinstance(v, str) else v)] = Field(default=None)

    @property
    def vorgang(self) -> GesetzVorgang:
        if self._vorgang is None:
            msg = "Dokument is standalone and is not attached to a Vorgang."
            raise RuntimeError(msg)

        return self._vorgang

    @property
    def all_urls(self) -> list[HttpUrl]:
        return ([self.lok_url] if self.lok_url else []) + (self.additional_urls or [])

    @model_validator(mode="after")
    def ensure_valid_DokTyp_to_DokTypL_mapping(self) -> Self:
        mapping = {
            DokTyp.ABespr_Par_21_Abs_3_GO: "Ausschussbesprechung § 21 Abs. 3 GO",
            DokTyp.ABespr: "Ausschussbesprechung",
            DokTyp.Antr_GesEntw: "Antrag (Gesetzentwurf)",
            DokTyp.Antr: "Antrag",
            DokTyp.Ausschussberatung: "Ausschussberatung",
            DokTyp.ABericht_Zwischenbericht: "Ausschussbericht (Zwischenbericht)",
            DokTyp.Behandlung_im_Plenum: "Behandlung im Plenum",
            DokTyp.Bekannt_GVBl: "Bekanntmachung (Gesetz- und Verordnungsblatt)",
            DokTyp.BeschlEmpf: "Beschlussempfehlung",
            DokTyp.GVBl: "Gesetz- und Verordnungsblatt",
            DokTyp.Lesung_I: "I. Lesung",
            DokTyp.Lesung_II: "II. Lesung",
            DokTyp.Lesung_III: "III. Lesung",
            DokTyp.Neufassung: "Neufassung",
            DokTyp.VorlBeschl: "Vorlage zur Beschlussfassung",
            DokTyp.VorlBeschl_GesEntw: "Vorlage zur Beschlussfassung (Gesetzentwurf)",
            DokTyp.VorlBeschl_GesEntwErg: "Vorlage zur Beschlussfassung (Gesetzentwurf/Ergänzung)",
            DokTyp.AendAntr: "Änderungsantrag",
        }
        if self.typ_l != mapping.get(self.typ):
            msg = f"DokTypL is not as expected by given DokTyp: '{self.typ_l}'"
            logger.warning(msg)

        return self

    @model_validator(mode="after")
    def ensure_valid_DokArt_to_DokArtL_mapping(self) -> Self:
        mapping = {
            DokArt.PlPr: "Plenarprotokoll",
            DokArt.APr: "Ausschussprotokoll",
            DokArt.GVBl: "Gesetz- und Verordnungsblatt",
            DokArt.Drs: "Drucksache",
        }
        if self.art_l != mapping[self.art]:
            msg = "'DokArtL' is not as expected by given 'DokArt'"
            raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def ensure_valid_DHerk_to_DHerk_mapping(self) -> Self:
        mapping = {"BLN": "Berlin"}
        if self.herk_l != mapping[self.herk]:
            msg = "'DHerkL' is not as expected by given 'DHerk'"
            raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def ensure_DHerk_is_BLN(self) -> Self:
        if self.herk != "BLN":
            msg = "'DHerk' is expected to be 'BLN'"
            raise ValueError(msg)

        return self


class Protokoll(BaseGesetzDokument):
    lok_url: HttpUrl | None = Field(default=None, alias="LokURL")
    dat: GermanDate | None = Field(default=None, alias="DokDat")


class PlPrDokument(Protokoll):
    art: Literal["PlPr"] = Field(alias="DokArt")

    sb: str | None = Field(default=None, alias="Sb")
    redner: CoercedStrList = Field(default_factory=list, alias="Redner")


class APrDokument(Protokoll):
    art: Literal["APr"] = Field(alias="DokArt")

    urheber: CoercedStrList = Field(default_factory=list, alias="Urheber")


class DeskTitelSbMixin:
    desk: str | None = Field(default=None, alias="Desk")
    titel: str | None = Field(default=None, alias="Titel")
    sb: str | None = Field(default=None, alias="Sb")


class GVBlDokument(BaseGesetzDokument, DeskTitelSbMixin):
    art: Literal["GVBl"] = Field(alias="DokArt")

    vk_dat: GermanDate = Field(alias="VkDat")
    jg: str = Field(alias="Jg")
    h_nr: str = Field(default=None, alias="HNr")
    nr: str | None = Field(default=None, alias="DokNr")


class DrsDokument(BaseGesetzDokument, DeskTitelSbMixin):
    art: Literal["Drs"] = Field(alias="DokArt")

    urheber: CoercedStrList = Field(default_factory=list, alias="Urheber")


class Nebeneintrag(BaseModel):
    reih_nr: int = Field(alias="ReihNr", gt=0)
    desk: str = Field(alias="Desk")


AnyGesetzDokument = PlPrDokument | GVBlDokument | APrDokument | DrsDokument


def parse_dokument(data: dict | AnyGesetzDokument) -> AnyGesetzDokument:
    if isinstance(data, get_args(AnyGesetzDokument)):
        return data

    if not isinstance(data, dict):
        msg = f"Expected dict, got {type(data)}"
        raise TypeError(msg)

    art = data.get("DokArt")
    mapping: dict[str, type[AnyGesetzDokument]] = {
        DokArt.PlPr: PlPrDokument,
        DokArt.APr: APrDokument,
        DokArt.GVBl: GVBlDokument,
        DokArt.Drs: DrsDokument,
    }
    dokument_class = mapping.get(art)

    if dokument_class is None:
        msg = f"Unknown DokArt: {art}. Has to be one of: {', '.join(mapping.keys())}."
        raise ValueError(msg)

    return dokument_class(**data)
