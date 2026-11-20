"""Mod class for representing individual mods."""

import zipfile
from enum import IntFlag, auto
from pathlib import Path
from typing import NewType

from constants import DOWNLOADS_DIR

Dependency = NewType("Dependency", "Mod")
TreeSet = NewType("TreeSet", set[Path])


class ModStatus(IntFlag):
    """Set status of mod."""

    NOT_INSTALLED = auto()
    INSTALLED = auto()
    NOT_ONDISK = auto()
    ONDISK = auto()



class Mod:
    """Mod class for Minimal Mod Manager (M3)."""

    def __init__(self, name, version=None):
        """Set mod name, version scoped id and status."""
        self.name: str = name
        self.version: str | None = version
        self.status: ModStatus = (
            ModStatus.ONDISK | ModStatus.NOT_INSTALLED
        )
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
