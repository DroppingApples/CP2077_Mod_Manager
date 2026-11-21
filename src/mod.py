"""Mod class for representing individual mods."""

import zipfile
from enum import Enum
from pathlib import Path
from typing import NewType

from constants import DOWNLOADS_DIR

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


type ModStatus = dict[str, InstallStatus | DownloadStatus]


class Mod:
    """Mod class for Minimal Mod Manager (M3)."""

    def __init__(
        self,
        name,
        version=None,
        install_status: InstallStatus = InstallStatus.NOT_INSTALLED,
        download_status: DownloadStatus = DownloadStatus.ONDISK,
    ):
        """Set mod name, version, scoped id, status and dir tree."""
        self.name: str = name
        self.version: str | None = version
        self.status: ModStatus = {
            "install": install_status,
            "download": download_status,
        }
        self.tree: set[Path] | None = self.get_mod_tree()

    def get_mod_tree(self) -> None:
        """Read the mod archive and return a set of file paths."""
        mod_path = Path(DOWNLOADS_DIR) / Path(
            f"{self.name} V{self.version}.zip",
        )
        archive = zipfile.ZipFile(mod_path, "r")
        file_list: list[str] = archive.namelist()
        self.tree: TreeSet = TreeSet({Path(file) for file in file_list})

    def install(self) -> None:
        pass

    def uninstall(self) -> None:
        pass

    def set_load_order(self) -> None:
        pass

    def __repr__(self):
        return f"{self.name} V{self.version}"
