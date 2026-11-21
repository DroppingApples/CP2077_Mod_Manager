"""The Controller class for Minimal Mod Manager (M3)."""

from PyQt6.QtWidgets import QDialog, QListWidgetItem, QTableWidgetItem

from mod import InstallStatus, Mod
from model import Model, SearchResult
from view import M3Window


class M3:
    """
    Controller class for Minimal Mod Manager.

    Delegates tasks to model and view instances
    and connects signals and slots.
    """

    def __init__(self, model: Model, view: M3Window) -> None:
        """
        Create a M3 controller object.

        Parameters
        ----------
        model : Model
            Model to be used for M3 controller
        view : M3Window
            Windows object to be used as view by the controller.

        """
        self._model: Model = model
        self._view: M3Window = view
        self._search_results: list[SearchResult] = []

        if self._model.game_install_path:
            self._view.download_button.setEnabled(True)
        self._connect_signals_and_slots()
        for mod in self._model.mods:
            self._add_mod_to_table(mod)

    def _add_mod_to_table(self, mod: Mod) -> None:
        """
        Add mod name, version and install status to mod table.

        Parameters
        ----------
        mod : Mod
            The mod object to be represented in table.

        """
        old_row_count = self._view.mod_table.rowCount()
        self._view.mod_table.setRowCount(old_row_count + 1)
        num_rows = self._view.mod_table.rowCount()
        name_item = QTableWidgetItem(mod.name)
        self._view.mod_table.setItem(
            num_rows - 1,
            0,
            name_item,
        )
        self._view.mod_table.setItem(
            num_rows - 1,
            1,
            QTableWidgetItem(mod.version),
        )
        self._view.mod_table.setItem(
            num_rows - 1,
            2,
            QTableWidgetItem(mod.status["install"].value),
        )
        self._view.mod_table.resizeColumnsToContents()

    def _print_log(self, msg: str) -> None:
        """
        Output message to user in log view.

        Parameters
        ----------
        msg : str
            Message string to be printed verbatim.

        """
        self._view.log_view.addItem(msg)

    def _connect_signals_and_slots(self):
        """Call individual methods for creation of signals and slots."""
        self._connect_search_button_to_search_for_mods_handler()
        self._connect_download_button_to_download_mod_handler()
        self._connect_game_folder_button_to_file_dialog()
        self._connect_active_mod_table_row_to_install_action()
        self._connect_active_mod_table_row_to_uninstall_action()

        self._connect_install_button_to_install_mod_handler()
        self._connect_uninstall_button_to_uinstall_mod_handler()

    def _connect_active_mod_table_row_to_install_action(self) -> None:
        self._view.mod_table.cellClicked.connect(
            self._ready_install_candidate,
        )

    def _connect_active_mod_table_row_to_uninstall_action(self) -> None:
        self._view.mod_table.cellClicked.connect(
            self._ready_uninstall_candidate,
        )

    # def _connect_active_mod_table_row_to_remove_action(self) -> None:
    #     self._view.mod_table.cellClicked.connect(
    #         self._ready_remove_candidate,
    #     )

    def _ready_install_candidate(self, row, _) -> None:
        self._selected_row: int = row
        mod_item: QTableWidgetItem | None = self._view.mod_table.item(row, 0)
        if mod_item:
            self._selected_mod = [  # noqa: RUF015
                mod for mod in self._model.mods if mod.name == mod_item.text()
            ][0]

        if self._selected_mod.status["install"] == InstallStatus.INSTALLED:
            self._view.install_action.setEnabled(False)
            (
                self._view.install_action.setText(
                    f"Mod {self._selected_mod.name} already installed",
                ),
            )
            return

        self._view.install_action.setEnabled(True)
        if mod_item:
            self._view.install_action.setText(
                f"install {self._selected_mod.name}",
            )

    def _ready_uninstall_candidate(self, row, _) -> None:
        self._selected_row: int = row
        mod_item: QTableWidgetItem | None = self._view.mod_table.item(row, 0)
        if mod_item:
            self._selected_mod = [  # noqa: RUF015
                mod for mod in self._model.mods if mod.name == mod_item.text()
            ][0]

        if self._selected_mod.status["install"] == InstallStatus.NOT_INSTALLED:
            self._view.uninstall_action.setEnabled(False)
            (
                self._view.uninstall_action.setText(
                    f"Mod {self._selected_mod.name} not installed",
                ),
            )
            return

        self._view.uninstall_action.setEnabled(True)
        if mod_item:
            self._view.uninstall_action.setText(
                f"Uninstall {self._selected_mod.name}",
            )

    def _connect_search_button_to_search_for_mods_handler(self) -> None:
        self._view.search_button.clicked.connect(
            self._search_for_mods_handler,
        )

    def _connect_download_button_to_download_mod_handler(self) -> None:
        self._view.download_button.clicked.connect(
            self._download_mod_handler,
        )

    def _connect_game_folder_button_to_file_dialog(self) -> None:
        self._view.game_folder_button.clicked.connect(
            self._set_game_folder,
        )

    def _connect_install_button_to_install_mod_handler(self) -> None:
        self._view.install_action.triggered.connect(
            self._install_mod_handler,
        )

    def _connect_uninstall_button_to_uinstall_mod_handler(self) -> None:
        self._view.uninstall_action.triggered.connect(
            self._uninstall_mod_handler,
        )

    def _install_mod_handler(self):
        self._view.mod_table.setItem(
            self._selected_row,
            2,
            QTableWidgetItem(InstallStatus.INSTALLED.value),
        )
        if self._model.game_install_path:
            self._model.install_mod(self._selected_mod)
        self._selected_mod.status["install"] = InstallStatus.INSTALLED
        self._model.write_to_mod_list_file()

    def _uninstall_mod_handler(self):
        self._view.mod_table.setItem(
            self._selected_row,
            2,
            QTableWidgetItem(InstallStatus.NOT_INSTALLED.value),
        )
        if self._model.game_install_path:
            self._model.uninstall_mod(self._selected_mod)
        self._selected_mod.status["install"] = InstallStatus.NOT_INSTALLED
        self._model.write_to_mod_list_file()

    def _set_game_folder(self) -> None:
        """Prompt user with file dialog to set game install folder."""
        self._view.create_file_dialog()
        if self._view.file_dialog.exec() == QDialog.DialogCode.Accepted:
            self._model.game_install_path = (
                self._view.file_dialog.selectedFiles()[0]
            )
            # Store new install path string to file
            self._model.store_game_install_path()
            # Enable download button in view
            if not self._view.download_button.isEnabled():
                self._view.download_button.setEnabled(True)
            self._view.log_view.addItem(
                f"Game root folder set to {self._model.game_install_path}",
            )

    def _read_search_line(self) -> str | None:
        """
        Read contents of search line edit widget and return query.

        Returns
        -------
        str:
            The query text to be used for API calls.

        """
        query: str = self._view.search_line.text()
        self._view.search_line.setText("")
        return query

    def _set_search_results_view(self) -> None:
        """Populate search results view and clear old results."""
        self._view.search_results_view.clear()
        if self.search_results:
            for result in self.search_results:
                print(result)
                if result["name"] not in [
                    mod.name for mod in self._model.mods
                ]:
                    self._view.search_results_view.addItem(
                        result["name"],
                    )

    def _search_for_mods_handler(self) -> None:
        """Handle searching for mods."""
        self._print_log(msg="Searching for mods...")
        query: str | None = self._read_search_line()
        if not query:
            self._print_log(
                "No query provided, search aborted",
            )
            return
        self._print_log(
            msg=f'Searching for mods with query "{query}"...',
        )
        self.search_results: list[SearchResult] = self._model.search_mods(
            query,
        )
        if not self.search_results:
            self._print_log(msg="No search results found...")
            return
        self._set_search_results_view()

    def _download_mod_handler(self) -> None:
        """
        Handle for downloading mod files.

        If mod archive exists (File ExistsError),
        abort and write message to user in log view.
        """
        current_item: QListWidgetItem | None = (
            self._view.search_results_view.currentItem()
        )
        if not current_item:
            return
        selected_mod_name: str = current_item.text()
        selected_search_result: SearchResult = next(
            res
            for res in self.search_results
            if res["name"] == selected_mod_name
        )

        try:
            mod: Mod = self._model.download_mod(selected_search_result)
            self._model.mods.append(mod)
            self._add_mod_to_table(mod)
            self._model.write_to_mod_list_file()

        except FileExistsError:
            self._print_log(
                "Download failed, mod files already downloaded!",
            )
