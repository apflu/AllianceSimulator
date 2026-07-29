from pytest import MonkeyPatch

from alliancesim.bootstrap.settings import Settings


def test_settings_read_prefixed_environment(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ASIM_PORT", "9001")
    monkeypatch.setenv("ASIM_ENVIRONMENT", "test")
    settings = Settings()
    assert settings.port == 9001
    assert settings.environment == "test"


def test_blank_optional_tokens_are_ignored(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ASIM_DISCORD_TOKEN", "")
    monkeypatch.setenv("ASIM_TELEGRAM_TOKEN", "")
    settings = Settings()
    assert settings.discord_token is None
    assert settings.telegram_token is None
