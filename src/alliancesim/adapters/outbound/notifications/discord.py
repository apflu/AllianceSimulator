from __future__ import annotations

import httpx

from alliancesim.application.models import PendingNotification
from alliancesim.application.notifications import NotificationDeliveryError
from alliancesim.domain.identity import Platform

DISCORD_API = "https://discord.com/api/v10"


def notification_text(notification: PendingNotification) -> str:
    if notification.event_type == "mining_completed":
        material = str(notification.payload["material_id"])
        quantity = int(notification.payload["quantity"])
        suffix = (
            " 使用 /events 处理新发现。" if "event_occurrence_id" in notification.payload else ""
        )
        return f"采矿行动已经完成：联盟库存获得 {quantity} {material}。{suffix}"
    if notification.event_type == "skill_training_completed":
        skill_id = str(notification.payload["skill_id"])
        level = int(notification.payload["level"])
        return f"技能训练已经完成：{skill_id} 达到 {level} 级。"
    return f"联盟发生了新事件：{notification.event_type}"


class DiscordNotificationSender:
    def __init__(
        self,
        token: str,
        *,
        api_base: str = DISCORD_API,
        proxy_url: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._token = token
        self._api_base = api_base.rstrip("/")
        self._proxy_url = proxy_url
        self._transport = transport

    async def send(self, notification: PendingNotification) -> None:
        if notification.platform is not Platform.DISCORD:
            raise ValueError(f"unsupported notification platform: {notification.platform}")
        headers = {"Authorization": f"Bot {self._token}"}
        try:
            async with httpx.AsyncClient(
                base_url=self._api_base,
                headers=headers,
                proxy=self._proxy_url,
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
        except httpx.HTTPStatusError as error:
            raise NotificationDeliveryError(
                f"Discord API returned HTTP {error.response.status_code}"
            ) from None
        except httpx.HTTPError as error:
            raise NotificationDeliveryError(
                f"Discord API request failed ({type(error).__name__})"
            ) from None


class UnavailableNotificationSender:
    async def send(self, notification: PendingNotification) -> None:
        raise NotificationDeliveryError(f"no sender configured for {notification.platform.value}")
