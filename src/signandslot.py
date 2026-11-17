# signals_slots.py

"""Signals and slots example."""

import sys
from functools import partial

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def greet(name):
    if msgLabel.text():
        msgLabel.setText("")
    else:
        msgLabel.setText(f"Hello, {name}!")


app = QApplication([])
window = QWidget()
window.setWindowTitle("Signals and slots")
layout = QVBoxLayout()

button = QPushButton("Greet")

# You can use the following syntax to connect a signal and a slot:
# widget.signal.connect(slot_function)
# This will connect slot_function to widget.signal.
# From now on, whenever .signal is emitted, slot_function() will be called.
button.clicked.connect(partial(greet, "jakob"))
layout.addWidget(button)
msgLabel = QLabel("")
layout.addWidget(msgLabel)
window.setLayout(layout)
window.show()
sys.exit(app.exec())
