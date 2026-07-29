from __future__ import annotations

from alliancesim.application.errors import ApplicationError
from alliancesim.application.game_service import GameService
from alliancesim.application.views import MessageView, ViewField
from alliancesim.domain.identity import Platform


class ChatCommandAdapter:
    def __init__(self, service: GameService, platform: Platform) -> None:
        self._service = service
        self._platform = platform

    async def start(self, user_id: str, alliance_name: str, interaction_id: str) -> MessageView:
        try:
            result = await self._service.create_alliance(
                self._platform, user_id, alliance_name, interaction_id
            )
        except (ApplicationError, ValueError) as error:
            return MessageView("无法创建联盟", str(error), is_error=True)
        if result.created:
            return MessageView(
                "联盟已建立",
                f"{result.name} 已获得一名初始成员和一艘 Pioneer。",
                (ViewField("下一步", "使用 /mine 开始第一次采矿。"),),
            )
        return MessageView("联盟已经存在", f"继续指挥 {result.name}。")

    async def status(self, user_id: str) -> MessageView:
        try:
            result = await self._service.get_status(self._platform, user_id)
        except ApplicationError as error:
            return MessageView("无法读取联盟", str(error), is_error=True)
        inventory = (
            "\n".join(f"{item.material_id}: {item.quantity}" for item in result.inventory)
            or "暂无资源"
        )
        skills = (
            "\n".join(f"{skill.skill_id}: {skill.level}" for skill in result.skills) or "尚未训练"
        )
        action = (
            f"{result.active_action.action_type}，完成于 "
            f"{result.active_action.finishes_at.isoformat()}"
            if result.active_action is not None
            else "空闲"
        )
        return MessageView(
            result.name,
            "联盟运行正常。",
            (
                ViewField("成员", result.character_name, inline=True),
                ViewField("舰船", result.ship_name, inline=True),
                ViewField("库存", inventory),
                ViewField("技能", skills),
                ViewField("当前行动", action),
            ),
        )

    async def mine(self, user_id: str, interaction_id: str) -> MessageView:
        try:
            result = await self._service.start_mining(self._platform, user_id, interaction_id)
        except ApplicationError as error:
            return MessageView("无法开始采矿", str(error), is_error=True)
        prefix = "采矿行动已开始" if result.created else "采矿行动已经登记"
        return MessageView(
            prefix,
            "Pioneer 正在 calm-asteroid-belt 开采 raw-ore。",
            (
                ViewField("预计完成", result.finishes_at.isoformat()),
                ViewField("预计产量", str(result.yield_quantity), inline=True),
            ),
        )

    async def train(self, user_id: str, interaction_id: str) -> MessageView:
        try:
            result = await self._service.start_training(self._platform, user_id, interaction_id)
        except (ApplicationError, ValueError) as error:
            return MessageView("无法开始训练", str(error), is_error=True)
        prefix = "技能训练已开始" if result.created else "技能训练已经登记"
        return MessageView(
            prefix,
            f"正在训练 {result.skill_id} 到 {result.target_level} 级。",
            (ViewField("预计完成", result.finishes_at.isoformat()),),
        )
