from __future__ import annotations

import json
import uuid

import httpx

from alliancesim.adapters.outbound.notifications.discord import DiscordNotificationSender
from alliancesim.application.models import PendingNotification
from alliancesim.domain.identity import Platform


async def test_discord_notification_creates_dm_and_sends_message() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/users/@me/channels"):
            return httpx.Response(200, json={"id": "channel-7"})
        return httpx.Response(200, json={"id": "message-8"})

    sender = DiscordNotificationSender("secret", transport=httpx.MockTransport(handler))
    await sender.send(
        PendingNotification(
            outbox_id=uuid.UUID(int=1),
            platform=Platform.DISCORD,
            platform_user_id="42",
            event_type="mining_completed",
            payload={"material_id": "raw-ore", "quantity": 100},
        )
    )
    assert [request.url.path for request in requests] == [
        "/api/v10/users/@me/channels",
        "/api/v10/channels/channel-7/messages",
    ]
    assert requests[0].headers["authorization"] == "Bot secret"
    assert json.loads(requests[1].content)["content"].endswith("100 raw-ore。")
