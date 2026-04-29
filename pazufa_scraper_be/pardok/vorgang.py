from __future__ import annotations

import logging
from typing import Annotated, Any, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator

from pazufa_scraper_be.pardok.dokument import AnyGesetzDokument, parse_dokument
from pazufa_scraper_be.pardok.utils import CoercedStrList, ensure_list, ignore_invalid_factory

logger = logging.getLogger(__name__)


class Nebeneintrag(BaseModel):
    reih_nr: int = Field(alias="ReihNr", gt=0)
    desk: str = Field(alias="Desk")


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
        list[Annotated[AnyGesetzDokument, Field(discriminator="art")]],
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
