import datetime as real_datetime
import re
from typing import Any

from hatch_vcs.version_source import VCSVersionSource
import pytest

from hatch_timestamp_version import hooks, ts_scheme
from hatch_timestamp_version.hooks import TSVersionSource
from hatch_timestamp_version.ts_scheme import TimestampDevVersionScheme


def test_hook() -> None:
    assert hooks.hatch_register_version_source()


def test_short_timestamp_format() -> None:
    scheme = TimestampDevVersionScheme(root=".", config={}, timestamp_fmt="short")
    version: str = scheme.update("1.0.0.dev0", "1.0.0.dev0", {})
    assert version.startswith("1.0.0.dev")
    timestamp = version.removeprefix("1.0.0.dev")
    assert re.fullmatch(r"\d{8}", timestamp)


def test_long_timestamp_format() -> None:
    scheme = TimestampDevVersionScheme(root=".", config={}, timestamp_fmt="long")
    version: str = scheme.update("1.0.0.dev0", "1.0.0.dev0", {})
    assert version.startswith("1.0.0.dev")
    timestamp = version.removeprefix("1.0.0.dev")
    assert re.fullmatch(r"\d{14}", timestamp)


def test_custom_strftime_format() -> None:
    fmt: str = "%Y%m%d%H%M"
    scheme = TimestampDevVersionScheme(root=".", config={}, timestamp_fmt=fmt)
    version: str = scheme.update("1.0.0.dev0", "1.0.0.dev0", {})
    timestamp: str = version.removeprefix("1.0.0.dev")
    assert re.fullmatch(r"\d{12}", timestamp)


def test_invalid_format_raises() -> None:
    scheme = TimestampDevVersionScheme(root=".", config={}, timestamp_fmt="%Q %Z %INVALID")
    with pytest.raises(ValueError, match=r"Invalid timestamp format '.*'"):
        scheme.update("1.0.0.dev0", "1.0.0.dev0", {})


def test_non_dev_version_passes_through() -> None:
    scheme = TimestampDevVersionScheme(root=".", config={}, timestamp_fmt="short")
    version: str = scheme.update("1.0.0", "1.0.0", {})
    assert version == "1.0.0"


class FrozenDatetime(real_datetime.datetime):
    @classmethod
    def now(cls, tz: Any = None) -> "FrozenDatetime":
        return cls(2025, 5, 26, 15, 0, 0, tzinfo=tz)


def test_validate_bump_triggers_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ts_scheme, "datetime", FrozenDatetime)

    scheme = ts_scheme.TimestampDevVersionScheme(root=".", config={}, timestamp_fmt="short")
    scheme.validate_bump = True

    v1: str = scheme.update("1.0.0.dev0", "1.0.0.dev0", {})
    with pytest.raises(ValueError, match="not greater than original"):
        scheme.update("1.0.0.dev0", v1, {})


class DummyVCSVersionSource(VCSVersionSource):
    def __init__(self, version: str) -> None:
        super().__init__(root=".", config={})
        self._mock_version = version
        self._config_raw_options = {"timestamp_format": "short"}

    def get_version_data(self) -> dict[str, str]:
        return {"version": self._mock_version}

    @property
    def config_raw_options(self) -> dict[str, str]:
        return self._config_raw_options

    def construct_setuptools_scm_config(self) -> dict[str, str]:
        return {
            "version_scheme": "guess-next-dev",
            "local_scheme": "no-local-version",
            "timestamp_format": "short",
        }


def test_construct_setuptools_scm_config_removes_timestamp_format() -> None:
    class Patched(TSVersionSource, DummyVCSVersionSource):
        def __init__(self) -> None:
            DummyVCSVersionSource.__init__(self, "0.1.0.dev0")

    source = Patched()
    config: dict[str, str] = source.construct_setuptools_scm_config()
    assert "timestamp_format" not in config


def test_get_version_data_with_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    class Patched(TSVersionSource, DummyVCSVersionSource):
        def __init__(self) -> None:
            DummyVCSVersionSource.__init__(self, "0.2.0.dev0")

    source = Patched()
    version_data: dict[str, str] = source.get_version_data()
    version: str = version_data["version"]

    assert version.startswith("0.2.0.dev")
    suffix: str = version.removeprefix("0.2.0.dev")
    assert re.fullmatch(r"\d{8}", suffix)


def test_get_version_data_with_non_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    class Patched(TSVersionSource, DummyVCSVersionSource):
        def __init__(self) -> None:
            DummyVCSVersionSource.__init__(self, "0.2.0")

    source = Patched()
    version_data: dict[str, str] = source.get_version_data()
    assert version_data["version"] == "0.2.0"
