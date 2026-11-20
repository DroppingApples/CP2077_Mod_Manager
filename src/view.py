"""The View module for Minimal Mod Manager (M3)."""

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QWidget,
)

from constants import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    LINE_EDIT_HEIGHT,
    LINE_EDIT_WIDTH,
    PROGRESS_BAR_HEIGHT,
    PROGRESS_BAR_WIDTH,
)


def get_rgb_from_hex(code):
    """Get rgb Qcolor value from HEX."""
    code_hex = code.replace("#", "")
    rgb = tuple(int(code_hex[i : i + 2], 16) for i in (0, 2, 4))
    return QColor.fromRgb(rgb[0], rgb[1], rgb[2])


class M3Window(QMainWindow):
    """The View class for Minimal Mod Manager."""

    def __init__(self):
        """Initialize the M3Window class.

        This method initializes the M3Window class, sets the window
        title, creates the general layout, and calls the _create_widgets
        method to create the widgets for the window.
        """
        super().__init__()
        self.setWindowTitle("Minimal Mod Manager - Cyberpunk 2077")
        self._central_layout = QGridLayout()
        self.setFixedSize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        central_widget: QWidget = QWidget(self)
        central_widget.setLayout(self._central_layout)
        self._central_layout.setVerticalSpacing(50)
        self.setCentralWidget(central_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._create_widgets()

    def _create_mod_table(self) -> None:
        self.mod_table = QTableWidget()
        self.mod_table.setRowCount(0)
        self.mod_table.setColumnCount(3)
        self.mod_table.setHorizontalHeaderLabels(
            ["Mod Name", "Version", "Status"],
        )
        self._central_layout.addWidget(self.mod_table, 0, 0, 2, 2)

    def _create_log_view(self) -> None:
        self.log_view = QListWidget()
        self._central_layout.addWidget(self.log_view, 0, 2, 2, 2)
        self.log_view.insertItem(0, "Log message 1")
        self.log_view.insertItem(1, "Log message 2")

    def _create_search_results_view(self) -> None:
        self.search_results_view = QListWidget()
        self._central_layout.addWidget(
            self.search_results_view,
            2,
            0,
            1,
            2,
        )
        self.search_results_view.insertItem(0, "Search result 1")
        self.search_results_view.insertItem(1, "Search result 2")

    def _create_search_line(self) -> None:
        self.search_line = QLineEdit()
        self.search_line.setFixedHeight(LINE_EDIT_HEIGHT)
        self.search_line.setFixedWidth(LINE_EDIT_WIDTH)
        self._central_layout.addWidget(self.search_line, 2, 2)

    def _create_search_button(self) -> None:
        self.search_button = QPushButton()
        self.search_button.setText("Search for Mods")
        self.search_button.setFixedHeight(BUTTON_HEIGHT)
        self.search_button.setFixedWidth(BUTTON_WIDTH)
        self._central_layout.addWidget(self.search_button, 2, 3)

    def _create_progress_bar(self) -> None:
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(PROGRESS_BAR_HEIGHT)
        self.progress_bar.setFixedWidth(PROGRESS_BAR_WIDTH)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def _create_download_button(self) -> None:
        self.download_button = QPushButton()
        self.download_button.setText("Download Mod")
        self.download_button.setFixedHeight(BUTTON_HEIGHT)
        self.download_button.setFixedWidth(BUTTON_WIDTH)
        self._central_layout.addWidget(self.download_button, 3, 2)

    def _create_game_folder_button(self) -> None:
        self.game_folder_button = QPushButton()
        self.game_folder_button.setText("Set game folder...")
        self.game_folder_button.setFixedHeight(BUTTON_HEIGHT)
        self.game_folder_button.setFixedWidth(BUTTON_WIDTH)
        self._central_layout.addWidget(self.game_folder_button, 3, 3)

    def create_file_dialog(self) -> None:
        """Create file dialog for selecting game root install folder."""
        self.file_dialog = QFileDialog(
            self,
            "Select Game Root Install folder",
        )
        self.file_dialog.setFileMode(QFileDialog.FileMode.Directory)

    def _create_widgets(self) -> None:
        self._create_mod_table()
        self._create_log_view()
        self._create_search_results_view()
        self._create_search_line()
        self._create_search_button()
        self._create_download_button()
        self._create_progress_bar()
        self._create_game_folder_button()
