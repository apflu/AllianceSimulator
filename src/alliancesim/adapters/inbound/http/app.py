from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog.contextvars
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from alliancesim import __version__
from alliancesim.application.ports import DatabaseProbe


class HealthResponse(BaseModel):
    status: str
    version: str


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> StarletteResponse:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.clear_contextvars()
        response.headers["x-request-id"] = request_id
        return response


def create_app(database: DatabaseProbe) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        yield
        close = getattr(database, "close", None)
        if close is not None:
            await close()

    app = FastAPI(title="Alliance Simulator", version=__version__, lifespan=lifespan)
    app.add_middleware(RequestContextMiddleware)

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
