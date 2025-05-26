from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.plugin import hookimpl
from hatchling.version.scheme.plugin.interface import VersionSchemeInterface
from hatchling.version.source.plugin.interface import VersionSourceInterface

from hatch_vcs.build_hook import VCSBuildHook
from hatch_vcs.metadata_hook import VCSMetadataHook
from hatch_vcs.version_source import VCSVersionSource
from .ts_scheme import TimestampDevVersionScheme


@hookimpl
def hatch_register_version_source() -> type[VersionSourceInterface]:
    return VCSVersionSource


@hookimpl
def hatch_register_build_hook() -> type[BuildHookInterface]:
    return VCSBuildHook


@hookimpl
def hatch_register_metadata_hook() -> type[MetadataHookInterface]:
    return VCSMetadataHook


@hookimpl
def hatch_register_version_scheme() -> type[VersionSchemeInterface]:
    return TimestampDevVersionScheme
