from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.dokument_hash_type_1_item_strategy import DokumentHashType1ItemStrategy
from ..models.mime import Mime






T = TypeVar("T", bound="DokumentHashType1Item")



@_attrs_define
class DokumentHashType1Item:
    """ 
        Attributes:
            value (str): Hash value as string of hexadecimal octets
            strategy (DokumentHashType1ItemStrategy): The Strategy used to compute the hash. sha256+text denotes that not
                the raw file, but the _exact_ volltext field of the document was hashed. All text must be utf-8, remain stable
                under subsequent extraction, and mime must be set to text/plain.
            mime (Mime):
     """

    value: str
    strategy: DokumentHashType1ItemStrategy
    mime: Mime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        value = self.value

        strategy = self.strategy.value

        mime = self.mime.value


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "value": value,
            "strategy": strategy,
            "mime": mime,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value")

        strategy = DokumentHashType1ItemStrategy(d.pop("strategy"))




        mime = Mime(d.pop("mime"))




        dokument_hash_type_1_item = cls(
            value=value,
            strategy=strategy,
            mime=mime,
        )


        dokument_hash_type_1_item.additional_properties = d
        return dokument_hash_type_1_item

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
