from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="VgIdent")



@_attrs_define
class VgIdent:
    """ Unique identifyer for a Vorgang within a parliamend and election period: Vorgangsnummer, Initiativdrucksache, ...

        Example:
            {'id': '20/12345', 'typ': 'initdrucks'}

        Attributes:
            id (str):  Example: 123e4567-e.
            typ (str): Type of an identifyer of a Vorgang. Can contain whatever a parliament uses to identify any complete
                process. Currently in existence: vorgnr, api-id, initdrucks, sonstig. If possible, please do not invent any type
                like `inids`, and use the ones in existence Example: initdrucks.
     """

    id: str
    typ: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        typ = self.typ


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "typ": typ,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        typ = d.pop("typ")

        vg_ident = cls(
            id=id,
            typ=typ,
        )


        vg_ident.additional_properties = d
        return vg_ident

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
