from typing import Any

from hatch_vcs.build_hook import VCSBuildHook
from hatch_vcs.metadata_hook import VCSMetadataHook
from hatch_vcs.version_source import VCSVersionSource
from hatchling.plugin import hookimpl
from hatchling.version.scheme.plugin.interface import VersionSchemeInterface

from .ts_scheme import TimestampDevVersionScheme


class TSVersionSource(VCSVersionSource):
    PLUGIN_NAME: str = "timestamp-dev"


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
