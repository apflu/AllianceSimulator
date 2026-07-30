from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from alliancesim.adapters.outbound.notifications.discord import DiscordNotificationSender
from alliancesim.application.models import PendingNotification
from alliancesim.application.notifications import NotificationDeliveryError
from alliancesim.domain.identity import Platform


def notification() -> PendingNotification:
    return PendingNotification(
        outbox_id=uuid.UUID(int=1),
        platform=Platform.DISCORD,
        platform_user_id="42",
        event_type="mining_completed",
        payload={"material_id": "raw-ore", "quantity": 100},
    )


async def test_discord_notification_creates_dm_and_sends_message() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/users/@me/channels"):
            return httpx.Response(200, json={"id": "channel-7"})
        return httpx.Response(200, json={"id": "message-8"})

    sender = DiscordNotificationSender("secret", transport=httpx.MockTransport(handler))
    await sender.send(notification())
    assert [request.url.path for request in requests] == [
        "/api/v10/users/@me/channels",
        "/api/v10/channels/channel-7/messages",
    ]
    assert requests[0].headers["authorization"] == "Bot secret"
    assert json.loads(requests[1].content)["content"].endswith("100 raw-ore。")


async def test_discord_notification_uses_configured_proxy() -> None:
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.post.side_effect = [
        httpx.Response(
            200,
            json={"id": "channel-7"},
            request=httpx.Request("POST", "https://discord.com/api/v10/users/@me/channels"),
        ),
        httpx.Response(
            200,
            json={"id": "message-8"},
            request=httpx.Request(
                "POST", "https://discord.com/api/v10/channels/channel-7/messages"
            ),
        ),
    ]
    with patch(
        "alliancesim.adapters.outbound.notifications.discord.httpx.AsyncClient",
        return_value=client,
    ) as async_client:
        await DiscordNotificationSender(
            "secret", proxy_url="http://host.docker.internal:7897"
        ).send(notification())

    assert async_client.call_args.kwargs["proxy"] == "http://host.docker.internal:7897"


@pytest.mark.parametrize(
    ("failed_path", "expected_operation"),
    [
        ("/api/v10/users/@me/channels", "create DM"),
        ("/api/v10/channels/channel-7/messages", "send DM"),
    ],
)
async def test_discord_notification_reports_safe_api_error_code(
    failed_path: str, expected_operation: str
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == failed_path:
            return httpx.Response(
                403,
                json={"code": 50007, "message": "sensitive upstream detail"},
            )
        return httpx.Response(200, json={"id": "channel-7"})

    sender = DiscordNotificationSender("secret", transport=httpx.MockTransport(handler))

    with pytest.raises(NotificationDeliveryError) as captured:
        await sender.send(notification())

    assert str(captured.value) == (
        f"Discord API {expected_operation} returned HTTP 403 (code 50007)"
    )
    assert "sensitive upstream detail" not in str(captured.value)
