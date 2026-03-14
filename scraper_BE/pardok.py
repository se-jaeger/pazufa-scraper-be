from datetime import date, datetime
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, BeforeValidator, Field, HttpUrl, RootModel, ValidationError, model_validator


def parse_german_date(date_as_str: str) -> date:
    return datetime.strptime(date_as_str, "%d.%m.%Y").date()


def ensure_list(value: Any | list) -> list:
    return value if isinstance(value, list) else [value]


GermanDate = Annotated[date, BeforeValidator(parse_german_date)]
CoercedStrList = Annotated[list[str], BeforeValidator(ensure_list)]
CoercedUrlList = Annotated[list[HttpUrl], BeforeValidator(ensure_list)]


class BaseGesetzDokument(BaseModel):
    model_config = {"extra": "forbid"}

    art: str
    art_l: str

    herk: str = Field(alias="DHerk")
    herk_l: str = Field(alias="DHerkL")

    typ: str = Field(alias="DokTyp")
    typ_l: str = Field(alias="DokTypL")

    id: str = Field(alias="DBID")
    wp: str = Field(alias="Wp")
    reih_nr: int = Field(alias="ReihNr", gt=0)
    lok_url: str | None = Field(default=None, alias="LokURL")

    nr: str | None = Field(default=None, alias="DokNr")
    abstract: str | None = Field(default=None, alias="Abstract")
    dat: GermanDate | None = Field(default=None, alias="DokDat")

    @model_validator(mode="after")
    def ensure_valid_dok_typ_mapping(self) -> Self:
        mapping = {
            "ABespr § 21 Abs. 3 GO": "Ausschussbesprechung § 21 Abs. 3 GO",
            "Antr (GesEntw)": "Antrag (Gesetzentwurf)",
            "Antr": "Antrag",
            "Ausschussberatung": "Ausschussberatung",
            "Behandlung im Plenum": "Behandlung im Plenum",
            "Bekannt (GVBl)": "Bekanntmachung (Gesetz- und Verordnungsblatt)",
            "BeschlEmpf": "Beschlussempfehlung",
            "GVBl": "Gesetz- und Verordnungsblatt",
            "I. Lesung": "I. Lesung",
            "II. Lesung": "II. Lesung",
            "III. Lesung": "III. Lesung",
            "Neufassung": "Neufassung",
            "VorlBeschl (GesEntw)": "Vorlage zur Beschlussfassung (Gesetzentwurf)",
            "VorlBeschl (GesEntwErg)": "Vorlage zur Beschlussfassung (Gesetzentwurf/Ergänzung)",
            "ÄndAntr": "Änderungsantrag",
        }
        if self.typ_l != mapping[self.typ]:
            msg = "'DokTypL' is not as expected by given 'DokTyp'"
            raise ValidationError(msg)

        return self

    @model_validator(mode="after")
    def ensure_valid_dok_herk_mapping(self) -> Self:
        mapping = {"BLN": "Berlin"}
        if self.herk_l != mapping[self.herk]:
            msg = "'DHerkL' is not as expected by given 'DHerk'"
            raise ValidationError(msg)

        return self


class PlPrDokument(BaseGesetzDokument):
    art: Literal["PlPr"] = Field(default="PlPr", alias="DokArt")
    art_l: Literal["Plenarprotokoll"] = Field(default="Plenarprotokoll", alias="DokArtL")

    sb: str | None = Field(default=None, alias="Sb")
    redner: CoercedStrList = Field(default_factory=list, alias="Redner")


class APrDokument(BaseGesetzDokument):
    art: Literal["APr"] = Field(default="APr", alias="DokArt")
    art_l: Literal["Ausschussprotokoll"] = Field(default="Ausschussprotokoll", alias="DokArtL")

    urheber: CoercedStrList = Field(default_factory=list, alias="Urheber")


class DeskTitelSbMixin:
    desk: str | None = Field(default=None, alias="Desk")
    titel: str | None = Field(default=None, alias="Titel")
    sb: str | None = Field(default=None, alias="Sb")


class GVBlDokument(BaseGesetzDokument, DeskTitelSbMixin):
    art: Literal["GVBl"] = Field(default="GVBl", alias="DokArt")
    art_l: Literal["Gesetz- und Verordnungsblatt"] = Field(default="Gesetz- und Verordnungsblatt", alias="DokArtL")

    vk_dat: GermanDate = Field(alias="VkDat")
    jg: str = Field(alias="Jg")
    h_nr: str | None = Field(default=None, alias="HNr")


class DrsDokument(BaseGesetzDokument, DeskTitelSbMixin):
    art: Literal["Drs"] = Field(default="Drs", alias="DokArt")
    art_l: Literal["Drucksache"] = Field(default="Drucksache", alias="DokArtL")

    urheber: CoercedStrList = Field(default_factory=list, alias="Urheber")


class GesetzDokument(RootModel[Annotated[PlPrDokument | GVBlDokument | APrDokument | DrsDokument, Field(discriminator="art")]]):
    def __getattr__(self, name: str):
        return getattr(self.root, name)

    def __repr__(self):
        return repr(self.root)


class Nebeneintrag(BaseModel):
    reih_nr: int = Field(alias="ReihNr", gt=0)
    desk: str = Field(alias="Desk")


# NOTE: https://www.parlament-berlin.de/media/download/4322
class GesetzVorgang(BaseModel):
    typ: Literal["Gesetz"] = "Gesetz"
    typ_l: Literal["Gesetzgebung"] = "Gesetzgebung"

    id: str = Field(alias="VID")
    reih_nr: int = Field(alias="ReihNr", ge=0, lt=1)
    nr: str = Field(alias="VNr")
    sys: CoercedStrList = Field(alias="VSys", default_factory=list)
    sys_l: CoercedStrList = Field(alias="VSysL", default_factory=list)
    ir: str = Field(alias="VIR")
    nebeneintraege: Annotated[list[Nebeneintrag], BeforeValidator(ensure_list)] = Field(alias="Nebeneintrag", default_factory=list)
    dokumente: Annotated[list[GesetzDokument], BeforeValidator(ensure_list)] = Field(alias="Dokument", default_factory=list)
