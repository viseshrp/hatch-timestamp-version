import datetime as real_datetime
from pathlib import Path
import re
import shutil
import subprocess
import textwrap
from typing import Any

from hatch_vcs.version_source import VCSVersionSource
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManager
import pytest

from hatch_timestamp_version import hooks, ts_scheme
from hatch_timestamp_version.hooks import TSVersionSource
from hatch_timestamp_version.ts_scheme import TimestampDevVersionScheme


def test_hook() -> None:
    plugin = hooks.hatch_register_version_source()
    assert issubclass(plugin, VCSVersionSource)


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

    scheme = ts_scheme.TimestampDevVersionScheme(
        root=".", config={"validate-bump": True}, timestamp_fmt="short"
    )

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


@pytest.mark.parametrize(
    "timestamp_format, expected_pattern",
    [
        ("short", r"0\.1\.dev\d{8}"),  # YYYYMMDD
        ("long", r"0\.1\.dev\d{14}"),  # YYYYMMDDHHMMSS
        ("%Y%m%d%H%M", r"0\.1\.dev\d{12}"),  # Custom
    ],
)
def test_hatch_version_timestamp_formats(
    tmp_path: Path, timestamp_format: str, expected_pattern: str
) -> None:
    # Setup temp package dir
    project_dir = tmp_path / "project"
    pkg_dir = project_dir / "my_pkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").touch()

    # Write pyproject.toml
    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text(
        textwrap.dedent(
            f"""\
        [project]
        name = "demo"
        dynamic = ["version"]
        description = "Dummy project for plugin testing"
        dependencies = []
        [build-system]
        requires = ["hatchling", "hatch-timestamp-version @ file:../../"]
        build-backend = "hatchling.build"
        [tool.hatch.version]
        source = "vcs-dev-timestamp"
        validate-bump = true
        [tool.hatch.version.raw-options]
        local_scheme = "no-local-version"
        timestamp_format = "{timestamp_format}"
    """
        )
    )
    # Git init and commit
    subprocess.run(["git", "init", "-b", "main"], cwd=project_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=project_dir, check=True)
    subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=project_dir, check=True)

    # Load project metadata (this uses the plugin under the hood)
    metadata = ProjectMetadata(str(project_dir), PluginManager())
    version = metadata.version

    assert version.startswith("0.1.dev")
    assert re.fullmatch(expected_pattern, version)

    # Optional cleanup
    for path in [".git", ".hatch", "__pycache__"]:
        dir_to_remove = project_dir / path
        if dir_to_remove.exists():
            shutil.rmtree(dir_to_remove, ignore_errors=True)
