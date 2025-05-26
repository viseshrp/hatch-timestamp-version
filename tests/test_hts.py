import datetime as real_datetime
import re

from hatch_vcs.version_source import VCSVersionSource
import pytest

from hatch_timestamp_version import hooks, ts_scheme
from hatch_timestamp_version.hooks import TSVersionSource
from hatch_timestamp_version.ts_scheme import TimestampDevVersionScheme


def test_hook() -> None:
    assert hooks.hatch_register_version_source()


def test_short_timestamp_format():
    scheme = TimestampDevVersionScheme(root=".", config={}, timestamp_fmt="short")
    version = scheme.update("1.0.0.dev0", "1.0.0.dev0", {})
    assert version.startswith("1.0.0.dev")
    timestamp = version.removeprefix("1.0.0.dev")
    assert re.fullmatch(r"\d{8}", timestamp)  # YYYYMMDD


def test_long_timestamp_format():
    scheme = TimestampDevVersionScheme(root=".", config={}, timestamp_fmt="long")
    version = scheme.update("1.0.0.dev0", "1.0.0.dev0", {})
    assert version.startswith("1.0.0.dev")
    timestamp = version.removeprefix("1.0.0.dev")
    assert re.fullmatch(r"\d{14}", timestamp)  # YYYYMMDDHHMMSS


def test_custom_strftime_format():
    fmt = "%Y%m%d%H%M"
    scheme = TimestampDevVersionScheme(root=".", config={}, timestamp_fmt=fmt)
    version = scheme.update("1.0.0.dev0", "1.0.0.dev0", {})
    timestamp = version.removeprefix("1.0.0.dev")
    assert re.fullmatch(r"\d{12}", timestamp)


def test_invalid_format_raises():
    scheme = TimestampDevVersionScheme(root=".", config={}, timestamp_fmt="%Q %Z %INVALID")
    with pytest.raises(ValueError, match=r"Invalid timestamp format '.*'"):
        scheme.update("1.0.0.dev0", "1.0.0.dev0", {})


def test_non_dev_version_passes_through():
    scheme = TimestampDevVersionScheme(root=".", config={}, timestamp_fmt="short")
    version = scheme.update("1.0.0", "1.0.0", {})
    assert version == "1.0.0"


class FrozenDatetime(real_datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return real_datetime.datetime(2025, 5, 26, 15, 0, 0, tzinfo=tz)


def test_validate_bump_triggers_error(monkeypatch):
    monkeypatch.setattr(ts_scheme, "datetime", FrozenDatetime)

    scheme = ts_scheme.TimestampDevVersionScheme(root=".", config={}, timestamp_fmt="short")
    scheme.validate_bump = True

    v1 = scheme.update("1.0.0.dev0", "1.0.0.dev0", {})
    with pytest.raises(ValueError, match="not greater than original"):
        scheme.update("1.0.0.dev0", v1, {})


class DummyVCSVersionSource(VCSVersionSource):
    def __init__(self, version: str):
        super().__init__(root=".", config={})
        self._mock_version = version
        self._config_raw_options = {"timestamp_format": "short"}

    def get_version_data(self) -> dict:
        return {"version": self._mock_version}

    @property
    def config_raw_options(self):
        return self._config_raw_options

    def construct_setuptools_scm_config(self) -> dict:
        return {
            "version_scheme": "guess-next-dev",
            "local_scheme": "no-local-version",
            "timestamp_format": "short",  # to be removed
        }


def test_construct_setuptools_scm_config_removes_timestamp_format():
    class Patched(TSVersionSource, DummyVCSVersionSource):
        def __init__(self):
            DummyVCSVersionSource.__init__(self, "0.1.0.dev0")

    source = Patched()
    config = source.construct_setuptools_scm_config()
    assert "timestamp_format" not in config


def test_get_version_data_with_dev(monkeypatch):
    class Patched(TSVersionSource, DummyVCSVersionSource):
        def __init__(self):
            DummyVCSVersionSource.__init__(self, "0.2.0.dev0")

    source = Patched()
    version_data = source.get_version_data()
    version = version_data["version"]

    assert version.startswith("0.2.0.dev")
    suffix = version.removeprefix("0.2.0.dev")
    assert re.fullmatch(r"\d{8}", suffix)  # matches short format (YYYYMMDD)


def test_get_version_data_with_non_dev(monkeypatch):
    class Patched(TSVersionSource, DummyVCSVersionSource):
        def __init__(self):
            DummyVCSVersionSource.__init__(self, "0.2.0")

    source = Patched()
    version_data = source.get_version_data()
    assert version_data["version"] == "0.2.0"
