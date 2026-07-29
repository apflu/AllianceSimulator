from pathlib import Path

from pytest import MonkeyPatch

from alliancesim.bootstrap.settings import Settings


def test_settings_read_prefixed_environment(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ASIM_PORT", "9001")
    monkeypatch.setenv("ASIM_ENVIRONMENT", "test")
    monkeypatch.setenv("ASIM_TELEGRAM_PROXY_URL", "http://127.0.0.1:7897")
    settings = Settings()
    assert settings.port == 9001
    assert settings.environment == "test"
    assert settings.telegram_proxy_url is not None
    assert settings.telegram_proxy_url.get_secret_value() == "http://127.0.0.1:7897"


def test_blank_optional_tokens_are_ignored(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ASIM_DISCORD_TOKEN", "")
    monkeypatch.setenv("ASIM_TELEGRAM_TOKEN", "")
    monkeypatch.setenv("ASIM_TELEGRAM_PROXY_URL", "")
    settings = Settings()
    assert settings.discord_token is None
    assert settings.telegram_token is None
    assert settings.telegram_proxy_url is None
