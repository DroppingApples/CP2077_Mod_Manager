from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLayout,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from constants import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    DEFAULT_LOG_HEIGHT,
    DEFAULT_MOD_LIST_HEIGHT,
    DEFAULT_SEARCH_HEIGHT,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    LINE_EDIT_HEIGHT,
    LINE_EDIT_WIDTH,
    MINIMUM_WINDOW_HEIGHT,
    MINIMUM_WINDOW_WIDTH,
    PROGRESS_BAR_HEIGHT,
    PROGRESS_BAR_WIDTH,
)


class M3Window(QMainWindow):
    """Mod manager main window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Mod Manager - Cyberpunk 2077")
        self._general_layout: QGridLayout = QGridLayout()

        self._search_and_get_layout = QVBoxLayout()
        self._general_layout.addLayout(self._search_and_get_layout, 1, 1)
        centralWidget: QWidget = QWidget(self)
        centralWidget.setLayout(self._general_layout)
        self.setCentralWidget(centralWidget)

        self._create_mod_list_view()
        self._create_log_view()
        self._create_search_results_view()
        self._create_search_line()
        self._create_search_button()
        self._create_search_button()
        self._create_progress_bar()

        self.status_bar: QStatusBar = self.statusBar()  # ty: ignore[invalid-assignment]
        self.status_bar.addPermanentWidget(self.progress_bar, stretch=1)  # ty: ignore[missing-union-attribute]

    def _create_mod_list_view(self) -> None:
        self.mod_list_view = QListWidget()
        self.mod_list_view.setFixedHeight(DEFAULT_MOD_LIST_HEIGHT)
        self._general_layout.addWidget(self.mod_list_view, 0, 0)
        self.mod_list_view.insertItem(0, "Mod A")
        self.mod_list_view.insertItem(1, "Mod B")

    def _create_log_view(self) -> None:
        self.log_view = QListWidget()
        self.log_view.setFixedHeight(DEFAULT_LOG_HEIGHT)
        self._general_layout.addWidget(self.log_view, 0, 1)
        self.log_view.insertItem(0, "Log message 1")
        self.log_view.insertItem(1, "Log message 2")

    def _create_search_results_view(self) -> None:
        self.search_results_view = QListWidget()
        self.search_results_view.setFixedHeight(DEFAULT_SEARCH_HEIGHT)
        self._general_layout.addWidget(
            self.search_results_view, 1, 0, Qt.AlignmentFlag.AlignTop
        )
        self.search_results_view.insertItem(0, "Search result 1")
        self.search_results_view.insertItem(1, "Search result 2")

    def _create_search_line(self) -> None:
        self.search_line = QLineEdit()
        self.search_line.setFixedHeight(LINE_EDIT_HEIGHT)
        self.search_line.setFixedWidth(LINE_EDIT_WIDTH)
        self._search_and_get_layout.addWidget(
            self.search_line, 0, Qt.AlignmentFlag.AlignLeft
        )

    def _create_search_button(self) -> None:
        self.search_button = QPushButton()
        self.search_button.setText("Search for Mods")
        self.search_button.setFixedHeight(BUTTON_HEIGHT)
        self.search_button.setFixedWidth(BUTTON_WIDTH)
        self._search_and_get_layout.addWidget(
            self.search_button, 0, Qt.AlignmentFlag.AlignTop
        )

    def _create_progress_bar(self) -> None:
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(PROGRESS_BAR_HEIGHT)
        self.progress_bar.setFixedWidth(PROGRESS_BAR_WIDTH)
