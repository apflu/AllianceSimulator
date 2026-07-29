from httpx import ASGITransport, AsyncClient

from alliancesim.adapters.inbound.http.app import create_app


class FakeDatabase:
    def __init__(self, ready: bool) -> None:
        self.ready = ready
        self.closed = False

    async def probe(self) -> bool:
        return self.ready

    async def close(self) -> None:
        self.closed = True


async def test_liveness_does_not_depend_on_database() -> None:
    app = create_app(FakeDatabase(ready=False))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_readiness_reports_database_failure() -> None:
    app = create_app(FakeDatabase(ready=False))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"


async def test_readiness_reports_success() -> None:
    app = create_app(FakeDatabase(ready=True))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
