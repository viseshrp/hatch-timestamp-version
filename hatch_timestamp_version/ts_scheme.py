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
        Replace `.devN` with `.dev<timestamp>` using UTC time.
        Format is controlled by [tool.hatch.version.raw-options.timestamp_format].
        Allowed values:
          - "short" → YYYYMMDD
          - "long"  → YYYYMMDDHHMMSS
          - any strftime string like "%Y%m%d%H%M"
        """
        if not desired_version or ".dev" not in desired_version:
            return desired_version or original_version

        # Get format string from user config
        fmt_option = self.config.get("timestamp_format", "long")
        if fmt_option == "short":
            fmt = "%Y%m%d"
        elif fmt_option == "long" or fmt_option == "default":
            fmt = "%Y%m%d%H%M%S"
        else:
            # Validate custom strftime format
            try:
                datetime.now(timezone.utc).strftime(fmt_option)
                fmt = fmt_option
            except Exception as e:
                msg = (
                    f"Invalid timestamp format '{fmt_option}'. "
                    "Use 'short', 'long', or a valid strftime pattern like '%Y%m%d%H%M'."
                )
                raise ValueError(msg) from e

        timestamp = datetime.now(timezone.utc).strftime(fmt)
        base_version, _, _ = desired_version.rpartition(".dev")
        new_version = f"{base_version}.dev{timestamp}"

        if self.validate_bump and parse_version(new_version) <= parse_version(original_version):
            msg = (
                f"Timestamp-based version '{new_version}' is not greater than "
                f"original '{original_version}'. "
                "This may happen if builds occur within the same second/minute/hour/day "
                "based on the chosen format. "
            )
            raise ValueError(msg)

        return new_version
