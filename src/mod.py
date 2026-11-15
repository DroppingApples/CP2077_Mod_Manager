from math import inf
from pathlib import Path


class Mod:
    ## Attributes
    def __init__(self, name, scoped_id, version):
        self.name: str = name
        self.scoped_id: int = scoped_id
        self.version: str = version
        self.dependencies: list[Mod] | None
        self.installed: bool = False
        self.downloaded: bool = True
        self.tree: list[Path]
        self.overwrites: list[Mod] | None
        self.load_order: int = -1

    ## Methods

    def install(self) -> None:
        pass

    def uninstall(self) -> None:
        pass

    def set_dependencies(self, deps: list["Mod"]) -> None:
        pass

    def __repr__(self):
        return f"{self.name}: {self.scoped_id}, {self.version}"
