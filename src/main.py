"""Minimal Mod Manager (M3) app initalization and main function.

description:
    This module contains the main function for the M3 app.
    It initializes the database, creates the QApplication,
    the main window, and the model.
    It then shows the main window and starts the event loop.
"""

import sys

from PyQt6.QtWidgets import QApplication

from controller import M3
from db import db_init
from model import Model
from view import M3Window


def main() -> None:
    """M3's main function."""
    db_init()
    m3_app = QApplication([])
    m3_window = M3Window()
    m3_model = Model()
    m3_window.show()
    _ = M3(m3_model, m3_window)
    sys.exit(m3_app.exec())


if __name__ == "__main__":
    main()
