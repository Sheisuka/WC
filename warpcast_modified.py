import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from farcaster import Warpcast
from farcaster.models import (
    CastContent,
    CastReactionsPutResponse,
    CastsGetResponse,
    CastsPostResponse,
    IterableCastsResult,
    Parent,
    ReactionsPutResult,
    StatusContent,
    StatusResponse,
)
from pydantic import PositiveInt


class WarpModified(Warpcast):
    def __init__(
        self,
        mnemonic: str | None = None,
        private_key: str | None = None,
        access_token: str | None = None,
        expires_at: int | None = None,
        rotation_duration: int = 10,
        proxy: str | None = None,
        **data,
    ):
        super().__init__(
            mnemonic, private_key, access_token, expires_at, rotation_duration, **data
        )
        if proxy:
            self.session.proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}",
            }

        self.config.base_path = "https://client.warpcast.com/v2/"
        self.now_time = int(time.time() * 1000)
        self.fc_device_id = str(uuid.uuid4())
        self.fc_amplitude_device_id = str(uuid.uuid4())
        self.session.headers.update(
            {
                "Host": "client.warpcast.com",
                "fc-device-model": "iPhone 14 Pro Max",
                "User-Agent": "mobile-client/400 CFNetwork/1496.0.7 Darwin/23.5.0",
                "fc-native-build-version": "400",
                "fc-device-id": self.fc_device_id,
                "fc-native-application-version": "1.0.74",
                "fc-device-os": "iOS",
                "fc-amplitude-session-id": str(self.now_time),
                "fc-amplitude-device-id": self.fc_amplitude_device_id,
                "Connection": "keep-alive",
                "fc-address": self.wallet.address,
                "Accept-Language": "ru",
                "Accept": "*/*",
                "Content-Type": "application/json; charset=utf-8",
            }
        )

    def _patch(
        self,
        path: str,
        params: Dict[Any, Any] = {},
        json: Dict[Any, Any] = {},
        headers: Dict[Any, Any] = {},
    ) -> Dict[Any, Any]:
        self._check_auth_header()
        logging.debug(f"PATCH {path} {params} {json} {headers}")
        response: Dict[Any, Any] = self.session.patch(
            self.config.base_path + path, params=params, json=json, headers=headers
        ).json()
        if "errors" in response:
            raise Exception(response["errors"])  # pragma: no cover
        return response

    def send_device(self):
        body = {
            "deviceId": self.fc_device_id,
            "deviceModel": "iPhone 14 Pro Max",
            "deviceName": "iPhone",
            "deviceOs": "iOS",
            "notificationsSystemEnabled": True,
        }
        response = self._put("devices", json=body)
        return response

    def casts_wiewed(self, cast_hashes: list):
        body = {
            "castHashes": cast_hashes,
        }
        response = self._put("casts-viewed", json=body)
        return response

    def set_bio_and_display_name(self, bio: str, display_name: str):
        body = {
            "displayName": display_name,
            "bio": bio,
        }
        response = self._patch(
            "me",
            json=body,
        )
        return StatusResponse(**response).result

    def post_cast(
        self,
        text: str,
        embeds: Optional[List[str]] = None,
        parent: Optional[Parent] = None,
    ) -> CastContent:
        body = {
            "text": text,
            "embeds": [],
        }
        if parent:
            body.update(
                {
                    "parent": {"hash": parent},
                }
            )

        response = self._post(
            "casts",
            json=body,
        )
        return CastsPostResponse(**response).result

    def delete_cast(self, cast_hash: str) -> StatusContent:
        body = {"castHash": cast_hash}
        response = self._delete(
            "casts",
            json=body,
        )
        return StatusResponse(**response).result

    def like_cast(self, cast_hash: str) -> ReactionsPutResult:
        body = {"castHash": cast_hash}
        response = self._put(
            "cast-likes",
            json=body,
        )
        return CastReactionsPutResponse(**response).result

    def follow_user(self, fid: PositiveInt) -> StatusContent:
        body = {"targetFid": fid}
        response = self._put(
            "follows",
            json=body,
        )
        return StatusResponse(**response).result

    def get_thread_casts(self, thread_hash: str):
        response = self._get(
            "thread-casts",
            params={
                "castHash": thread_hash,
                "limit": "15",
            },
        )
        return CastsGetResponse(**response).result

    def get_casts(
        self,
        fid: int,
        limit: PositiveInt = 15,
    ) -> IterableCastsResult:
        response = self._get(
            "profile-casts",
            params={"fid": fid, "limit": min(limit, 100)},
        )
        return CastsGetResponse(**response).result
