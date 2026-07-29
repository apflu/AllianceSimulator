from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from alliancesim.adapters.inbound.http.app import create_app
from alliancesim.adapters.outbound.persistence.database import Database
from alliancesim.bootstrap.logging import configure_logging
from alliancesim.bootstrap.settings import get_settings


def build_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    return create_app(Database(settings.database_url))


def main() -> None:
    settings = get_settings()
    uvicorn.run(build_app(), host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
