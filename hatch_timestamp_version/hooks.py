from hatchling.plugin import hookimpl
from hatchling.version.scheme.plugin.interface import VersionSchemeInterface

from ._vendor.hatch_vcs.build_hook import VCSBuildHook
from ._vendor.hatch_vcs.metadata_hook import VCSMetadataHook
from ._vendor.hatch_vcs.version_source import VCSVersionSource
from .ts_scheme import TimestampDevVersionScheme


@hookimpl
def hatch_register_version_source():
    return VCSVersionSource


@hookimpl
def hatch_register_build_hook():
    return VCSBuildHook


@hookimpl
def hatch_register_metadata_hook():
    return VCSMetadataHook

@hookimpl
def hatch_register_version_scheme() -> type[VersionSchemeInterface]:
    return TimestampDevVersionScheme
