"""The View module for Minimal Mod Manager (M3)."""

from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QToolBar,
    QVBoxLayout,
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


def _get_rgb_from_hex(code) -> QColor:
    """
    Get rgb Qcolor value from HEX.

    Parameters
    ----------
    code : str
        Hexadecimal code for a specific color.

    Returns
    -------
    QColor
        Object containing a rgb color value.

    """
    code_hex = code.replace("#", "")
    rgb: tuple[int, ...] = tuple(
        int(code_hex[i : i + 2], 16) for i in (0, 2, 4)
    )
    return QColor.fromRgb(rgb[0], rgb[1], rgb[2])


class M3Window(QMainWindow):
    """The View class for Minimal Mod Manager."""

    def __init__(self):
        """
        Initialize the M3Window class.

        This method initializes the M3Window class, sets the window
        title, creates the general layout, and calls the _create_widgets
        method to create the widgets for the window.
        """
        super().__init__()
        self.setWindowTitle("Minimal Mod Manager - Cyberpunk 2077")
        self.setFixedSize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        self._outer_layout = QVBoxLayout(central_widget)
        self._first_row_layout = QHBoxLayout()
        self._second_row_layout = QHBoxLayout()
        self._outer_search_layout = QVBoxLayout()
        self._search_line_layout = QFormLayout()
        self._outer_search_layout.addLayout(self._search_line_layout)
        self._second_row_layout.addLayout(self._outer_search_layout)
        self._outer_layout.addLayout(self._first_row_layout)
        self._outer_layout.addLayout(self._second_row_layout)

        self._create_widgets()

        self._search_line_layout.addRow(self.search_button, self.search_line)

    def _create_widgets(self) -> None:
        self._create_mod_table()
        self._create_log_view()
        self._create_search_results_view()
        self._create_search_line()
        self._create_search_button()
        self._create_download_button()
        self._create_progress_bar()
        self._create_game_folder_button()
        self._create_tool_bar_buttons()

    def _create_mod_table(self) -> None:
        self.mod_table = QTableWidget()
        self.mod_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers,
        )
        self.mod_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows,
        )
        self.mod_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection,
        )
        self.mod_table.setRowCount(0)
        self.mod_table.setColumnCount(3)
        self.mod_table.setHorizontalHeaderLabels(
            ["Mod Name", "Version", "Installed?"],
        )
        self._first_row_layout.addWidget(self.mod_table, stretch=1)

    def _create_log_view(self) -> None:
        self.log_view = QListWidget()
        self._first_row_layout.addWidget(self.log_view, stretch=2)

    def _create_search_results_view(self) -> None:
        self.search_results_view = QListWidget()
        self._outer_search_layout.addWidget(self.search_results_view)

    def _create_search_line(self) -> None:
        self.search_line = QLineEdit()
        self.search_line.setFixedHeight(LINE_EDIT_HEIGHT)
        self.search_line.setFixedWidth(LINE_EDIT_WIDTH)

    def _create_search_button(self) -> None:
        self.search_button = QPushButton()
        self.search_button.setText("Search for Mods")
        self.search_button.setFixedHeight(BUTTON_HEIGHT)
        self.search_button.setFixedWidth(BUTTON_WIDTH)

    def _create_progress_bar(self) -> None:
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(PROGRESS_BAR_HEIGHT)
        self.progress_bar.setFixedWidth(PROGRESS_BAR_WIDTH)
        self._status_bar.addPermanentWidget(self.progress_bar)

    def _create_download_button(self) -> None:
        self.download_button = QPushButton()
        self.download_button.setEnabled(False)
        self.download_button.setText("Download Mod")
        self.download_button.setFixedHeight(BUTTON_HEIGHT)
        self.download_button.setFixedWidth(BUTTON_WIDTH)
        self._second_row_layout.addWidget(self.download_button)

    def _create_game_folder_button(self) -> None:
        self.game_folder_button = QPushButton()
        self.game_folder_button.setText("Set game folder...")
        self.game_folder_button.setFixedHeight(BUTTON_HEIGHT)
        self.game_folder_button.setFixedWidth(BUTTON_WIDTH)
        self._second_row_layout.addWidget(self.game_folder_button)

    def _create_tool_bar_buttons(self) -> None:
        self.install_action = QAction("Install Selected Mod")
        self.toolbar.addAction(self.install_action)
        self.install_action.setEnabled(False)

        self.uninstall_action = QAction("Uninstall Selected Mod")
        self.toolbar.addAction(self.uninstall_action)
        self.install_action.setEnabled(False)

        self.remove_action = QAction("Remove Selected Mod")
        self.toolbar.addAction(self.uninstall_action)
        self.install_action.setEnabled(False)

    def create_file_dialog(self) -> None:
        """Create file dialog for selecting game root install folder."""
        self.file_dialog = QFileDialog(
            self,
            "Select Game Root Install folder",
        )
        self.file_dialog.setFileMode(QFileDialog.FileMode.Directory)
