"""Mod class for representing individual mods."""

from enum import Enum
from pathlib import Path
from typing import NewType

Dependency = NewType("Dependency", "Mod")
TreeSet = NewType("TreeSet", set[Path])


class InstallStatus(Enum):
    """Set install status of mod."""

    NOT_INSTALLED = "No"
    INSTALLED = "Yes"


class DownloadStatus(Enum):
    """Set download status on mod archive."""

    NOT_ONDISK = "Not on Disk"
    ONDISK = "On Disk"


class Mod:
    """Mod class for Minimal Mod Manager (M3)."""

    def __init__(
        self,
        name,
        version=None,
        install_status: InstallStatus = InstallStatus.NOT_INSTALLED,
        download_status: DownloadStatus = DownloadStatus.ONDISK,
        tree: set[Path] | None = None,
    ):
        """Set mod name, version, scoped id, status and dir tree."""
        self.name: str = name
        self.version: str | None = version
        self.status: dict[str, InstallStatus | DownloadStatus] = {
            "install": install_status,
            "download": download_status,
        }
        self.tree: set[Path] | None = tree

    def __repr__(self):
        return f"{self.name} V{self.version}"

    def __eq__(self, other):
        return isinstance(other, Mod) and self.name == other.name
