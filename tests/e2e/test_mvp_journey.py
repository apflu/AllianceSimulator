from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from alliancesim.adapters.outbound.persistence.database import Database
from alliancesim.adapters.outbound.persistence.game_store import SqlAlchemyGameStore
from alliancesim.adapters.outbound.persistence.models import Base
from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.game_service import GameService
from alliancesim.application.models import PendingNotification
from alliancesim.application.notifications import ActionWorkerPoller
from alliancesim.domain.identity import Platform


class CapturingSender:
    def __init__(self) -> None:
        self.notifications: list[PendingNotification] = []

    async def send(self, notification: PendingNotification) -> None:
        self.notifications.append(notification)


async def test_player_completes_mvp_journey_without_database_edits(tmp_path: Path) -> None:
    database = Database(f"sqlite+aiosqlite:///{(tmp_path / 'journey.sqlite3').as_posix()}")
    async with database.engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    now = [datetime(2026, 7, 30, 12, 0, tzinfo=UTC)]
    store = SqlAlchemyGameStore(database.sessions)
    service = GameService(store, clock=lambda: now[0])
    commands = ChatCommandAdapter(service, Platform.DISCORD)
    sender = CapturingSender()
    worker = ActionWorkerPoller(store, sender, clock=lambda: now[0])
    try:
        created = await commands.start("mvp-player", "MVP Union", "start-1")
        assert created.title == "联盟已建立"

        initial_status = await commands.status("mvp-player")
        assert any(
            field.name == "库存" and field.value == "暂无资源" for field in initial_status.fields
        )

        mining = await commands.mine("mvp-player", "mine-1")
        assert mining.title == "采矿行动已开始"
        assert any(field.name == "预计产量" and field.value == "100" for field in mining.fields)

        now[0] += timedelta(minutes=1)
        assert await worker.poll_once() == 2
        assert sender.notifications[-1].event_type == "mining_completed"

        mined_status = await commands.status("mvp-player")
        assert any(
            field.name == "库存" and "raw-ore: 100" in field.value for field in mined_status.fields
        )

        event = await commands.events("mvp-player")
        assert event.title == "异常矿石样本"
        analyze = next(action for action in event.actions if action.action_id.endswith(":analyze"))
        resolved = await commands.resolve_action("mvp-player", analyze.action_id)
        assert resolved.title == "事件已处理"
        assert "research-data" in resolved.body

        training = await commands.train("mvp-player", "train-1")
        assert training.title == "技能训练已开始"
        now[0] += timedelta(minutes=2)
        assert await worker.poll_once() == 2
        assert sender.notifications[-1].event_type == "skill_training_completed"

        improved_mining = await commands.mine("mvp-player", "mine-2")
        assert any(
            field.name == "预计产量" and field.value == "110" for field in improved_mining.fields
        )
        now[0] += timedelta(minutes=1)
        assert await worker.poll_once() == 2

        final_status = await commands.status("mvp-player")
        assert any(
            field.name == "库存" and "raw-ore: 210" in field.value for field in final_status.fields
        )
        assert any(
            field.name == "技能" and "mining-operations: 1" in field.value
            for field in final_status.fields
        )
    finally:
        await database.close()
