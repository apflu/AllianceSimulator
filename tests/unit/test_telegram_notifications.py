from __future__ import annotations

import json
import uuid

import httpx
import pytest

from alliancesim.adapters.outbound.notifications.telegram import TelegramNotificationSender
from alliancesim.application.models import PendingNotification
from alliancesim.application.notifications import NotificationDeliveryError
from alliancesim.domain.identity import Platform


async def test_telegram_notification_sends_bot_message() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 1}})

    sender = TelegramNotificationSender("secret", transport=httpx.MockTransport(handler))
    await sender.send(
        PendingNotification(
            outbox_id=uuid.UUID(int=1),
            platform=Platform.TELEGRAM,
            platform_user_id="42",
            event_type="mining_completed",
            payload={"material_id": "raw-ore", "quantity": 100},
        )
    )
    assert requests[0].url.path == "/botsecret/sendMessage"
    payload = json.loads(requests[0].content)
    assert payload["chat_id"] == "42"
    assert payload["text"].endswith("100 raw-ore。")


async def test_telegram_notification_failure_does_not_expose_token() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"ok": False})

    sender = TelegramNotificationSender(
        "super-secret-token", transport=httpx.MockTransport(handler)
    )
    notification = PendingNotification(
        outbox_id=uuid.UUID(int=1),
        platform=Platform.TELEGRAM,
        platform_user_id="42",
        event_type="mining_completed",
        payload={"material_id": "raw-ore", "quantity": 100},
    )
    with pytest.raises(NotificationDeliveryError, match="HTTP 401") as caught:
        await sender.send(notification)
    assert "super-secret-token" not in str(caught.value)
