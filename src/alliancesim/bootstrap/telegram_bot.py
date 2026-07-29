from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher

from alliancesim.adapters.inbound.telegram.bot import AllianceTelegramRouter
from alliancesim.adapters.outbound.persistence.database import Database
from alliancesim.adapters.outbound.persistence.game_store import SqlAlchemyGameStore
from alliancesim.application.chat_commands import ChatCommandAdapter
from alliancesim.application.game_service import GameService
from alliancesim.bootstrap.logging import configure_logging
from alliancesim.bootstrap.settings import get_settings
from alliancesim.domain.identity import Platform


async def run_bot() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    if settings.telegram_token is None:
        raise RuntimeError("ASIM_TELEGRAM_TOKEN is required")
    database = Database(settings.database_url)
    store = SqlAlchemyGameStore(database.sessions)
    commands = ChatCommandAdapter(GameService(store), Platform.TELEGRAM)
    adapter = AllianceTelegramRouter(commands)
    bot = Bot(settings.telegram_token.get_secret_value())
    dispatcher = Dispatcher()
    dispatcher.include_router(adapter.router)
    try:
        await dispatcher.start_polling(bot)  # pyright: ignore[reportUnknownMemberType]
    finally:
        await bot.session.close()
        await database.close()


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
