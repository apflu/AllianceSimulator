from __future__ import annotations

import httpx

from alliancesim.adapters.outbound.notifications.discord import notification_text
from alliancesim.application.models import PendingNotification
from alliancesim.application.notifications import NotificationDeliveryError
from alliancesim.domain.identity import Platform

TELEGRAM_API = "https://api.telegram.org"


class TelegramNotificationSender:
    def __init__(
        self,
        token: str,
        *,
        api_base: str = TELEGRAM_API,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._token = token
        self._api_base = api_base.rstrip("/")
        self._transport = transport

    async def send(self, notification: PendingNotification) -> None:
        if notification.platform is not Platform.TELEGRAM:
            raise ValueError(f"unsupported notification platform: {notification.platform}")
        try:
            async with httpx.AsyncClient(
                base_url=self._api_base,
                timeout=10,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    f"/bot{self._token}/sendMessage",
                    json={
                        "chat_id": notification.platform_user_id,
                        "text": notification_text(notification),
                    },
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise NotificationDeliveryError(
                f"Telegram API returned HTTP {error.response.status_code}"
            ) from None
        except httpx.HTTPError as error:
            raise NotificationDeliveryError(
                f"Telegram API request failed ({type(error).__name__})"
            ) from None
