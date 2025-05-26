from typing import Any

from hatch_vcs.build_hook import VCSBuildHook
from hatch_vcs.metadata_hook import VCSMetadataHook
from hatch_vcs.version_source import VCSVersionSource
from hatchling.plugin import hookimpl
from hatchling.version.scheme.plugin.interface import VersionSchemeInterface

from .ts_scheme import TimestampDevVersionScheme


@hookimpl
def hatch_register_version_source() -> Any:
    return VCSVersionSource


@hookimpl
def hatch_register_build_hook() -> Any:
    return VCSBuildHook


@hookimpl
def hatch_register_metadata_hook() -> Any:
    return VCSMetadataHook


@hookimpl
def hatch_register_version_scheme() -> type[VersionSchemeInterface]:
    return TimestampDevVersionScheme
