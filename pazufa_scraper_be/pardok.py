from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import date, datetime
from typing import Annotated, Any, Literal, Self, get_args

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, HttpUrl, PrivateAttr, ValidationError, model_validator

logger = logging.getLogger(__name__)


def parse_german_date(date_or_str: date | str) -> date:
    if isinstance(date_or_str, date):
        return date_or_str

    return datetime.strptime(date_or_str, "%d.%m.%Y").date()


def ensure_list(value: Any | list) -> list:
    return value if isinstance(value, list) else [value]


def ignore_invalid_factory(cls: type[BaseModel]) -> Callable[tuple[type[BaseModel]], list]:
    def return_function(items: list[Any]) -> list[type[BaseModel]]:
        result = []
        for item in items:
            try:
                result.append(cls.model_validate(item))

            except ValidationError:
                msg = f"Ignoring invalid {cls.__name__}: {item}"
                logger.warning(msg)

        return result

    return return_function


GermanDate = Annotated[date, BeforeValidator(parse_german_date)]
CoercedStrList = Annotated[list[str], BeforeValidator(ensure_list)]


class BaseGesetzDokument(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always", populate_by_name=True)
    _vorgang: GesetzVorgang | None = PrivateAttr(default=None)

    art: str = Field(alias="DokArt")
    art_l: str = Field(alias="DokArtL")

    herk: str = Field(alias="DHerk")
    herk_l: str = Field(alias="DHerkL")

    typ: str = Field(alias="DokTyp")
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
            "ABespr § 21 Abs. 3 GO": "Ausschussbesprechung § 21 Abs. 3 GO",
            "ABespr": "Ausschussbesprechung",
            "Antr (GesEntw)": "Antrag (Gesetzentwurf)",
            "Antr": "Antrag",
            "Ausschussberatung": "Ausschussberatung",
            "ABericht (Zwischenbericht)": "Ausschussbericht (Zwischenbericht)",
            "Behandlung im Plenum": "Behandlung im Plenum",
            "Bekannt (GVBl)": "Bekanntmachung (Gesetz- und Verordnungsblatt)",
            "BeschlEmpf": "Beschlussempfehlung",
            "GVBl": "Gesetz- und Verordnungsblatt",
            "I. Lesung": "I. Lesung",
            "II. Lesung": "II. Lesung",
            "III. Lesung": "III. Lesung",
            "Neufassung": "Neufassung",
            "VorlBeschl": "Vorlage zur Beschlussfassung",
            "VorlBeschl (GesEntw)": "Vorlage zur Beschlussfassung (Gesetzentwurf)",
            "VorlBeschl (GesEntwErg)": "Vorlage zur Beschlussfassung (Gesetzentwurf/Ergänzung)",
            "ÄndAntr": "Änderungsantrag",
        }
        if self.typ_l != mapping.get(self.typ):
            msg = f"DokTypL is not as expected by given DokTyp: '{self.typ_l}'"
            logger.warning(msg)

        return self

    @model_validator(mode="after")
    def ensure_valid_DokArt_to_DokArtL_mapping(self) -> Self:
        mapping = {
            "PlPr": "Plenarprotokoll",
            "APr": "Ausschussprotokoll",
            "GVBl": "Gesetz- und Verordnungsblatt",
            "Drs": "Drucksache",
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
AnyGesetzDokumentField = Annotated[AnyGesetzDokument, Field(discriminator="art")]


def parse_dokument(data: dict | AnyGesetzDokument) -> AnyGesetzDokument:
    if isinstance(data, get_args(AnyGesetzDokument)):
        return data

    if not isinstance(data, dict):
        msg = f"Expected dict, got {type(data)}"
        raise TypeError(msg)

    art = data.get("DokArt")
    mapping: dict[str, type[AnyGesetzDokument]] = {
        "PlPr": PlPrDokument,
        "APr": APrDokument,
        "GVBl": GVBlDokument,
        "Drs": DrsDokument,
    }
    Dokument = mapping.get(art)

    if Dokument is None:
        msg = f"Unknown DokArt: {art}. Has to be one of: {', '.join(mapping.keys())}."
        raise ValueError(msg)

    return Dokument(**data)


# NOTE: https://www.parlament-berlin.de/media/download/4322
class GesetzVorgang(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always", populate_by_name=True)

    typ: str = Field(alias="VTyp")
    typ_l: str = Field(alias="VTypL")

    id: str = Field(alias="VID")
    reih_nr: int = Field(alias="ReihNr", ge=0, lt=1)
    nr: str = Field(alias="VNr")
    sys: CoercedStrList = Field(alias="VSys", default_factory=list)
    sys_l: CoercedStrList = Field(alias="VSysL", default_factory=list)
    ir: str = Field(alias="VIR")
    nebeneintraege: Annotated[
        list[Nebeneintrag],
        # NOTE: Order of validators is crucial - last runs first.
        BeforeValidator(ignore_invalid_factory(Nebeneintrag)),
        BeforeValidator(ensure_list),
    ] = Field(alias="Nebeneintrag", default_factory=list)
    dokumente: Annotated[
        list[AnyGesetzDokumentField],
        # NOTE: Order of validators is crucial - last runs first.
        BeforeValidator(lambda dokumente: [parse_dokument(dokument) for dokument in dokumente]),
        BeforeValidator(ensure_list),
    ] = Field(alias="Dokument", default_factory=list)

    @model_validator(mode="after")
    def ensure_VID_equals_VNr(self) -> Self:
        if self.id != self.nr:
            msg = "'VID' is expected to be equal to 'VNr'"
            raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def ensure_VIR_is_X(self) -> Self:
        if self.ir != "X":
            msg = "'VIR' is expected to be 'X'"
            raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def ensure_valid_VTyp_to_VTypL_mapping(self) -> Self:
        mapping = {"Gesetz": "Gesetzgebung"}
        if self.typ_l != mapping[self.typ]:
            msg = "'VTypL' is not as expected by given 'VTyp'"
            raise ValueError(msg)

        return self

    def model_post_init(self, _context: Any) -> None:
        for dokument in self.dokumente:
            dokument._vorgang = self
