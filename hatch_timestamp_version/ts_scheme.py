from datetime import datetime, timezone
from functools import cached_property
from typing import Any

from hatchling.version.scheme.plugin.interface import VersionSchemeInterface
from packaging.version import parse as parse_version


class TimestampDevVersionScheme(VersionSchemeInterface):
    PLUGIN_NAME: str = "vcs-dev-timestamp"

    def __init__(self, root: str, config: dict[str, Any], timestamp_fmt: str) -> None:
        super().__init__(root, config)
        self._timestamp_fmt: str = timestamp_fmt

    @cached_property
    def timestamp_fmt(self) -> str:
        """
        This is the value of the `timestamp_format` option.


        ```toml config-example
        [tool.hatch.version.raw-options]
        local_scheme = "no-local-version"
        timestamp_format = "short"
        ```
        """
        timestamp_fmt = self._timestamp_fmt
        if not isinstance(timestamp_fmt, str):
            msg = "option `timestamp_format` must be a string"
            raise TypeError(msg)

        if timestamp_fmt == "short":
            return "%Y%m%d"
        elif timestamp_fmt in {"long", "default"}:
            return "%Y%m%d%H%M%S"

        # Validate custom strftime format
        try:
            preview = datetime.now(timezone.utc).strftime(timestamp_fmt)
        except Exception as e:
            msg = (
                f"Invalid timestamp format '{timestamp_fmt}': {e}. "
                "Use 'short', 'long', or a valid strftime pattern like '%Y%m%d%H%M'."
            )
            raise ValueError(msg) from e

        if not preview.isdigit():
            msg = (
                f"Invalid timestamp format '{timestamp_fmt}': "
                "timestamp must consist of digits only. "
                "Use 'short', 'long', or a valid digit-only strftime pattern like '%Y%m%d%H%M'."
            )
            raise ValueError(msg)

        return timestamp_fmt

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

        timestamp = datetime.now(timezone.utc).strftime(self.timestamp_fmt)
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
