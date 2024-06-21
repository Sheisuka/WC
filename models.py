from typing import List, Optional

from eth_account.account import Account as Eth_account
from humps import camelize
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(alias_generator=camelize, populate_by_name=True)


class CastsPostRequestModified(BaseModel):
    text: str
    embeds: Optional[List[str]] = None
    parent: Optional[str] = None


class Account(BaseModel):
    display_name: Optional[str] = None
    username: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    language: Optional[str] = None
    post_max_symbol_limit: Optional[int] = None
    shadow_ban: Optional[bool] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    ps: str
    proxy: Optional[str] = None
    role: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.ps and self.address is None:
            Eth_account.enable_unaudited_hdwallet_features()
            self.address = Eth_account.from_mnemonic(self.ps).address

    def to_list_value(self):
        return list(self.model_dump().values())

    def to_list_headers(self):
        return list(self.model_dump().keys())
