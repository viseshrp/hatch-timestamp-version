from typing import Any

from hatch_vcs.build_hook import VCSBuildHook
from hatch_vcs.metadata_hook import VCSMetadataHook
from hatch_vcs.version_source import VCSVersionSource
from hatchling.plugin import hookimpl
from hatchling.version.scheme.plugin.interface import VersionSchemeInterface

from .ts_scheme import TimestampDevVersionScheme


class TSVersionSource(VCSVersionSource):
    PLUGIN_NAME: str = "timestamp-dev"

    def is_dev_version(self, version: str) -> bool:
        return ".dev" in version and version.split(".dev")[-1].isdigit()

    def get_version_data(self) -> Any:
        version_data = super().get_version_data()
        version = version_data.get("version", "")
        if self.is_dev_version(version):
            scheme = TimestampDevVersionScheme(self.root, self.config)
            version_data["version"] = scheme.update(version, version, version_data)
        return version_data


class TSBuildHook(VCSBuildHook):
    PLUGIN_NAME: str = "timestamp-dev"


class TSMetadataHook(VCSMetadataHook):
    PLUGIN_NAME: str = "timestamp-dev"


@hookimpl
def hatch_register_version_source() -> Any:
    return TSVersionSource


@hookimpl
def hatch_register_build_hook() -> Any:
    return TSBuildHook


@hookimpl
def hatch_register_metadata_hook() -> Any:
    return TSMetadataHook


@hookimpl
def hatch_register_version_scheme() -> type[VersionSchemeInterface]:
    return TimestampDevVersionScheme
