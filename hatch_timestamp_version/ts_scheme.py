from datetime import datetime, timezone

from hatchling.version.scheme.plugin.interface import VersionSchemeInterface
from packaging.version import parse as parse_version


class TimestampDevVersionScheme(VersionSchemeInterface):
    PLUGIN_NAME: str = "timestamp-dev"

    def update(
        self,
        desired_version: str,
        original_version: str,
        _version_data: dict[str, str],
    ) -> str:
        """
        Replace `.devN` with `.devYYYYMMDDHHMMSS` using current UTC time.
        """
        if not desired_version or ".dev" not in desired_version:
            return desired_version or original_version

        base_version, _, _ = desired_version.rpartition(".dev")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        new_version = f"{base_version}.dev{timestamp}"

        if self.validate_bump and parse_version(new_version) <= parse_version(original_version):
            raise ValueError

        return new_version
