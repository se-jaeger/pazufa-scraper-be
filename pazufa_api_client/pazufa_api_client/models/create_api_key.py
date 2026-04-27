from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.create_api_key_scope import CreateApiKeyScope
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="CreateApiKey")



@_attrs_define
class CreateApiKey:
    """ Requests a new API key. The key will be saved as hash in the database and only produced once in clear text.

        Attributes:
            scope (CreateApiKeyScope):
            expires_at (datetime.datetime | Unset): The expiration date of the API Key Example: 2024-12-31T23:59:59+00:00.
     """

    scope: CreateApiKeyScope
    expires_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        scope = self.scope.value

        expires_at: str | Unset = UNSET
        if not isinstance(self.expires_at, Unset):
            expires_at = self.expires_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "scope": scope,
        })
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        scope = CreateApiKeyScope(d.pop("scope"))




        _expires_at = d.pop("expires_at", UNSET)
        expires_at: datetime.datetime | Unset
        if isinstance(_expires_at,  Unset):
            expires_at = UNSET
        else:
            expires_at = isoparse(_expires_at)




        create_api_key = cls(
            scope=scope,
            expires_at=expires_at,
        )


        create_api_key.additional_properties = d
        return create_api_key

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
