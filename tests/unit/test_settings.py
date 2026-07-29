from pytest import MonkeyPatch

from alliancesim.bootstrap.settings import Settings


def test_settings_read_prefixed_environment(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ASIM_PORT", "9001")
    monkeypatch.setenv("ASIM_ENVIRONMENT", "test")
    settings = Settings()
    assert settings.port == 9001
    assert settings.environment == "test"
