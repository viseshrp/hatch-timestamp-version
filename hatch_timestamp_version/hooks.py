from typing import Any

from hatch_vcs.build_hook import VCSBuildHook
from hatch_vcs.metadata_hook import VCSMetadataHook
from hatch_vcs.version_source import VCSVersionSource
from hatchling.plugin import hookimpl

from .ts_scheme import TimestampDevVersionScheme


class TSVersionSource(VCSVersionSource):
    PLUGIN_NAME: str = "timestamp-dev"

    def construct_setuptools_scm_config(self) -> Any:
        # Inherit base config
        config = super().construct_setuptools_scm_config()
        # Remove custom keys not recognized by setuptools_scm
        config.pop("timestamp_format", None)
        return config

    def get_version_data(self) -> Any:
        timestamp_fmt = self.config_raw_options.get("timestamp_format", "long")
        # Get version data from hatch-vcs
        version_data = super().get_version_data()
        version = version_data.get("version", "")
        if ".dev" in version and version.split(".dev")[-1].isdigit():
            scheme = TimestampDevVersionScheme(self.root, self.config, timestamp_fmt)
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
