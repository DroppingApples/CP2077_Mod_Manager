"""Mod class for representing individual mods."""

from pathlib import Path
from typing import NewType

Dependency = NewType("Dependency", "Mod")
TreeSet = NewType("TreeSet", set[Path])


class Mod:
    def __init__(self, name, scoped_id, version=None):
        self.name: str = name
        self.scoped_id: int = scoped_id
        self.version: str | None = version
        self.dependencies: set[Mod] | None
        self.installed: bool = False
        self.downloaded: bool = True
        self.tree: set[Path] | None = None
        self.overwrites: set[Mod] | None = None
        self.load_order: int = -1

    def install(self) -> None:
        pass

    def uninstall(self) -> None:
        pass

    def set_dependencies(self, deps: Dependency) -> None:
        pass

    def set_load_order(self) -> None:
        pass

    def __repr__(self):
        return f"{self.name}: {self.scoped_id}, {self.version}"
