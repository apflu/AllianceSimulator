from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from alliancesim import __version__
from alliancesim.application.ports import DatabaseProbe


class HealthResponse(BaseModel):
    status: str
    version: str


def create_app(database: DatabaseProbe) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        yield
        close = getattr(database, "close", None)
        if close is not None:
            await close()

    app = FastAPI(title="Alliance Simulator", version=__version__, lifespan=lifespan)

    async def live() -> HealthResponse:
        return HealthResponse(status="ok", version=__version__)

    async def ready(response: Response) -> HealthResponse:
        if not await database.probe():
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return HealthResponse(status="not_ready", version=__version__)
        return HealthResponse(status="ok", version=__version__)

    app.add_api_route("/health/live", live, methods=["GET"], response_model=HealthResponse)
    app.add_api_route("/health/ready", ready, methods=["GET"], response_model=HealthResponse)

    return app
