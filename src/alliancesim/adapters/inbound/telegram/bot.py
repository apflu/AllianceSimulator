from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.views import MessageView


def telegram_text(view: MessageView) -> str:
    sections = [view.title, view.body]
    sections.extend(f"{field.name}\n{field.value}" for field in view.fields)
    return "\n\n".join(section for section in sections if section)


def telegram_markup(view: MessageView) -> InlineKeyboardMarkup | None:
    if not view.actions:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=action.label, callback_data=action.action_id)]
            for action in view.actions
        ]
    )


class AllianceTelegramRouter:
    def __init__(self, commands: ChatCommandAdapter) -> None:
        self._commands = commands
        self.router = Router(name="alliance-simulator")
        self.router.message.register(self.start_command, Command("start"))
        self.router.message.register(self.status_command, Command("status"))
        self.router.message.register(self.mine_command, Command("mine"))
        self.router.message.register(self.train_command, Command("train"))
        self.router.message.register(self.events_command, Command("events"))
        self.router.callback_query.register(self.action_callback, F.data.startswith("event:"))

    @staticmethod
    def _user_id(message: Message) -> str:
        return str(message.from_user.id if message.from_user is not None else message.chat.id)

    @staticmethod
    def _interaction_id(message: Message) -> str:
        return f"{message.chat.id}:{message.message_id}"

    async def start_command(self, message: Message, command: CommandObject) -> None:
        name = (command.args or "").strip()
        if not name:
            await message.answer("请使用 /start <联盟名称> 创建联盟。")
            return
        view = await self._commands.start(
            self._user_id(message), name, self._interaction_id(message)
        )
        await message.answer(telegram_text(view))

    async def status_command(self, message: Message) -> None:
        view = await self._commands.status(self._user_id(message))
        await message.answer(telegram_text(view))

    async def mine_command(self, message: Message) -> None:
        view = await self._commands.mine(self._user_id(message), self._interaction_id(message))
        await message.answer(telegram_text(view))

    async def train_command(self, message: Message) -> None:
        view = await self._commands.train(self._user_id(message), self._interaction_id(message))
        await message.answer(telegram_text(view))

    async def events_command(self, message: Message) -> None:
        view = await self._commands.events(self._user_id(message))
        await message.answer(telegram_text(view), reply_markup=telegram_markup(view))

    async def action_callback(self, callback: CallbackQuery) -> None:
        if callback.data is None:
            await callback.answer("无效操作。", show_alert=True)
            return
        await callback.answer()
        view = await self._commands.resolve_action(str(callback.from_user.id), callback.data)
        if callback.bot is None:
            raise RuntimeError("Telegram callback has no Bot context")
        await callback.bot.send_message(
            callback.from_user.id,
            telegram_text(view),
            reply_markup=telegram_markup(view),
        )
