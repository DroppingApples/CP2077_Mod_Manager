import os
import sys

from PyQt6.QtWidgets import QApplication

from controller import M3
from model import Model
from view import M3Window


def main() -> None:
    """PyCalc's main function."""
    m3_app = QApplication([])
    m3_window = M3Window()
    m3_model = Model()
    m3_window.show()
    _ = M3(m3_model, m3_window)
    sys.exit(m3_app.exec())

if __name__ == "__main__":
    main()
