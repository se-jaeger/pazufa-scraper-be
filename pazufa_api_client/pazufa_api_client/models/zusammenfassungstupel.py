from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="Zusammenfassungstupel")



@_attrs_define
class Zusammenfassungstupel:
    """ 
        Attributes:
            typ (str | Unset): Type of summary, if the summary is made up of parts Example: Basisinformationen.
            inhalt (str | Unset): Content of the Summary part Example: Das Gesetz zur Haarfärbeverordnung dient der
                Umsetzung der EU-Richtline 42/69420 zur Schuppenfreiheit bei Eigenschaftsänderlichen Haarmodifikationen vor....
     """

    typ: str | Unset = UNSET
    inhalt: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        typ = self.typ

        inhalt = self.inhalt


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if typ is not UNSET:
            field_dict["typ"] = typ
        if inhalt is not UNSET:
            field_dict["inhalt"] = inhalt

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        typ = d.pop("typ", UNSET)

        inhalt = d.pop("inhalt", UNSET)

        zusammenfassungstupel = cls(
            typ=typ,
            inhalt=inhalt,
        )


        zusammenfassungstupel.additional_properties = d
        return zusammenfassungstupel

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
