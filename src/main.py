import os
import sys

from PyQt6.QtWidgets import QApplication

from model import ModSearchResult, get_mod_file, search_mods
from view import M3Window


def main() -> None:
    """PyCalc's main function."""
    m3_app = QApplication([])
    m3_window = M3Window()
    m3_window.show()
    sys.exit(m3_app.exec())
    # search_results: list[ModSearchResult] = search_mods(
    #     "Immersive Third Person - True First Person Camera - Compatibility Fix",
    #     verbose=False,
    # )

    # mod = get_mod_file(search_results[0])
    # print(mod)


if __name__ == "__main__":
    main()
