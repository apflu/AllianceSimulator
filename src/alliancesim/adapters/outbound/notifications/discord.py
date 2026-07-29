from __future__ import annotations

import httpx

from alliancesim.application.models import PendingNotification
from alliancesim.domain.identity import Platform

DISCORD_API = "https://discord.com/api/v10"


def notification_text(notification: PendingNotification) -> str:
    if notification.event_type == "mining_completed":
        material = str(notification.payload["material_id"])
        quantity = int(notification.payload["quantity"])
        return f"采矿行动已经完成：联盟库存获得 {quantity} {material}。"
    return f"联盟发生了新事件：{notification.event_type}"


class DiscordNotificationSender:
    def __init__(
        self,
        token: str,
        *,
        api_base: str = DISCORD_API,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._token = token
        self._api_base = api_base.rstrip("/")
        self._transport = transport

    async def send(self, notification: PendingNotification) -> None:
        if notification.platform is not Platform.DISCORD:
            raise ValueError(f"unsupported notification platform: {notification.platform}")
        headers = {"Authorization": f"Bot {self._token}"}
        async with httpx.AsyncClient(
            base_url=self._api_base,
            headers=headers,
            timeout=10,
            transport=self._transport,
        ) as client:
            channel_response = await client.post(
                "/users/@me/channels", json={"recipient_id": notification.platform_user_id}
            )
            channel_response.raise_for_status()
            channel_id = str(channel_response.json()["id"])
            message_response = await client.post(
                f"/channels/{channel_id}/messages",
                json={"content": notification_text(notification)},
            )
            message_response.raise_for_status()


class UnavailableNotificationSender:
    async def send(self, notification: PendingNotification) -> None:
        raise RuntimeError(f"no sender configured for {notification.platform}")
